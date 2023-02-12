from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy



app = Flask(__name__)
app.secret_key = "Secret Key"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

app.app_context().push()

class data(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(100))
    brand = db.Column(db.String(100))
    category = db.Column(db.String(100))
    quantity = db.Column(db.String(100))
    price = db.Column(db.String(100))

    def __init__(self, name, brand, category, quantity, price):
        self.name = name
        self.brand = brand
        self.category = category
        self.quantity = quantity
        self.price = price


@app.route('/')
def Index():
    all_data = data.query.all()
<<<<<<< HEAD
=======

>>>>>>> e43af79c29e09cbf1a39370be6694f1e4249a500
    return render_template('index.html',  products = all_data)



@app.route('/insert', methods = ['POST'])
def insert():
<<<<<<< HEAD
    if request.method == 'POST':
=======

    if request.method == 'POST':

>>>>>>> e43af79c29e09cbf1a39370be6694f1e4249a500
        name = request.form['name']
        brand = request.form['brand']
        category = request.form['category']
        quantity = request.form['quantity']
        price = request.form['price']
<<<<<<< HEAD
        my_data = data(name, brand, category, quantity, price)
        db.session.add(my_data)
        db.session.commit()
        flash("Product Added Successfully")
=======


        my_data = data(name, brand, category, quantity, price)
        db.session.add(my_data)
        db.session.commit()

        flash("Product Added Successfully")

>>>>>>> e43af79c29e09cbf1a39370be6694f1e4249a500
        return redirect(url_for('Index'))

@app.route('/update', methods = ['GET', 'POST'])
def update():
<<<<<<< HEAD
    if request.method == 'POST':
        my_data = data.query.get(request.form.get('id'))
=======

    if request.method == 'POST':
        my_data = data.query.get(request.form.get('id'))

>>>>>>> e43af79c29e09cbf1a39370be6694f1e4249a500
        my_data.name = request.form['name']
        my_data.brand = request.form['brand']
        my_data.category = request.form['category']
        my_data.quantity = request.form['quantity']
        my_data.price = request.form['price']
<<<<<<< HEAD
        db.session.commit()
        flash("Product Updated Successfully")
=======

        db.session.commit()
        flash("Product Updated Successfully")

>>>>>>> e43af79c29e09cbf1a39370be6694f1e4249a500
        return redirect(url_for('Index'))


@app.route('/delete/<id>/', methods = ['GET', 'POST'])
def delete(id):
    my_data = data.query.get(id)
    db.session.delete(my_data)
    db.session.commit()
    flash("Product Deleted Successfully")
<<<<<<< HEAD
=======

>>>>>>> e43af79c29e09cbf1a39370be6694f1e4249a500
    return redirect(url_for('Index'))

@app.route('/index')
def index():
    return render_template("index.html")

@app.route('/home')
def home():
    return render_template("homepg.html")

if __name__ == '__main__':
    app.run(debug=True)
