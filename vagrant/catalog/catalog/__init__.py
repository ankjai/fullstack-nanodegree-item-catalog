from flask import Flask

app = Flask(__name__)

# import all routes
import loginviews
import restaurantviews
import menuviews
import apiviews

if __name__ == '__main__':
    app.secret_key = 'super_secret_key_1'
    app.debug = True
    app.run()
