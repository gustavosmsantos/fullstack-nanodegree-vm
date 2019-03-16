from flask import Flask, render_template, request, flash, redirect, url_for
from persistence.config import DbSession
from persistence.entities import Category, Item
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
    if request.method == 'POST':
        params = validate_and_extract_form_params(request, ['name', 'description', 'category_id'])
        dbSession = DbSession()
        category = Item(name = params['name'], description = params['description'],
            category_id = params['category_id'])
        dbSession.add(category)
        dbSession.commit()
        dbSession.close()
        flash('Item successfully created.')
        return redirect(url_for('main'))

    selected_category = request.args.get('category')
    return render_template('items/new.html', categories=find_categories(), selected=selected_category)

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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)