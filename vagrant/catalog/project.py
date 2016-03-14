import json
import random
import string

import httplib2
import requests
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask import make_response
from flask import session as login_session
from oauth2client.client import FlowExchangeError
from oauth2client.client import flow_from_clientsecrets
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Base, Restaurant, MenuItem

app = Flask(__name__)

CLIENT_ID = json.loads(open('client_secrets.json', 'r').read())['web']['client_id']

# Create an engine that stores data in the local directory's
# restaurantmenu.db file.
engine = create_engine('sqlite:///restaurantmenu.db')

# Create all tables in the engine. This is equivalent to 'Create Table'
# statement in SQL.
# bind engine obj to our base class
Base.metadata.create_all(engine)

DBSession = sessionmaker(bind=engine)
session = DBSession()


@app.route('/login')
def show_login():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))
    login_session['state'] = state
    print "state:", state
    return render_template('login.html', state=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    print "in gconnect()"
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['credentials'] = credentials
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output


@app.route('/')
@app.route('/restaurant')
def list_restaurants():
    restaurants = session.query(Restaurant).all()
    return render_template('home.html', restaurants=restaurants)


@app.route('/restaurant/<int:restaurant_id>/', methods=['GET'])
@app.route('/restaurant/<int:restaurant_id>/menu/', methods=['GET'])
def view_restaurant_menu(restaurant_id):
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    items = session.query(MenuItem).filter_by(restaurant_id=restaurant_id).all()
    return render_template('restaurant_menu.html', restaurant=restaurant, items=items, restaurant_id=restaurant_id)


@app.route('/restaurant/<int:restaurant_id>/menu/JSON')
def view_restaurant_menu_json(restaurant_id):
    items = session.query(MenuItem).filter_by(restaurant_id=restaurant_id).all()
    return jsonify(MenuItem=[i.serialize for i in items])


@app.route('/restaurant/new/', methods=['GET', 'POST'])
def new_restaurant():
    if request.method == 'POST':
        restaurant = Restaurant(name=request.form['name'])
        session.add(restaurant)
        session.commit()
        flash("New restaurant created.")
        return redirect(url_for('list_restaurants'))
    else:
        return render_template('restaurant_new.html')


@app.route('/restaurant/<int:restaurant_id>/edit/', methods=['GET', 'POST'])
def edit_restaurant(restaurant_id):
    edited_restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    if request.method == 'POST':
        if request.form['name']:
            edited_restaurant.name = request.form['name']
        session.add(edited_restaurant)
        session.commit()
        flash("Updated restaurant info.")
        return redirect(url_for('list_restaurants'))
    else:
        return render_template('restaurant_edit.html', restaurant=edited_restaurant)


@app.route('/restaurant/<int:restaurant_id>/delete/', methods=['GET', 'POST'])
def delete_restaurant(restaurant_id):
    restaurant_to_delete = session.query(Restaurant).filter_by(id=restaurant_id).one()
    if request.method == 'POST':
        session.delete(restaurant_to_delete)
        session.commit()
        flash("Restaurant deleted.")
        return redirect(url_for('list_restaurants'))
    else:
        return render_template('restaurant_delete.html', restaurant=restaurant_to_delete)


@app.route('/restaurant/<int:restaurant_id>/menu/new/', methods=['GET', 'POST'])
def new_menu_item(restaurant_id):
    if request.method == 'POST':
        menu_item = MenuItem(name=request.form['name'],
                             course=request.form['course'],
                             description=request.form['description'],
                             price="$" + request.form['price'],
                             restaurant_id=restaurant_id)
        session.add(menu_item)
        session.commit()
        flash("New menu item created.")
        return redirect(url_for('view_restaurant_menu', restaurant_id=restaurant_id))
    else:
        restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
        return render_template('menu_new.html', restaurant_id=restaurant_id, restaurant=restaurant)


@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/edit/', methods=['GET', 'POST'])
def edit_menu_item(restaurant_id, menu_id):
    edited_item = session.query(MenuItem).filter_by(id=menu_id).one()
    edited_item_price = edited_item.price[1:]
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
        flash("Menu item updated.")
        return redirect(url_for('view_restaurant_menu', restaurant_id=restaurant_id))
    else:
        return render_template('menu_edit.html', restaurant_id=restaurant_id, menu_id=menu_id, item=edited_item,
                               item_price=edited_item_price)


@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/delete/', methods=['GET', 'POST'])
def delete_menu_item(restaurant_id, menu_id):
    item_to_delete = session.query(MenuItem).filter_by(id=menu_id).one()
    if request.method == 'POST':
        session.delete(item_to_delete)
        session.commit()
        flash("Menu item deleted.")
        return redirect(url_for('view_restaurant_menu', restaurant_id=restaurant_id))
    else:
        return render_template('menu_delete.html', restaurant_id=restaurant_id, menu_id=menu_id, item=item_to_delete)


@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/JSON')
def view_menu_item_json(restaurant_id, menu_id):
    item = session.query(MenuItem).filter_by(id=menu_id, restaurant_id=restaurant_id).one()
    return jsonify(MenuItem=item.serialize)


if __name__ == '__main__':
    app.secret_key = 'super_secret_key_1'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
