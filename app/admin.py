from flask_admin import Admin,AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView
from flask_admin.contrib.fileadmin import FileAdmin
from app import app,db
from models import Entry, Tag, User, entry_tags
from wtforms.fields import SelectField, PasswordField  # At top of module.
from flask import g, url_for
from flask import redirect

class AdminAuthentication(object):
    def is_accessible(self):
        return g.user.is_authenticated and g.user.is_admin()

class BlogFileAdmin(AdminAuthentication,FileAdmin):
    pass

##### The following function customizes the Admin page view that was given by default by FLASK.
##### Initialement : BaseModelView(AdminAuthentication,ModelView)
class BaseModelView(AdminAuthentication,ModelView): #AdminAuthentication needed for giving access to only required fields.
    pass

class SlugModelView(BaseModelView):
    def on_model_change(self, form, model, is_created):
        model.generate_slug()
        return super(SlugModelView, self).on_model_change(
            form, model, is_created)


#class EntryModelView(ModelView): #this extends basic ModelView
class EntryModelView(SlugModelView): #his extends SlugModelView
#####  VIEW display
    _status_choices = [(choice, label) for choice, label in [
        (Entry.STATUS_PUBLIC, 'Public'),
        (Entry.STATUS_DRAFT, 'Draft'),
        (Entry.STATUS_DELETED, 'Deleted'),
    ]]

    column_choices = {
        'status': _status_choices,
    }
    column_filters = [
        'status', User.name, User.email, 'created_timestamp'
    ]
    column_list = [
        'title', 'status', 'author', 'tease', 'tag_list', 'created_timestamp',
    ]
    column_searchable_list = ['title', 'body'] # to be able to search inside these columns
    column_select_related_list = ['author']

##### FORM display
    form_args = {
        'status': {'choices': _status_choices, 'coerce': int},
    }
    form_columns = ['title', 'body', 'status', 'author', 'tags','slug']
    form_overrides = {'status': SelectField}
    form_ajax_refs = { #allows to search on only two fields to optimize the retrieval time
    'author': {
        'fields': (User.name, User.email),
    },
}

class UserModelView(ModelView):
###### VIEW
    column_filters = [
         'email', 'created_timestamp','name', 'active', 'admin'
     ]
    column_list = ['email', 'name', 'active', 'admin', 'created_timestamp']
    column_searchable_list = ['name','email'] # to be able to search inside these columns
#####   FORM
    form_columns = ['entries','email', 'password', 'name', 'active', 'admin']
    form_extra_fields = {
        'password': PasswordField('New password'),
    }
    def on_model_change(self, form, model, is_created):
        if form.password.data:
            model.password_hash = User.make_password(form.password.data)
        return super(UserModelView, self).on_model_change(
            form, model, is_created)

# this function is created last, in order to give special access views
class IndexView(AdminIndexView):
    @expose('/')
    def index(self):
        if not (g.user.is_authenticated and g.user.is_admin()):
            return redirect(url_for('login', next=request.path))
        return self.render('admin/index.html')

admin = Admin(app, 'Blog Admin', index_view=IndexView())
#admin.add_view(ModelView(Entry, db.session))#the default model view;
admin.add_view(EntryModelView(Entry, db.session))
admin.add_view(SlugModelView(Tag, db.session))
admin.add_view(UserModelView(User, db.session))
admin.add_view(BlogFileAdmin(app.config['STATIC_DIR'], '/static/', name='Static Files'))
