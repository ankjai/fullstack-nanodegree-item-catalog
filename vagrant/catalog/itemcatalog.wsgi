from catalog import app

# set app propertied
app.secret_key = 'super_secret_key_1'
app.debug = True

# application object for mod_wsgi
application = app
