from catalog import app

# starting point of the app
app.secret_key = 'super_secret_key_1'
app.debug = True
app.run(host='0.0.0.0', port=8000)
