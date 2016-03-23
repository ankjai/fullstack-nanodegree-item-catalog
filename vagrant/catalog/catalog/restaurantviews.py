from flask import render_template
from catalog import app
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Base, Restaurant

# Create an engine that stores data in the local directory's
# restaurantmenu.db file.
engine = create_engine('sqlite:////vagrant/catalog/catalog/restaurantapp.db')

# Create all tables in the engine. This is equivalent to 'Create Table'
# statement in SQL.
# bind engine obj to our base class
Base.metadata.create_all(engine)

DBSession = sessionmaker(bind=engine)
session = DBSession()


@app.route('/')
@app.route('/restaurant')
def list_restaurants():
    restaurants = session.query(Restaurant).all()
    return render_template('home.html', restaurants=restaurants)
