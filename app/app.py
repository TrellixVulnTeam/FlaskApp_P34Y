from flask import Flask,flash,g, request,session
from config import Configuration
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager #allows to execute commands from the command line
from flask_login import LoginManager, current_user
from flask_bcrypt import Bcrypt


app = Flask(__name__)
app.config.from_object(Configuration)

#this part needed to ommit ALTER constraint_error
convention = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

metadata = MetaData(naming_convention=convention)

db = SQLAlchemy(app,metadata=metadata)

#migrate needed in order to be able to modify existing models
migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('db', MigrateCommand)

#LOGINMANAGER for user Sessions
login_manager = LoginManager(app)
login_manager.login_view = "login"

bcrypt = Bcrypt(app)

@app.before_request
def _before_request():
    g.user = current_user

@app.before_request
def _last_page_visited():
    if "current_page" in session:
        session["last_page"] = session["current_page"]
    session["current_page"] = request.path
# from flask import Flask #represents a single WSGI application. WSGI is the Python standard web server interface
# from flask import abort, request
# @app.route('/hello/<name>')
# @app.route('/hello/')
# def hello(name=None):
#     if name is None:
#         # If no name is specified in the URL, attempt to retrieve it
#         # from the query string.
#         name = request.args.get('name')   #   /hello?name=Russlan
#         if name:
#             return 'Hello, %s' % name
#         else:
#             # No name was specified in the URL or the query string.
#             abort(404)
#     else:  #/hello/Russlan
#         return 'Hello, %s' % name
