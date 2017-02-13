#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
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
#
import webapp2
import jinja2
import os
from google.appengine.ext import db


template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir),
                               autoescape=True)


class Blog(db.Model):
    title   = db.StringProperty(required=True)
    body    = db.TextProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)

    
class Handler(webapp2.RequestHandler):

    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)
        
    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)
    
    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

        
class MainHandler(Handler):
    def get(self):
        self.redirect('/blog')
        
        
class BlogPage(Handler):
    def render_blogpage(self, blogs=""):
        blogs = db.GqlQuery("SELECT * FROM Blog ORDER BY created DESC LIMIT 5")
        self.render("blogpage.html", blogs= blogs)
    
    def get(self):
        self.render_blogpage()
        

class NewPost(Handler):
    def render_newpost(self, 
                         title="", 
                         body ="", 
                         error=""):
                         
        self.render("newpost.html", 
                    title= title, 
                    body = body, 
                    error= error)
    
    def get(self):
        self.render_newpost()
        
    def post(self):
        title = self.request.get("title")
        body  = self.request.get("body")
        
        if title and body:
            b = Blog(title=title, body=body)
            b.put()
            
            self.redirect("/")
            
        else:
            error = "we need both a title and content."
            self.render_frontpage(title, body, error, blogs)

            
app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/blog', BlogPage),
    ('/newpost', NewPost),
], debug=True)
