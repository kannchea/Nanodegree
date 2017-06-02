# Copyright 2016 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os

import jinja2
import webapp2
import string
import re
import random
import hashlib

from google.appengine.ext import db

#### Global Variables
USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
PASSWORD_RE = re.compile(r"^.{3,20}$")
EMAIL_RE = re.compile(r"^[\S]+@[\S]+.[\S]+$")

#### Global Method
##### User's Info Validation
def render_str(template, **params):
    t = jinja_env.get_template(template)
    return t.render(params)
def valid_username(username):
    return USER_RE.match(username)
    
def valid_password(password):
    return PASSWORD_RE.match(password)
    
def valid_email(email):
    return EMAIL_RE.match(email)

##### Hash Password
def make_salt():
    return ''.join(random.choice(string.lowercase) for i in range (5))

def make_pw_hash(name, pw):
    salt = make_salt()
    h = hashlib.sha256(name + pw + salt).hexdigest()
    return '%s,%s' % (h, salt)

##### Validate Password
def valid_pw(name, pw, h):
    salt = h.split(",")[1]
    hash_pw = hashlib.sha256(name + pw + salt).hexdigest()
    return hash_pw == h.split(',')[0]

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape = True)

#### User Instance
class User(db.Model):
    name = db.StringProperty(required = True)
    pw_hash = db.StringProperty(required = True)
    email = db.StringProperty()

#### Post Instance
class Post(db.Model):
    subject = db.StringProperty(required = True)
    content = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)
    created_by = db.StringProperty(required = True)
    comment = db.IntegerProperty(default = 0)
    like = db.IntegerProperty(default = 0)
    

#### Comment Instace
class Comment(db.Model):
    comment = db.StringProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)
    post_id = db.StringProperty(required = True)
    commented_by = db.StringProperty(required = True)


#### Post Like
class PostLiked(db.Model):
    user = db.ReferenceProperty(User, collection_name = 'post_liked')
    liked = db.StringProperty()
    disliked = db.StringProperty()


#### Base class Handler
class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)
        
    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)
    
    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

#### Front Page 
class FrontPage(Handler):
    def get(self):
        username = self.request.cookies.get('name')
        posts = db.GqlQuery("select * from Post order by created DESC limit 10")
        self.render("front_page.html", posts=posts, username=username)
    def post(self):
        self.redirect('/login')
            

#### Welcome
class Welcome(Handler):
    def get(self):
        username = self.request.cookies.get('name')
        posts = db.GqlQuery("select * from Post order by created DESC limit 10")
        self.render("welcome.html", posts=posts, username=username)
    def post(self):
        username = self.request.cookies.get('name')
        
        if username:
            error = ''
            action = self.request.get('action')
            post_id = action.split(',')[0]
            action = action.split(',')[1]
            key = db.Key.from_path('Post', int(post_id))
            post = db.get(key)
            
            if action == 'delete':
                if post.created_by == username:
                    post.delete()
                    db.get(key)                    
                else:
                    error = "You can only delete your post."

            elif action == 'edit':
                if post.created_by == username:
                    self.redirect('/edit?post_id=%s' % post_id)
                else:
                    error = "You can only edit your post"

            ##### Like or Dislike
            else:
            	checker = True
            	if username == post.created_by:
            		error = "You can't like/dislike your own post."
            		checker = False

            	if checker:
	            	user = User.all().filter('name =', username).get()

	            	liked = user.post_liked.filter('liked =', post_id).get()
	            	disliked = user.post_liked.filter('disliked =', post_id).get()

        		if action == 'like':
        			if disliked:
        				PostLiked(user=user, liked=post_id).put()
        				user.post_liked.filter('disliked =', post_id).get().delete()
        				post.like += 1
        				post.put()
        				db.get(key)
        			elif liked:
        				error = "You've already liked this post."
        			else:
        				PostLiked(user=user, liked=post_id).put()
        				post.like += 1
        				post.put()
        				db.get(key)
        		else:
        			if liked:
        				PostLiked(user=user, disliked=post_id).put()
        				user.post_liked.filter('liked =', post_id).get().delete()
        				post.like -= 1
        				post.put()
        				db.get(key)
        			elif disliked:
        				error = "You've already disliked this post."
        			else:
        				PostLiked(user=user, disliked=post_id).put()
        				post.like -= 1
        				post.put()
        				db.get(key)

            posts = db.GqlQuery("select * from Post order by created DESC limit 10")        
            self.render("welcome.html", posts=posts, username=username, error=error, like=post.like)
        
        else:
            self.redirect('/login')
        
#### Profile Page
class Profile(Handler):
    def get(self):
        username = self.request.cookies.get('name')
        posts = Post.all().filter('created_by =', username)
        self.render("profile.html", posts=posts, username=username)
        
#### Add new post
class NewPost(Handler):
    def get (self):
        username = self.request.cookies.get('name')
        self.render("newpost.html", username=username)
        
    def post (self):
        username = self.request.cookies.get('name')
        subject = self.request.get('subject')
        content = self.request.get('content')
        
        if subject and content:
            p = Post(subject=subject, content=content, created_by = username, like = 0, dislike = 0)
            p.put()
            self.redirect("/%s" % str(p.key().id()))
        else:
            error = "subject and content please!"
            self.render("newpost.html", subject=subject, content=content, error=error, username=username)
            

#### Edit post
class Edit(Handler):
    def get (self):
        username = self.request.cookies.get('name')
        post_id = self.request.get('post_id')
        key = db.Key.from_path('Post', int(post_id))
        post = db.get(key)

        print post.subject
        self.render("edit.html", subject=post.subject, content=post.content, username=username)
        
    def post (self):
        username = self.request.cookies.get('name')
        subject = self.request.get('subject')
        content = self.request.get('content')
        
        post_id = self.request.get('post_id')
        key = db.Key.from_path('Post', int(post_id))
        post = db.get(key)
        
        if subject and content:
            post.subject = subject
            post.content = content
            post.put()
            
            self.redirect("/%s" % str(post.key().id()))
        else:
            error = "subject and content please!"
            self.render("newpost.html", subject=subject, content=content, error=error, username=username)
            
#### Handle post after user add new post
class PostHandler(Handler):
    def get(self, post_id):
        key = db.Key.from_path('Post', int(post_id))
        post = db.get(key)
        
        if not post:
            self.error(404)
            return
        
        username = self.request.cookies.get('name')
        comments = Comment.all().filter('post_id =', post_id).order('-created')

        self.render("post.html", comments = comments, post=post, post_id=post_id, username=username)
    
    def post(self, post_id):
        post_key = db.Key.from_path('Post', int(post_id))        
        post = db.get(post_key)
        
        if not post:
            self.error(404)
            return
        
        username = self.request.cookies.get('name')

        if username:
            comment = self.request.get('comment')
            error = ''
            action = self.request.get('action')
            
            if comment:
                c = Comment(comment = comment, post_id = post_id, commented_by = username)
                c.put()
                c_id = c.key().id()
                c_key = db.Key.from_path('Comment', int(c_id))  
                # print(c_id)
                # print(type(c_id))
                db.get(c_key)

                post.comment += 1
                post.put()
                db.get(post_key)

            if action:
                comment_id = action.split(',')[0]
                action = action.split(',')[1]
                c_key = db.Key.from_path('Comment', int(comment_id))
                comment = db.get(c_key)

                if comment.commented_by == username:
                    comment.delete()
                    db.get(c_key)                   
                    post.comment -= 1
                    if(post.comment < 0):
                        post.comment = 0
                    post.put() 
                    db.get(post_key)                   
                else:
                    error = "You can only delete your own comment."
            
            comments = Comment.all().filter('post_id =', post_id).order('-created')

            self.render("post.html", comments = comments, post=post, post_id=post_id, username=username, error=error)

        else:
            self.redirect('/login')
        
#### Sign Up
class SignUp(Handler):
    def get(self):
        self.render('signup.html')
    
    def post(self):
        user_name = self.request.get('username')
        pass_word = self.request.get('password')
        email_    = self.request.get('email')
        
        username = valid_username(user_name)
        password = valid_password(pass_word)
        verify = self.request.get('verify')
        email = valid_email(email_)
        
        username_err = ""
        password_err = ""
        verify_err   = ""
        email_err    = ""
        
        checker = False
        
        if not (username):
            username_err = "That's not a valid username."
            checker = True 
        if username:
            u = User.all().filter('name =', user_name).get()
            if u:
                username_err = "That user already exists."
                return self.render("signup.html", username=user_name, username_err=username_err, password_err = password_err, verify_err=verify_err, email_err=email_err, email=email_)
        if not (password):
            password_err = "That wasn't a valid password."
            checker = True
        if (password):
            if not verify or (verify != pass_word):
                verify_err   = "Your passwords didn't match."
                checker = True
        if (email_):
            if not (email): 
                email_err    = "That's not a valid email."
                checker = True
        
        if checker:
            self.render("signup.html", username=user_name, username_err=username_err, password_err = password_err, verify_err=verify_err, email_err=email_err, email=email_)
            
        else:
            password=make_pw_hash(user_name, pass_word)
            
            u = User(name=user_name, pw_hash=password, email=email_)
            u.put()
            
            cookie_val = "name=" + user_name + "; password=" + password + "; Path=/"
            cookie_val = cookie_val.encode('utf8')
            self.response.headers.add_header('Set-Cookie', cookie_val)
            self.redirect("/welcome")
        
        
##### Welcome page
#class Welcome(Handler):
#    def get(self):
#        username = self.request.cookies.get('name')
#        self.render("welcome.html", username=username)
        
#### Login
class Login(Handler):
    def get(self):
        self.render("login.html")
    def post(self):
        
        user_name = self.request.get('username')
        pass_word = self.request.get('password')
        
        username = valid_username(user_name)
        password = valid_password(pass_word)
        
        checker = False
        error = ''
        
        if not (username):
            error = "Invalid login."
            checker = True 
        if not (password):
            error = "Invalid login."
            checker = True
        if password and username:
            u = User.all().filter('name =', user_name).get()
            if u:
                valid = valid_pw(user_name, pass_word, u.pw_hash)
                if not valid:
                    error = "Invalid login."
                    checker = True
            else:
                error = "Invalid login."
                checker = True
        if checker:
            self.render("login.html", username=user_name, error = error)
        else:
            password=make_pw_hash(user_name, pass_word)
            cookie_val = "name=" + user_name + "; password=" + password + "; Path=/"
            cookie_val = cookie_val.encode('utf8')
            self.response.headers.add_header('Set-Cookie', cookie_val)
            self.redirect("/welcome")

#### Logout
class Logout(Handler):
    def get(self):
        self.response.headers.add_header('Set-Cookie', "name=; password=; Path=/")
        self.redirect('/signup')
        
app = webapp2.WSGIApplication([
    ('/', FrontPage),
    ('/welcome', Welcome),
    ('/profile', Profile),
    ('/newpost', NewPost),
    ('/edit', Edit),
    ('/([0-9]+)', PostHandler),
    ('/signup', SignUp),
    ('/login', Login),
    ('/logout', Logout),
], debug=True)
