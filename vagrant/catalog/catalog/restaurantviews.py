from . import app
from flask import render_template, request, redirect, url_for, flash
from flask import session as login_session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Base, Restaurant

# Create an engine that stores data in the local directory's
# restaurantapp.db file.
engine = create_engine('sqlite:///restaurantapp.db', connect_args={'check_same_thread': False})

# Create all tables in the engine. This is equivalent to 'Create Table'
# statement in SQL.
# bind engine obj to our base class
Base.metadata.create_all(engine)

DBSession = sessionmaker(bind=engine)
session = DBSession()


@app.route('/')
@app.route('/restaurant')
def list_restaurants():
    """ retrieve restaurant list and renders it in home.html page """
    restaurants = session.query(Restaurant).all()
    return render_template('home.html', restaurants=restaurants)


@app.route('/restaurant/new/', methods=['GET', 'POST'])
def new_restaurant():
    """ create new restaurant """
    # if user is logged out, redirect to login page
    if login_session.get('username') is None:
        return redirect('/login')

    # on POST create a new restaurant in db
    # else render new restaurant creation form
    if request.method == 'POST':
        restaurant = Restaurant(name=request.form['name'], user_id=login_session['user_id'])
        session.add(restaurant)
        session.commit()
        flash("New restaurant created.", category='success')
        return redirect(url_for('list_restaurants'))
    else:
        return render_template('restaurant_new.html')


@app.route('/restaurant/<int:restaurant_id>/edit/', methods=['GET', 'POST'])
def edit_restaurant(restaurant_id):
    """ edit existing restaurant """
    # if user is logged out, redirect to login page
    if login_session.get('username') is None:
        return redirect('/login')

    edited_restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()

    # on POST update existing restaurant info in db
    # else render edit restaurant form
    if request.method == 'POST':
        if request.form['name']:
            edited_restaurant.name = request.form['name']
        session.add(edited_restaurant)
        session.commit()
        flash("Updated restaurant info.", category='success')
        return redirect(url_for('list_restaurants'))
    else:
        return render_template('restaurant_edit.html', restaurant=edited_restaurant)


@app.route('/restaurant/<int:restaurant_id>/delete/', methods=['GET', 'POST'])
def delete_restaurant(restaurant_id):
    """ delete existing restaurant """
    # if user is logged out, redirect to login page
    if login_session.get('username') is None:
        return redirect('/login')

    restaurant_to_delete = session.query(Restaurant).filter_by(id=restaurant_id).one()

    # on POST delete the existing restaurant from db
    # else render the delete restaurant page
    if request.method == 'POST':
        session.delete(restaurant_to_delete)
        session.commit()
        flash("Restaurant deleted.", category='success')
        return redirect(url_for('list_restaurants'))
    else:
        return render_template('restaurant_delete.html', restaurant=restaurant_to_delete)
