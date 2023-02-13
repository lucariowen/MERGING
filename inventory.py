# from flask import Flask, render_template, request, redirect, url_for, flash
# from flask_sqlalchemy import SQLAlchemy
#
# app = Flask(__name__)
# app.secret_key = "Secret Key"
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
#
# db = SQLAlchemy(app)
#
# app.app_context().push()
#
#
# class data(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(100))
#     brand = db.Column(db.String(100))
#     category = db.Column(db.String(100))
#     quantity = db.Column(db.String(100))
#     price = db.Column(db.String(100))
#
#     def __init__(self, name, brand, category, quantity, price):
#         self.name = name
#         self.brand = brand
#         self.category = category
#         self.quantity = quantity
#         self.price = price
#
#
# @app.route('/')
# def Index():
#     all_data = data.query.all()
#     return render_template('index.html', products=all_data)
#
#
# @app.route('/insert', methods=['POST'])
# def insert():
#     if request.method == 'POST':
#         name = request.form['name']
#         brand = request.form['brand']
#         category = request.form['category']
#         quantity = request.form['quantity']
#         price = request.form['price']
#         my_data = data(name, brand, category, quantity, price)
#         db.session.add(my_data)
#         db.session.commit()
#         flash("Product Added Successfully")
#         return redirect(url_for('Index'))
#
#
# @app.route('/update', methods=['GET', 'POST'])
# def update():
#     if request.method == 'POST':
#         my_data = data.query.get(request.form.get('id'))
#
#         my_data.name = request.form['name']
#         my_data.brand = request.form['brand']
#         my_data.category = request.form['category']
#         my_data.quantity = request.form['quantity']
#         my_data.price = request.form['price']
#         db.session.commit()
#         flash("Product Updated Successfully")
#         return redirect(url_for('Index'))
#
#
# @app.route('/delete/<id>/', methods=['GET', 'POST'])
# def delete(id):
#     my_data = data.query.get(id)
#     db.session.delete(my_data)
#     db.session.commit()
#     flash("Product Deleted Successfully")
#     return redirect(url_for('Index'))
#
#
# @app.route('/index')
# def index():
#     return render_template("index.html")
#
#
# @app.route('/home')
# def home():
#     return render_template("shop.html")
#
#
# if __name__ == '__main__':
#     app.run(debug=True)
#

from flask import Flask, render_template, request, redirect, url_for, flash
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, FloatField, SubmitField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy.exc import IntegrityError, OperationalError
from flask_wtf.file import FileField
from werkzeug.utils import secure_filename
import uuid as uuid
import os
# import pytz

app = Flask(__name__)
app.config['SECRET_KEY'] = 's'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
UPLOAD_FOLDER = 'static/uploads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
db = SQLAlchemy(app)


class Inventory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    price = db.Column(db.Integer, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    category = db.Column(db.String(100), nullable=False)
    date_added = db.Column(db.DateTime, default=datetime.now())
    rewardpic = db.Column(db.String(), nullable=False)

    def __repr__(self):
        return '<Name %r>' % self.name


with app.app_context():
    db.create_all()


# Create a form class
class inventoryform(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    price = IntegerField('Price', validators=[DataRequired()])
    quantity = IntegerField('Quantity', validators=[DataRequired()])
    category = StringField('Category', validators=[DataRequired()])
    rewardpic = FileField("Reward Image")
    submit = SubmitField('Submit', validators=[DataRequired()])


# @app.route('/')
# def home():
#     return render_template("shop.html")


@app.route('/index')
def index():
    items = Inventory.query.order_by(Inventory.date_added)
    return render_template('index.html', items=items)


@app.route('/')
def shop():
    items = Inventory.query.order_by(Inventory.date_added)
    return render_template('shop.html', items=items)


@app.route('/add_items', methods=['GET', 'POST'])
def additems():
    name = None
    form = inventoryform()
    if form.validate_on_submit():
        # reward = Rewards.query.filter_by(name=form.name.data)
        try:
            rewardpic = form.rewardpic.data
            # Pic Name
            pic_filename = secure_filename(rewardpic.filename)
            # Set UUID, str to set as string to save in rshop_db
            pic_name = str(uuid.uuid1()) + '_' + pic_filename
            # Save pic
            saver = form.rewardpic.data
            saver.save(os.path.join(app.config['UPLOAD_FOLDER'], pic_name))

            reward = Inventory(name=form.name.data, price=form.price.data, quantity=form.quantity.data,
                             category=form.category.data, rewardpic=pic_name)

            db.session.add(reward)
            db.session.commit()
            name = form.name.data
            form = inventoryform(formdata=None)
            flash('Reward Added Successfully', 'success')
            return render_template('additems.html', name=name, form=form)

        except IntegrityError:
            db.session.rollback()
            flash('Error! Name has already been used', 'danger')
            return render_template('additems.html', name=name, form=form)
        except AttributeError:
            db.session.rollback()
            flash('Error! Please insert an image', 'danger')
            return render_template('additems.html', name=name, form=form)
    else:
        pass
        items = Inventory.query.order_by(Inventory.date_added)
    return render_template('additems.html', name=name, form=form, items=items)


@app.route('/update_items/<int:id>', methods=['GET', 'POST'])
def updateitems(id):
    form = inventoryform()
    update = Inventory.query.get_or_404(id)
    if request.method == "POST":
        update.name = request.form['name']
        update.price = request.form['price']
        update.quantity = request.form['quantity']
        update.category = request.form['category']

        update.rewardpic = request.files['rewardpic']

        # update.rewardpic.save(os.path.join(app.config['UPLOAD_FOLDER'], pic_name))

        pic_filename = secure_filename(update.rewardpic.filename)
        pic_name = str(uuid.uuid1()) + '_' + pic_filename
        saver = request.files['rewardpic']
        saver.save(os.path.join(app.config['UPLOAD_FOLDER'], pic_name))

        update.rewardpic = pic_name

        try:
            db.session.commit()
            flash('Updated Successfully', 'success')
            return render_template('updateitems.html', form=form, update=update)

        except IntegrityError:
            db.session.rollback()
            flash('Error! Name has already been used', 'danger')
            return render_template('updateitems.html', form=form, update=update)
        except AttributeError:
            db.session.rollback()
            flash('Error! Please insert an image', 'danger')
            return render_template('updateitems.html', form=form, update=update)

    else:
        pass
    return render_template('updateitems.html', form=form, update=update)


@app.route('/delete_items/<int:id>')
def deleteitems(id):
    delete = Inventory.query.get_or_404(id)
    name = None
    form = inventoryform()
    try:
        db.session.delete(delete)
        db.session.commit()
        flash('Item Deleted Successfully', 'success')
        items = Inventory.query.order_by(Inventory.date_added)
        return render_template('index.html', name=name, form=form, items=items)

    except:
        flash('Error! There was a problem deleting the reward''danger')
        return render_template('index.html', name=name, form=form, items=items)


if __name__ == '__main__':
    app.run(debug=True)
