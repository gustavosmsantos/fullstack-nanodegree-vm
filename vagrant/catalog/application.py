from flask import Flask, render_template, request, flash, redirect, url_for
from persistence.config import DbSession
from persistence.entities import Category, Item
from sqlalchemy.orm import joinedload
from sqlalchemy.orm.exc import NoResultFound

app = Flask(__name__)
app.secret_key='138323278'

def find_categories():
    dbSession = DbSession() 
    categories = dbSession.query(Category).all()
    return categories

app.jinja_env.globals.update(find_categories=find_categories)

@app.route('/', methods=['GET'])
def main():
    return render_template("home.html")

@app.route('/items/new', methods=['GET','POST'])
def new_item():
    dbSession = DbSession()
    if request.method == 'POST':
        params = validate_and_extract_form_params(request, ['name', 'description', 'category_id'])
        item = Item(name = params['name'], description = params['description'],
            category_id = params['category_id'])
        dbSession.add(item)
        dbSession.commit()
        flash('Item successfully created.')
        return redirect(url_for('list_category', category_name=item.category.name))

    selected_category = request.args.get('category')
    return render_template('items/new.html', categories=find_categories(), item=Item(category=Category(name = selected_category)))

def validate_and_extract_form_params(request, params):
    final_params = {}
    for param_name in params:
        form_value = request.form.get(param_name)
        if form_value == None:
            raise Exception('Missing required param: %s' % param_name)
        final_params[param_name] = form_value
    return final_params

@app.route('/categories/<category_name>', methods=['GET'])
def list_category(category_name):
    dbSession = DbSession()
    try:
        category = dbSession.query(Category).filter_by(name=category_name).one()
        items = dbSession.query(Item).filter_by(category_id = category.id).all()
        return render_template('categories/single.html', items=items, category=category)
    except NoResultFound:
        flash('Category not found')
        return redirect(url_for('main'))

@app.route('/catalog/<item_name>/edit', methods=['GET', 'POST'])
def edit_item(item_name):
    try:
        dbSession = DbSession()
        item = dbSession.query(Item).filter_by(name=item_name).one()
        if request.method == 'POST':
            params = validate_and_extract_form_params(request, ['name', 'description', 'category_id'])
            item.name = params['name']
            item.description = params['description']
            item.category_id = params['category_id']
            dbSession.add(item)
            dbSession.commit()
            flash('Item successfully updated')
            return redirect(url_for('list_category', category_name=item.category.name))
        return render_template('items/new.html', categories=find_categories(), item=item)
    except NoResultFound: 
        flash('Item not found')
        return redirect(url_for('main'))

@app.route('/catalog/<item_name>/delete', methods=['GET', 'POST'])
def delete_item(item_name):
    try:
        dbSession = DbSession()
        item = dbSession.query(Item).filter_by(name=item_name).options(joinedload('category')).one()
        if request.method == 'POST':
            dbSession.delete(item)
            dbSession.commit()
            flash('Item successfully deleted')
            return redirect(url_for('list_category', category_name=item.category.name))

        return render_template('items/delete.html', item=item)

    except NoResultFound: 
        flash('Item not found')
        return redirect(url_for('main'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)