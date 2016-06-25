from . import app
from flask import render_template, request, redirect, url_for, flash
from flask import session as login_session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Base, Restaurant, MenuItem

# Create an engine that stores data in the local directory's
# restaurantapp.db file.
engine = create_engine('sqlite:///restaurantapp.db', connect_args={'check_same_thread': False})

# Create all tables in the engine. This is equivalent to 'Create Table'
# statement in SQL.
# bind engine obj to our base class
Base.metadata.create_all(engine)

DBSession = sessionmaker(bind=engine)
session = DBSession()


@app.route('/restaurant/<int:restaurant_id>/', methods=['GET'])
@app.route('/restaurant/<int:restaurant_id>/menu/', methods=['GET'])
def view_restaurant_menu(restaurant_id):
    """ retrieve restaurant's menu list and renders on page """
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    items = session.query(MenuItem).filter_by(restaurant_id=restaurant_id).all()
    return render_template('restaurant_menu.html', restaurant=restaurant, items=items, restaurant_id=restaurant_id)


@app.route('/restaurant/<int:restaurant_id>/menu/new/', methods=['GET', 'POST'])
def new_menu_item(restaurant_id):
    """ create new menu item in that restaurant """
    # if user is logged out, redirect to login page
    if login_session.get('username') is None:
        return redirect('/login')

    # on POST, create a new menu item for specific restaurant_id and user_id
    if request.method == 'POST':
        menu_item = MenuItem(name=request.form['name'],
                             course=request.form['course'],
                             description=request.form['description'],
                             price="$" + request.form['price'],
                             restaurant_id=restaurant_id,
                             user_id=login_session['user_id'])
        session.add(menu_item)
        session.commit()
        flash("New menu item created.", category='success')
        return redirect(url_for('view_restaurant_menu', restaurant_id=restaurant_id))
    else:
        restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
        # allow only owner of the restaurant to add menu items
        if login_session['user_id'] != restaurant.user_id:
            flash('You are not the owner of this restaurant.', category='warning')
            flash('You do not have authorization to add menu item.', category='error')
            return redirect(url_for('view_restaurant_menu', restaurant_id=restaurant_id))
        else:
            return render_template('menu_new.html', restaurant_id=restaurant_id, restaurant=restaurant)


@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/edit/', methods=['GET', 'POST'])
def edit_menu_item(restaurant_id, menu_id):
    """ update existing menu item """
    # if user is logged out, redirect to login page
    if login_session.get('username') is None:
        return redirect('/login')

    edited_item = session.query(MenuItem).filter_by(id=menu_id).one()
    edited_item_price = edited_item.price[1:]

    # on POST, update the existing menu item
    if request.method == 'POST':
        if request.form['name']:
            edited_item.name = request.form['name']
        if request.form['course']:
            edited_item.course = request.form['course']
        if request.form['description']:
            edited_item.description = request.form['description']
        if request.form['price']:
            edited_item.price = "$" + request.form['price']
        session.add(edited_item)
        session.commit()
        flash("Menu item updated.", category='success')
        return redirect(url_for('view_restaurant_menu', restaurant_id=restaurant_id))
    else:
        return render_template('menu_edit.html', restaurant_id=restaurant_id, menu_id=menu_id, item=edited_item,
                               item_price=edited_item_price)


@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/delete/', methods=['GET', 'POST'])
def delete_menu_item(restaurant_id, menu_id):
    """ delete existing menu item """
    # if user is logged out, redirect to login page
    if login_session.get('username') is None:
        return redirect('/login')

    item_to_delete = session.query(MenuItem).filter_by(id=menu_id).one()

    # on POST, delete the existing menu item
    if request.method == 'POST':
        session.delete(item_to_delete)
        session.commit()
        flash("Menu item deleted.", category='success')
        return redirect(url_for('view_restaurant_menu', restaurant_id=restaurant_id))
    else:
        return render_template('menu_delete.html', restaurant_id=restaurant_id, menu_id=menu_id, item=item_to_delete)
