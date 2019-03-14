from flask import Flask, render_template
from persistence.config import Session
from persistence.entities import Category

session = Session()
app = Flask(__name__)

@app.route('/', methods=['GET'])
def main():
    categories = session.query(Category).all()
    return render_template("main.html", categories=categories)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)