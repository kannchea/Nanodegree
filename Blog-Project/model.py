from google.appengine.ext import db

# User Instance

class User(db.Model):
    ''' a user object that will be stored in the database '''
    name = db.StringProperty(required=True)
    pw_hash = db.StringProperty(required=True)
    email = db.StringProperty()


# Post Instance

class Post(db.Model):
    ''' a post object that will be stored in the database '''
    subject = db.StringProperty(required=True)
    content = db.TextProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)
    created_by = db.StringProperty(required=True)
    comment = db.IntegerProperty(default=0)
    like = db.IntegerProperty(default=0)


# Comment Instace

class Comment(db.Model):
    ''' a comment object that will be stored in the database '''
    comment = db.StringProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)
    post_id = db.StringProperty(required=True)
    commented_by = db.StringProperty(required=True)


# Post Like

class PostLiked(db.Model):
    ''' an object for each post that is liked or disliked and will be
    stored in the database '''
    user = db.ReferenceProperty(User, collection_name='post_liked')
    liked = db.StringProperty()
    disliked = db.StringProperty()
