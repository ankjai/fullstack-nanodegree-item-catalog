from xml.dom import minidom
from xml.etree.ElementTree import Element, SubElement, tostring

from . import app
from flask import make_response
from flask import request, jsonify
from flask_restful import Api
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Base, Restaurant, MenuItem

api = Api(app)

# Create an engine that stores data in the local directory's
# restaurantapp.db file.
engine = create_engine('sqlite:///restaurantapp.db', connect_args={'check_same_thread': False})

# Create all tables in the engine. This is equivalent to 'Create Table'
# statement in SQL.
# bind engine obj to our base class
Base.metadata.create_all(engine)

DBSession = sessionmaker(bind=engine)
session = DBSession()


@app.route('/api/v1.0/restaurant', methods=['GET'])
def api_list_restaurants():
    """ List of restaurants in the db.

    Two supported response format: JSON and XML

    Returns: all restaurants in format as per 'Accept' header type in request

    """
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


@app.route('/api/v1.0/restaurant/<int:restaurant_id>/', methods=['GET'])
@app.route('/api/v1.0/restaurant/<int:restaurant_id>/menu/', methods=['GET'])
def api_view_restaurant_menu(restaurant_id):
    """ All menu items in restaurant_id

    Two supported response format: JSON and XML

    Args:
        restaurant_id: id of the restaurant whose menu was requested

    Returns: all menu items of restaurant_id and in format as per
    'Accept' header type in request

    """
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


@app.route('/api/v1.0/restaurant/<int:restaurant_id>/menu/<int:menu_id>/', methods=['GET'])
def view_menu_item_json(restaurant_id, menu_id):
    """ List specific menu item of a specific restaurant

    Two supported response format: JSON and XML

    Args:
        restaurant_id: id of restaurant whose menu was requested
        menu_id: id of the menu item

    Returns: specific menu item of restaurant_id and in format as per
    'Accept' header type in request

    """
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


@api.representation('application/json')
def output_json(data, code, headers=None):
    """ make response to support 'application/json' media type
    Args:
        data: json data
        code: response code
        headers: response headers dictionary

    Returns: flask response object

    """
    resp = make_response(data, code)
    resp.headers.extend(headers or {})
    return resp


@api.representation('application/xml')
def output_xml(data, code, headers=None):
    """ make response to support 'application/xml' media type
    Args:
        data: xml data
        code: response code
        headers: response headers dictionary

    Returns: flask response object

    """
    resp = make_response(data, code)
    resp.headers.extend(headers or {})
    return resp


def data_xml(data, root_ele, sub_root_ele):
    """ converts serialized Restaurant/User object into xml
    Args:
        data: serialized Restaurant/User object
        root_ele: String - xml root element name
        sub_root_ele: String - xml sub root element name

    Returns: xml representation of data

    """
    root = Element(root_ele)
    for _dict in data:
        sub_root = SubElement(root, sub_root_ele)
        for key in _dict:
            data_ele = SubElement(sub_root, key)
            data_ele.text = _dict[key]
    raw = tostring(root, 'utf-8')
    parsed = minidom.parseString(raw)
    return parsed.toprettyxml(indent=" ")
