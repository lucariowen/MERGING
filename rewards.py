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
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///rshop.db'
UPLOAD_FOLDER = 'static/uploads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
rshop_db = SQLAlchemy(app)


class Rewards(rshop_db.Model):
    id = rshop_db.Column(rshop_db.Integer, primary_key=True)
    name = rshop_db.Column(rshop_db.String(100), nullable=False, unique=True)
    price = rshop_db.Column(rshop_db.Integer, nullable=False)
    quantity = rshop_db.Column(rshop_db.Integer, nullable=False)
    category = rshop_db.Column(rshop_db.String(100), nullable=False)
    date_added = rshop_db.Column(rshop_db.DateTime, default=datetime.now())
    rewardpic = rshop_db.Column(rshop_db.String(), nullable=False)

    def __repr__(self):
        return '<Name %r>' % self.name


with app.app_context():
    rshop_db.create_all()


# Create a form class
class rewardform(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    price = IntegerField('Price', validators=[DataRequired()])
    quantity = IntegerField('Quantity', validators=[DataRequired()])
    category = StringField('Category', validators=[DataRequired()])
    rewardpic = FileField("Reward Image")
    submit = SubmitField('Submit', validators=[DataRequired()])


@app.route('/')
def home():
    return render_template("homepg.html")


@app.route('/manage_rewards')
def rmanage():
    ourrewards = Rewards.query.order_by(Rewards.date_added)
    return render_template('rmanage.html', ourrewards=ourrewards)


@app.route('/rewards_shop')
def rshop():
    ourrewards = Rewards.query.order_by(Rewards.date_added)
    return render_template('rshop.html', ourrewards=ourrewards)


@app.route('/add_rewards', methods=['GET', 'POST'])
def addrewards():
    name = None
    form = rewardform()
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

            reward = Rewards(name=form.name.data, price=form.price.data, quantity=form.quantity.data,
                             category=form.category.data, rewardpic=pic_name)

            rshop_db.session.add(reward)
            rshop_db.session.commit()
            name = form.name.data
            form = rewardform(formdata=None)
            flash('Reward Added Successfully', 'success')
            return render_template('addr.html', name=name, form=form)

        except IntegrityError:
            rshop_db.session.rollback()
            flash('Error! Name has already been used', 'danger')
            return render_template('addr.html', name=name, form=form)
        except AttributeError:
            rshop_db.session.rollback()
            flash('Error! Please insert an image', 'danger')
            return render_template('addr.html', name=name, form=form)
    else:
        pass
        ourrewards = Rewards.query.order_by(Rewards.date_added)
    return render_template('addr.html', name=name, form=form, ourrewards=ourrewards)


@app.route('/update_rewards/<int:id>', methods=['GET', 'POST'])
def updaterewards(id):
    form = rewardform()
    update = Rewards.query.get_or_404(id)
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
            rshop_db.session.commit()
            flash('Updated Successfully', 'success')
            return render_template('updater.html', form=form, update=update)

        except IntegrityError:
            rshop_db.session.rollback()
            flash('Error! Name has already been used', 'danger')
            return render_template('updater.html', form=form, update=update)
        except AttributeError:
            rshop_db.session.rollback()
            flash('Error! Please insert an image', 'danger')
            return render_template('updater.html', form=form, update=update)

    else:
        pass
    return render_template('updater.html', form=form, update=update)


@app.route('/delete_rewards/<int:id>')
def deleterewards(id):
    delete = Rewards.query.get_or_404(id)
    name = None
    form = rewardform()
    try:
        rshop_db.session.delete(delete)
        rshop_db.session.commit()
        flash('Reward Deleted Successfully', 'success')
        ourrewards = Rewards.query.order_by(Rewards.date_added)
        return render_template('rmanage.html', name=name, form=form, ourrewards=ourrewards)

    except:
        flash('Error! There was a problem deleting the reward''danger')
        return render_template('rmanage.html', name=name, form=form, ourrewards=ourrewards)


if __name__ == '__main__':
    app.run(debug=True)
