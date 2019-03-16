from flask import Flask, render_template, request, flash, redirect, url_for
from persistence.config import DbSession
from persistence.entities import Category, Item
# from 

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
        name = request.form.get('name')
        if (name == None):
            raise Exception("Empty item name")
        dbSession = DbSession()
        category = Item(name = name, description = description, category_id = cat_id)
        dbSession.add(category)
        dbSession.commit()
        dbSession.close()
        flash('Item successfully created.')
        return redirect(url_for('main'))
    return render_template('items/new.html')

@app.route('/categories/<category_name>', methods=['GET'])
def list_category(category_name):

    dbSession = DbSession()
    try:
        category = dbSession.query(Category).filter_by(name=category_name).one()
        items = dbSession.query(Item).filter_by(category_id = category.id)
        return render_template('categories/single.html', items=items, category=category)
    except Exception:
        flash('Category not found')
        return redirect(url_for('main'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)