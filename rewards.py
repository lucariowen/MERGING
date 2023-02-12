from flask import Flask, render_template, request, redirect, url_for, flash
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, FloatField, SubmitField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 's'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///rshop.db'
rshop_db = SQLAlchemy(app)


class Rewards(rshop_db.Model):
    id = rshop_db.Column(rshop_db.Integer, primary_key=True)
    name = rshop_db.Column(rshop_db.String(100), nullable=False, unique=True)
    price = rshop_db.Column(rshop_db.Integer, nullable=False)
    quantity = rshop_db.Column(rshop_db.Integer, nullable=False)
    category = rshop_db.Column(rshop_db.String(100), nullable=False)
    date_added = rshop_db.Column(rshop_db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Name %r>' % self.name


with app.app_context():
    rshop_db.create_all()


# Create a form class
class rewardform(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    price = IntegerField('Price', validators=[DataRequired()])
    quantity=IntegerField('Quantity', validators=[DataRequired()])
    category=StringField('Category', validators=[DataRequired()])
    submit = SubmitField('Submit')


@app.route('/')
def home():
    return render_template("homepg.html")


@app.route('/manage_rewards')
def rmanage():
    return render_template('rmanage.html')


@app.route('/add_rewards', methods=['GET', 'POST'])
def addrewards():
    name = None
    form = rewardform()
    if form.validate_on_submit():
        # reward = Rewards.query.filter_by(name=form.name.data)
        reward = Rewards(name=form.name.data, price=form.price.data,quantity=form.quantity.data,category=form.category.data)
        rshop_db.session.add(reward)
        rshop_db.session.commit()
        name = form.name.data
        # form.name.data = ''
        # form.price.data = ''
        # form.quantity.data=''
        # form.category.data=''
        form = rewardform(formdata=None)
        flash('Reward Added Successfully', 'success')
    ourrewards = Rewards.query.order_by(Rewards.date_added)
    return render_template('addr.html', name=name, form=form, ourrewards=ourrewards)

if __name__ == '__main__':
    app.run(debug=True)
