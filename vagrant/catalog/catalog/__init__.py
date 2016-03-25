from flask import Flask

app = Flask(__name__)

# import all routes
from catalog import loginviews
from catalog import restaurantviews
from catalog import menuviews
from catalog import apiviews
