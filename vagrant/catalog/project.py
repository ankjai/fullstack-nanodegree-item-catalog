from flask import Flask, render_template
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Base, Restaurant, MenuItem

app = Flask(__name__)

# Create an engine that stores data in the local directory's
# restaurantmenu.db file.
engine = create_engine('sqlite:///restaurantmenu.db')

# Create all tables in the engine. This is equivalent to 'Create Table'
# statement in SQL.
# bind engine obj to our base class
Base.metadata.create_all(engine)

DBSession = sessionmaker(bind=engine)
session = DBSession()


@app.route('/')
@app.route('/restaurants')
def restaurantAll():
    restaurants = session.query(Restaurant).all()
    return render_template('home.html', restaurants=restaurants)


@app.route('/restaurant/<int:restaurant_id>/')
@app.route('/restaurant/<int:restaurant_id>/menu/')
def viewRestaurantMenu(restaurant_id):
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    items = session.query(MenuItem).filter_by(restaurant_id=restaurant_id)
    return render_template('restaurant_menu.html', restaurant=restaurant, items=items)


@app.route('/restaurant/new/')
def newRestaurant():
    return render_template('restaurant_new.html', stm="add new restaurant")


@app.route('/restaurant/<int:restaurant_id>/edit/')
def editRestaurant(restaurant_id):
    return render_template('restaurant_edit.html', stm="edit existing restaurant")


@app.route('/restaurant/<int:restaurant_id>/delete/')
def deleteRestaurant(restaurant_id):
    return render_template('restaurant_delete.html', stm="delete existing restaurant")


@app.route('/restaurant/<int:restaurant_id>/menu/new/')
def newMenuItem(restaurant_id):
    return render_template('menu_new.html', stm="new menu item")


@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/edit/')
def editMenuItem(restaurant_id, menu_id):
    return render_template('menu_edit.html', stm="edit menu item")


@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/delete/')
def deleteMenuItem(restaurant_id, menu_id):
    return render_template('menu_delete.html', stm="delete menu item")


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
