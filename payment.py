from flask import Flask, render_template, flash, redirect, url_for, request
from flask_wtf import FlaskForm
from wtforms import DateField, TextAreaField, StringField, SubmitField, EmailField, SelectField, validators, PasswordField
from wtforms.validators import DataRequired, Email, Length
app = Flask(__name__)

#form class


app.config['SECRET_KEY'] = "dsf"


class NamerForm(FlaskForm):
    address = StringField("Address", validators=[DataRequired()])
    number = StringField("Contact Number", validators=[DataRequired(), Length(min = 8, max = 8) ])
    postalcode = StringField("Postal Code", validators=[DataRequired(), Length(min=6, max=6)])
    name = StringField("Name on Card:", validators=[DataRequired()])
    cnumber = StringField("Credit card Number", validators=[DataRequired(), Length(min = 16, max = 16)])
    cvv = PasswordField("CVV", validators=[DataRequired(), Length(min= 3, max= 3)])
    month = SelectField('Expiry Month', choices=[('3', '03'), ('4', '04'), ('5', '05'), ('6', '06'), ('7', '07'), ('8', '08'), ('9', '09'), ('10', '10'), ('11', '11'), ('12', '12')])
    year = SelectField('Expiry Year', choices=[('1', '2023'), ('2', '2024'), ('3', '2025'), ('4', '2026'), ('5', '2027'), ('6', '2028')])
    submit = SubmitField("Submit")

@app.route('/')
def index():
    return render_template("shop.html")


@app.route("/name", methods=['GET', 'POST'])
def name():

    form = NamerForm()
    if form.validate_on_submit():
        form.address.data = ''
        form.number.data = ''
        form.postalcode.data = ''
        form.name.data = ''
        form.cnumber.data = ''
        form.cvv.data = ''
        form.month.data = ''
        flash("Payment Successful!")
        return redirect(url_for('namtest'))
    return render_template("name.html" , form = form)

@app.route('/namtest')
def namtest():

    return render_template('namtest.html')


if __name__ == "__main__":
    app.run()

