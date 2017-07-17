from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from app import app,db
from models import Entry, Tag, User, entry_tags
from wtforms.fields import SelectField, PasswordField  # At top of module.
from flask_admin.contrib.fileadmin import FileAdmin

class BlogFileAdmin(FileAdmin):
    pass

##### The following function customizes the Admin page view that was given by default by FLASK.
class BaseModelView(ModelView):
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
         'email', 'created_timestamp','name', 'active'
     ]
    column_list = ['email', 'name', 'active', 'created_timestamp']
    column_searchable_list = ['name','email'] # to be able to search inside these columns
#####   FORM
    form_columns = ['email', 'password', 'name', 'active']
    form_extra_fields = {
        'password': PasswordField('New password'),
    }
    def on_model_change(self, form, model, is_created):
        if form.password.data:
            model.password_hash = User.make_password(form.password.data)
        return super(UserModelView, self).on_model_change(
            form, model, is_created)

admin=Admin(app,'Blog Admin')
#admin.add_view(ModelView(Entry, db.session))#the default model view;
admin.add_view(EntryModelView(Entry, db.session))
admin.add_view(SlugModelView(Tag, db.session))
admin.add_view(UserModelView(User, db.session))
admin.add_view(BlogFileAdmin(app.config['STATIC_DIR'], '/static/', name='Static Files'))
