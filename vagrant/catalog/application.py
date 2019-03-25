from flask import Flask, render_template, request, flash, redirect, url_for, jsonify, session as login_session, make_response
from persistence.config import DbSession
from persistence.entities import Category, Item
from sqlalchemy.orm import joinedload
from sqlalchemy.orm.exc import NoResultFound
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import json
import random
import string
import httplib2
import requests
import logging
import traceback
import os

app = Flask(__name__)
app.secret_key = '138323278'

CLIENT_ID = json.loads(open('client_secrets.json', 'r').read())[
    'web']['client_id']

if CLIENT_ID is None:
    raise Exception("File client_secrets.json should be provided in root")

google_client_id = os.getenv("G_CLIENT_ID")

if google_client_id is None:
    raise Exception(
        "Environment G_CLIENT_ID should provide the Google client id.")

# Find all categories, used in layout
def find_categories():
    dbSession = DbSession()
    categories = dbSession.query(Category).all()
    return categories

# Generates token to prevent CSRF attacks
def newState():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return state

app.jinja_env.globals.update(find_categories=find_categories)
app.jinja_env.globals.update(newState=newState)
app.jinja_env.globals.update(google_client_id=google_client_id)

# Main route
@app.route('/', methods=['GET'])
def main():
    return render_template("home.html")

# Authentication strongly inspired in lesson's code
@app.route('/gconnect', methods=['POST'])
def gconnect():
    # prevents CSRF validating server-side generated token
    if request.args.get('state') != login_session['state']:
        return json_response("Invalid state parameter.", 500)

    code = request.data
    print("Actual code is: %s" % code)

    # Exchange google's code for the token
    try:
        oauth_flow = flow_from_clientsecrets(
            'client_secrets.json', scope='openid')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError as error:
        traceback.print_exc()
        return json_response(
            "Failed to upgrade the authorization code. %s" %
            str(error), 401)

    # Retrieve the token info by the access token
    access_token = credentials.access_token
    url = (
        'https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s' %
        access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])

    if result.get('error') is not None:
        return json_response(result.get('error'), 500)

    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        return json_response(
            "Token's user ID doesn't match given user ID.", 401)

    if result['issued_to'] != CLIENT_ID:
        return json_response("Token's client ID does not match app's.", 401)

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        return json_response('Current user is already connected.', 200)

    # Setup session with retrieved data
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()
    login_session['name'] = data['name']
    return redirect(url_for('main'))

# utilitary method that formats the output in json format
def json_response(message, statusCode):
    response = make_response(jsonify(message=message), statusCode)
    if statusCode >= 400:
        logging.error(message)
    response.headers['Content-Type'] = 'application/json'
    return response

# ivalidates the token in google server.
@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        return json_response("Current user not connected.", 401)
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['name']
        flash("Successfully disconnected")
    else:
        flash("Failed to revoke token for given user")
    return redirect(url_for('main'))


# creates a new item, available if user is logged in
@app.route('/items/new', methods=['GET', 'POST'])
def new_item():
    if login_session.get('name') is None:
        flash("Login first to create items")
        return redirect(url_for('main'))

    dbSession = DbSession()
    if request.method == 'POST':
        params = validate_and_extract_form_params(
            request, ['name', 'description', 'category_id'])
        item = Item(
            name=params['name'],
            description=params['description'],
            category_id=params['category_id'],
            user_id=login_session.get('gplus_id'))
        dbSession.add(item)
        dbSession.commit()
        flash('Item successfully created.')
        return redirect(
            url_for(
                'list_category',
                category_name=item.category.name))

    selected_category = request.args.get('category')
    return render_template(
        'items/new.html',
        categories=find_categories(),
        item=Item(
            category=Category(
                name=selected_category)))

# utilitary function to validate request inputs
def validate_and_extract_form_params(request, params):
    final_params = {}
    for param_name in params:
        form_value = request.form.get(param_name)
        if form_value is None:
            raise Exception('Missing required param: %s' % param_name)
        final_params[param_name] = form_value
    return final_params

# Controller that lists all items from category
@app.route('/categories/<category_name>', methods=['GET'])
def list_category(category_name):
    dbSession = DbSession()
    try:
        category = dbSession.query(Category).filter_by(
            name=category_name).one()
        items = dbSession.query(Item).filter_by(category_id=category.id).all()
        return render_template(
            'categories/single.html',
            items=items,
            category=category)
    except NoResultFound:
        flash('Category not found')
        return redirect(url_for('main'))

# Controller that allows to edit an item that the logged user owns
@app.route('/catalog/<item_name>/edit', methods=['GET', 'POST'])
def edit_item(item_name):
    try:
        dbSession = DbSession()
        item = dbSession.query(Item).filter_by(name=item_name).one()

        if not item.user_id == login_session.get('gplus_id'):
            flash("Not authorized to edit this item")
            return redirect(url_for('main'))

        if request.method == 'POST':
            params = validate_and_extract_form_params(
                request, ['name', 'description', 'category_id'])
            item.name = params['name']
            item.description = params['description']
            item.category_id = params['category_id']
            dbSession.add(item)
            dbSession.commit()
            flash('Item successfully updated')
            return redirect(
                url_for(
                    'list_category',
                    category_name=item.category.name))
        return render_template(
            'items/new.html',
            categories=find_categories(),
            item=item)
    except NoResultFound:
        flash('Item not found')
        return redirect(url_for('main'))

# Controller that allows to delete an item that the logged user owns
@app.route('/catalog/<item_name>/delete', methods=['GET', 'POST'])
def delete_item(item_name):
    try:
        dbSession = DbSession()
        item = dbSession.query(Item).filter_by(
            name=item_name).options(
            joinedload('category')).one()

        if not item.user_id == login_session.get('gplus_id'):
            flash("Not authorized to edit this item")
            return redirect(url_for('main'))

        if request.method == 'POST':
            dbSession.delete(item)
            dbSession.commit()
            flash('Item successfully deleted')
            return redirect(
                url_for(
                    'list_category',
                    category_name=item.category.name))

        return render_template('items/delete.html', item=item)

    except NoResultFound:
        flash('Item not found')
        return redirect(url_for('main'))

# Provides the list of all categories
@app.route('/catalog.json', methods=['GET'])
def json_endpoint():
    dbSession = DbSession()
    categories = dbSession.query(Category).all()
    return jsonify(categories=[category.serialize for category in categories])


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
