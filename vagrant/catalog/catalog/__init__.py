import json
from xml.dom import minidom
from xml.etree.ElementTree import Element, SubElement, tostring

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask import make_response
from flask import session as login_session
from flask_restful import Api
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Base, Restaurant, MenuItem, User

app = Flask(__name__)
api = Api(app)

from catalog import loginviews
from catalog import restaurantviews
from catalog import menuviews

CLIENT_ID = json.loads(open('catalog/client_secrets.json', 'r').read())['web']['client_id']

# Create an engine that stores data in the local directory's
# restaurantmenu.db file.
engine = create_engine('sqlite:////vagrant/catalog/catalog/restaurantapp.db')

# Create all tables in the engine. This is equivalent to 'Create Table'
# statement in SQL.
# bind engine obj to our base class
Base.metadata.create_all(engine)

DBSession = sessionmaker(bind=engine)
session = DBSession()


@app.route('/api/v1.0/restaurant', methods=['GET'])
def api_list_restaurants():
    restaurants = session.query(Restaurant).all()

    if request.headers['Accept'] == 'application/json':
        data = jsonify(Restaurant=[r.serialize for r in restaurants])
        return output_json(data, 200, {'Content-Type': 'application/json'})
    elif request.headers['Accept'] == 'application/xml':
        data = data_xml([r.serialize for r in restaurants], 'restaurants', 'restaurant')
        return output_xml(data, 200, {'Content-Type': 'application/xml'})
    else:
        resp = make_response(jsonify({'error': 'Unsupported Media Type'}), 415)
        resp.headers.extend({})
        return resp


@api.representation('application/json')
def output_json(data, code, headers=None):
    resp = make_response(data, code)
    resp.headers.extend(headers or {})
    return resp


@api.representation('application/xml')
def output_xml(data, code, headers=None):
    resp = make_response(data, code)
    resp.headers.extend(headers or {})
    return resp


def data_xml(data, root_ele, sub_root_ele):
    root = Element(root_ele)
    for _dict in data:
        sub_root = SubElement(root, sub_root_ele)
        for key in _dict:
            data_ele = SubElement(sub_root, key)
            data_ele.text = _dict[key]
    raw = tostring(root, 'utf-8')
    parsed = minidom.parseString(raw)
    return parsed.toprettyxml(indent=" ")


@app.route('/api/v1.0/restaurant/<int:restaurant_id>/menu', methods=['GET'])
def api_view_restaurant_menu(restaurant_id):
    items = session.query(MenuItem).filter_by(restaurant_id=restaurant_id).all()

    if request.headers['Accept'] == 'application/json':
        data = jsonify(MenuItem=[i.serialize for i in items])
        return output_json(data, 200, {'Content-Type': 'application/json'})
    elif request.headers['Accept'] == 'application/xml':
        data = data_xml([i.serialize for i in items], 'menuitems', 'menuitem')
        return output_xml(data, 200, {'Content-Type': 'application/xml'})
    else:
        resp = make_response(jsonify({'error': 'Unsupported Media Type'}), 415)
        resp.headers.extend({})
        return resp


@app.route('/api/v1.0/restaurant/<int:restaurant_id>/menu/<int:menu_id>', methods=['GET'])
def view_menu_item_json(restaurant_id, menu_id):
    item = session.query(MenuItem).filter_by(id=menu_id, restaurant_id=restaurant_id).one()

    if request.headers['Accept'] == 'application/json':
        data = jsonify(MenuItem=item.serialize)
        return output_json(data, 200, {'Content-Type': 'application/json'})
    elif request.headers['Accept'] == 'application/xml':
        data = data_xml([item.serialize], 'menuitems', 'menuitem')
        return output_xml(data, 200, {'Content-Type': 'application/xml'})
    else:
        resp = make_response(jsonify({'error': 'Unsupported Media Type'}), 415)
        resp.headers.extend({})
        return resp


if __name__ == '__main__':
    app.secret_key = 'super_secret_key_1'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
