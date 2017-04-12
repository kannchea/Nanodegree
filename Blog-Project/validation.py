
import string
import re
import random
import hashlib

from model import *


def render_str(template, **params):
    t = jinja_env.get_template(template)
    return t.render(params)


def valid_username(username):
    USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
    return USER_RE.match(username)


def valid_password(password):
    PASSWORD_RE = re.compile(r"^.{3,20}$")
    return PASSWORD_RE.match(password)


def valid_email(email):
    EMAIL_RE = re.compile(r"^[\S]+@[\S]+.[\S]+$")
    return EMAIL_RE.match(email)


# Hash Password

def make_salt():
    return ''.join(random.choice(string.lowercase) for i in range(5))


def make_pw_hash(name, pw):
    salt = make_salt()
    h = hashlib.sha256(name + pw + salt).hexdigest()
    return '%s,%s' % (h, salt)


# Validate Password
def valid_pw(name, pw, h):
    salt = h.split(",")[1]
    hash_pw = hashlib.sha256(name + pw + salt).hexdigest()
    return hash_pw == h.split(',')[0]


# Hash Cookie

def hash_str(s):
    return hashlib.md5(s).hexdigest()


def make_secure_val(s):
    HASH = hash_str(s)
    return '%s|%s' % (s, HASH)


# Validate Cookie
def valid_val(h):
    s = h.split("|")
    user = User.all().filter('name =', s[0]).get()

    if hash_str(s[0]) == s[1]:
        if s[0] == user.name:
            return s[0]
