import datetime

from flask import Flask, render_template, flash, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import PasswordField, DateField, TextAreaField, StringField, SubmitField, EmailField, SelectField, validators
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.app_context().push()
    #form class
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///transaction.db'
app.config['SECRET_KEY'] = "dsf"

db = SQLAlchemy(app)


class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key= True)
    name = db.Column(db.String(200), nullable = False)
    email = db.Column(db.String(120), nullable = False)
    date_added = db.Column(db.DateTime, default = datetime.timezone)

    def __repr__(self):
        return "<name %r>" %self.name




class NamerForm(FlaskForm):
    firstname = StringField("First name", [validators.DataRequired("Please enter a value")])
    lastname = StringField("last name: ", [validators.DataRequired("Please enter a value")])
    email = EmailField('Email', [validators.optional(), validators.Email("Please enter a value")])
    address= TextAreaField("Address: ", [validators.DataRequired("Please enter a value")])
    country = SelectField(u'country', choices=[('SG', 'Singapore'), ('MY', 'Malaysia'), ('IN', 'Indonesia')])
    postalcode= StringField("Postal Code: ", [validators.DataRequired("Please enter a value"), validators.NumberRange(min=100000,max=999999)])
    name= StringField("Name on card: ", [validators.DataRequired("Please enter a value")])
    number = StringField("Credit card number: ", [validators.DataRequired("Please enter a value"), validators.length(min=16, max=16)])
    date= DateField("Expiring", [validators.DataRequired("Please enter a value")], format="%Y-%m")
    cvv = PasswordField("CVV: ", [validators.DataRequired("Please enter a value"), validators.length(min=3, max= 3)])
    submit = SubmitField("submit")



@app.route('/')
def index():
    return render_template("index.html")


#invalid URL
@app.errorhandler(404)
def page_not_found (e):
    return render_template("404.html"), 404

# Internal Server error
@app.errorhandler(500)
def page_not_found (e):
    return render_template("500.html"), 500

# Name page



@app.route("/checkout", methods=['GET', 'POST'])
def add_transaction():
    form = NamerForm()
    firstname = None
    lastname = None
    email = None
    address = None
    country = None
    postalcode = 0
    name = None
    number = 0
    date = None
    cvv = 0


    if form.validate_on_submit():
        transaction = Transaction.query.filter_by(id=form.email.data).first()
        if transaction:
            pass
        else:
           transaction = Transaction(name=form.name.data, email=form.email.data)
           db.session.add(transaction)
           db.session.commit()

        firstname = form.firstname.data
        lastname = form.lastname.data
        email = form.email.data
        address = form.address.data
        country = form.country.data
        postalcode = form.postalcode.data
        name = form.name.data
        number = form.number.data
        date = form.date.data
        cvv = form.cvv.data


        form.firstname.data = ''
        form.lastname.data = ''
        form.email.data = ''
        form.email.data = ''
        form.address.data = ''
        form.country.data = ''
        form.postalcode.data = ''
        form.name.data = ''
        form.number.data = ''
        form.date.data = ''
        form.cvv.data = ''
        flash("Transaction successful!")
        return redirect(url_for('name'))

    total_transaction = Transaction.query.order_by(Transaction.date_added)
    return render_template('checkout.html', form = form
                               # firstname= firstname,
                               # total_transaction = total_transaction,
                               # lastname = lastname,
                               # email = email,
                               # address = address,
                               # country = country,
                               # postalcode = postalcode,
                               # name = name,
                               # number = number,
                               # date = date,
                               # cvv = cvv,
                               )



@app.route("/name", methods=['GET', 'POST'])
def name():
    name = None
    form = NamerForm()
    if form.validate_on_submit():
        name = form.name.data
        form.name.data = ''
        flash("Payment Successful!")
    return render_template("name.html", name = name, form = form)

db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
