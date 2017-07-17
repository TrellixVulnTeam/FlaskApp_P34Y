from app import app,db # import our Flask app
import admin
import models
import views # i will reference to the app which is already in memory

from entries.blueprint import entries
app.register_blueprint(entries, url_prefix='/entries')


if __name__ == '__main__':
    app.run()
