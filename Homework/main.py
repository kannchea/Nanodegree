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

from google.appengine.ext import db

USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
PASSWORD_RE = re.compile(r"^.{3,20}$")
EMAIL_RE = re.compile(r"^[\S]+@[\S]+.[\S]+$")

def render_str(template, **params):
    t = jinja_env.get_template(template)
    return t.render(params)
def valid_username(username):
    return USER_RE.match(username)
    
def valid_password(password):
    return PASSWORD_RE.match(password)
    
def valid_email(email):
    return EMAIL_RE.match(email)

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape = True)

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)
        
    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)
    
    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class MainPage(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.write('Hello! Welcome to my Nanodegree projects')
        
        
class Rot13(Handler):
    def get(self):
        self.render("rot13.html")
        
    def post(self):
        
        text = self.request.get("text")
        rot13 = string.maketrans("ABCDEFGHIJKLMabcdefghijklmNOPQRSTUVWXYZnopqrstuvwxyz","NOPQRSTUVWXYZnopqrstuvwxyzABCDEFGHIJKLMabcdefghijklm")
        
        text = text.encode('utf8')
        text = string.translate(text, rot13)
        self.render("rot13.html", text=text)

        
class Signup(Handler):
    def get(self):
        self.render("signup.html")
    
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
            self.redirect("/welcome?username=" + user_name)
            
class Welcome(Handler):
    def get(self):
        self.render("welcome.html", username=self.request.get('username'))

        
class Blog(Handler):
    def get (self):
        posts = db.GqlQuery("select * from Post order by created DESC")
        self.render("blog.html", posts=posts)
        
class NewPost(Handler):
    def get (self):
        self.render("newpost.html")
        
    def post (self):
        subject = self.request.get('subject')
        content = self.request.get('content')
        
        if subject and content:
            p = Post(subject=subject, content=content)
            p.put()
            self.redirect("/blog/%s" % str(p.key().id()))
        else:
            error = "subject and content please!"
            self.render("newpost.html", subject=subject, content=content, error=error)
            
class PostHandler(Handler):
    def get(self, post_id):
        key = db.Key.from_path('Post', int(post_id))
        post = db.get(key)
        
        if not post:
            self.error(404)
            return
        
        self.render("post.html", post = post)
            
class Post(db.Model):
    subject = db.StringProperty(required = True)
    content = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)
    
    def render(self):
        return render_str("post.html", post = self)
        
        
app = webapp2.WSGIApplication([
    ('/', MainPage), 
    ('/rot13', Rot13), 
    ('/signup', Signup), 
    ('/welcome', Welcome),
    ('/blog/?', Blog),
    ('/blog/newpost', NewPost),
    ('/blog/([0-9]+)', PostHandler)
], debug=True)
