import json
import random
import string

import httplib2
import requests
from catalog import app
from flask import make_response
from flask import render_template, request, redirect, url_for, flash
from flask import session as login_session
from oauth2client.client import FlowExchangeError
from oauth2client.client import flow_from_clientsecrets
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Base, User

# Create an engine that stores data in the local directory's
# restaurantmenu.db file.
engine = create_engine('sqlite:////vagrant/catalog/catalog/restaurantapp.db')

# Create all tables in the engine. This is equivalent to 'Create Table'
# statement in SQL.
# bind engine obj to our base class
Base.metadata.create_all(engine)

DBSession = sessionmaker(bind=engine)
session = DBSession()

G_CLIENT_ID = json.loads(open('catalog/client_secrets.json', 'r').read())['web']['client_id']

FB_APP_ID = json.loads(open('catalog/fb_client_secrets.json', 'r').read())['web']['app_id']
FB_APP_SECRET = json.loads(open('catalog/fb_client_secrets.json', 'r').read())['web']['app_secret']


@app.route('/login')
def show_login():
    """ create anti-forgery state token and forward it to login.html page """
    state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


@app.route('/logout')
def show_logout():
    """ just renders logout.html page """
    return render_template('logout.html')


@app.route('/connect', methods=['POST'])
def connect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Obtain authorization code
    code = request.data

    if request.args.get('provider') == 'google':
        data = g_connect(code)
    elif request.args.get('provider') == 'facebook':
        data = fb_connect(code)
    else:
        response = make_response(json.dumps('Unsupported provider in query params.'), 400)
        response.headers['Content-Type'] = 'application/json'
        return response

    login_session['username'] = data['name']
    login_session['email'] = data['email']

    # check if user persist in db
    # else create user
    if get_user_id(login_session['email']) is None:
        login_session['user_id'] = create_user(login_session)
    else:
        login_session['user_id'] = get_user_id(login_session['email'])

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("Logged in as %s" % login_session['username'], category='success')
    return output


def g_connect(code):
    """ google connect
    Args:
        code: authorization code

    Returns: json - user info data

    """
    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('catalog/client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(json.dumps('Failed to upgrade the authorization code.'), 401)
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
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != G_CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')

    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Get user info
    user_info_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(user_info_url, params=params)
    data = answer.json()

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['provider'] = 'google'
    login_session['gplus_id'] = gplus_id
    login_session['picture'] = data['picture']

    return data


def fb_connect(access_token):
    """ facebook connect
    Args:
        access_token: fb exchange token

    Returns: json - user info data

    """
    url = 'https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id=%s&client_secret=%s&fb_exchange_token=%s' % (
        FB_APP_ID, FB_APP_SECRET, access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]

    # Use token to get user info from API
    token = result.split("&")[0]

    user_info_url = "https://graph.facebook.com/v2.5/me"

    # Get user picture
    url = user_info_url + '/picture?%s&redirect=0&height=200&width=200' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    pic_data = json.loads(result)

    url = user_info_url + '?%s&fields=name,id,email' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)

    login_session['access_token'] = token.split("=")[1]
    login_session['provider'] = 'facebook'
    login_session['facebook_id'] = data["id"]
    login_session['picture'] = pic_data["data"]["url"]

    return data


@app.route('/disconnect', methods=['POST'])
def disconnect():
    """ handles logout request for both google and facebook """
    access_token = login_session.get('access_token')

    if access_token is None:
        flash('Current user not connected.', category='warning')
        return redirect(url_for('list_restaurants'))

    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            g_disconnect(access_token)
        elif login_session['provider'] == 'facebook':
            fb_disconnect(access_token)
        else:
            flash('Unknown provider.', category='error')
            return redirect('/restaurant')

        del login_session['access_token']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['provider']
        del login_session['user_id']
        flash("Logged out.", category='success')
        return redirect('/restaurant')


def g_disconnect(access_token):
    """ logout from google session """
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    check_response(h.request(url, 'GET')[0])
    del login_session['gplus_id']


def fb_disconnect(access_token):
    """ logout from facebook session """
    url = 'https://graph.facebook.com/%s/permissions?access_token=%s' % (login_session['facebook_id'], access_token)
    h = httplib2.Http()
    check_response(h.request(url, 'DELETE')[0])
    del login_session['facebook_id']


def check_response(response):
    """ check revoke token's response """
    if response['status'] != '200':
        flash('Failed to revoke token for given user.', category='error')
        return redirect('/restaurant')


def create_user(login_session):
    """
    creates a new user.
    Args:
        login_session: google/facebook login session obj

    Returns: id of newly created user

    """
    new_user = User(name=login_session['username'], email=login_session['email'], image=login_session['picture'])
    session.add(new_user)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def get_user_info(user_id):
    """
    get user query result obj.
    Args:
        user_id: user id whose info is needed

    Returns: user query result obj

    """
    try:
        return session.query(User).filter_by(id=user_id).one()
    except:
        return None


def get_user_id(email):
    """
    get user id
    Args:
        email: user's email address.

    Returns: user id

    """
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None
