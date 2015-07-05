import os
import urllib
import cgi
import jinja2
import webapp2

from google.appengine.ext import ndb

template_dir = os.path.join(os.path.dirname(__file__),'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape = True)


DEFAULT_WALL = 'Public'


def wall_key(wall_name=DEFAULT_WALL):
  """Constructs a Datastore key for a Wall entity.

  We use wall_name as the key.
  """
  return ndb.Key('Wall', wall_name)

class Post(ndb.Model):
    name = ndb.StringProperty()
    content = ndb.StringProperty()
    date = ndb.DateTimeProperty(auto_now_add=True)

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
    	t = jinja_env.get_template(template)
    	return t.render(params)

    def render(self, template, **kw):
    	self.write(self.render_str(template, **kw))

class SomeHandler(Handler):
    def get(self):
        self.render("stage1.html")

class SomeHandler2(Handler):
    def get(self):
        self.render("stage2.html")

class SomeHandler3(Handler):
    def get(self):
        self.render("stage3.html")

class SomeHandler4(Handler):
    def get(self):
        self.render("stage4.html")

class MainPage(Handler):
    def get(self):
        self.render('main.html')

        wall_name = self.request.get('wall_name',DEFAULT_WALL)
        if wall_name == DEFAULT_WALL.lower(): wall_name = DEFAULT_WALL

        posts_query = Post.query(ancestor = wall_key(wall_name)).order(-Post.date)

        posts = posts_query.fetch()

        template_values = {
            'posts' : posts,
            'wall_name' : urllib.quote_plus(wall_name),
        }

        template = jinja_env.get_template('HTML_TEMPLATE.html')
        self.response.write(template.render(template_values))


class PostWall(Handler):
    def post(self):
        wall_name = self.request.get('wall_name',DEFAULT_WALL)
        post = Post(parent=wall_key(wall_name))

        post.content = self.request.get('content')

        sign_query_params = {'wall_name': wall_name}

        if post.content.isspace():
            self.render("redirect.html")
        else:
            post.put()
            self.redirect('/?' + urllib.urlencode(sign_query_params))





app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/stage1.html', SomeHandler),
    ('/stage2.html', SomeHandler2),
    ('/stage3.html', SomeHandler3),
    ('/stage4.html', SomeHandler4),
    ('/sign', PostWall),
    ], debug=True)