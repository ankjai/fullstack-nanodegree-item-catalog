from flask import Flask, render_template, request, redirect, url_for
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
@app.route('/restaurant')
def list_restaurants():
    restaurants = session.query(Restaurant).all()
    return render_template('home.html', restaurants=restaurants)


@app.route('/restaurant/<int:restaurant_id>/', methods=['GET'])
@app.route('/restaurant/<int:restaurant_id>/menu/', methods=['GET'])
def view_restaurant_menu(restaurant_id):
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    items = session.query(MenuItem).filter_by(restaurant_id=restaurant_id)
    return render_template('restaurant_menu.html', restaurant=restaurant, items=items, restaurant_id=restaurant_id)


@app.route('/restaurant/new/', methods=['GET', 'POST'])
def new_restaurant():
    if request.method == 'POST':
        restaurant = Restaurant(name=request.form['name'])
        session.add(restaurant)
        session.commit()
        return redirect(url_for('list_restaurants'))
    return render_template('restaurant_new.html')


@app.route('/restaurant/<int:restaurant_id>/edit/', methods=['GET'])
def edit_restaurant(restaurant_id):
    return render_template('restaurant_edit.html', stm="edit existing restaurant")


@app.route('/restaurant/<int:restaurant_id>/delete/', methods=['GET', 'DELETE'])
def delete_restaurant(restaurant_id):
    return render_template('restaurant_delete.html', stm="delete existing restaurant")


@app.route('/restaurant/<int:restaurant_id>/menu/new/', methods=['GET', 'POST'])
def new_menu_item(restaurant_id):
    restaurant = None

    if request.method == 'GET':
        restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()

    if request.method == 'POST':
        menu_item = MenuItem(name=request.form['name'],
                             course=request.form['course'],
                             description=request.form['description'],
                             price=request.form['price'],
                             restaurant_id=restaurant_id)
        session.add(menu_item)
        session.commit()
        return redirect(url_for('view_restaurant_menu', restaurant_id=restaurant_id))

    return render_template('menu_new.html', restaurant_id=restaurant_id, restaurant=restaurant)


@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/edit/', methods=['GET', 'POST'])
def edit_menu_item(restaurant_id, menu_id):
    return render_template('menu_edit.html', stm="edit menu item")


@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/delete/', methods=['GET', 'DELETE'])
def delete_menu_item(restaurant_id, menu_id):
    return render_template('menu_delete.html', stm="delete menu item")


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
