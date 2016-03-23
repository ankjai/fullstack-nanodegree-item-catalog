from flask import Flask

app = Flask(__name__)

from catalog import loginviews
from catalog import restaurantviews
from catalog import menuviews
from catalog import apiviews
