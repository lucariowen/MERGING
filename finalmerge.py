from flask import Flask, render_template, url_for, redirect, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, PasswordField, SubmitField, FloatField, IntegerField, DateField, TextAreaField, EmailField, SelectField, validators
from wtforms.validators import InputRequired, Length, ValidationError, DataRequired, Email
from flask_bcrypt import Bcrypt
from email_validator import validate_email, EmailNotValidError
from datetime import datetime
from sqlalchemy.exc import IntegrityError, OperationalError
from flask_wtf.file import FileField
from werkzeug.utils import secure_filename
import uuid as uuid
import os

app = Flask(__name__)
bcrypt = Bcrypt(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_BINDS'] = {'inventory' : 'sqlite:///data.db',
                                  'rewards' : 'sqlite:///rshop.db'}
app.config['SECRET_KEY'] = 'thisisasecretkey'
app.config['RECAPTCHA_PUBLIC_KEY'] = "6LdqlXUkAAAAAHVX8Ax_YuatX0XWzLxvj_tnxWx7"
app.config['RECAPTCHA_PRIVATE_KEY'] = "6LdqlXUkAAAAAM42XqKH27dw9WQu1kdsM8wF-jgF"
UPLOAD_FOLDER = 'static/uploads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(100), unique=True)
    points = db.Column(db.Integer)
    ordered = db.Column(db.String)
    address = db.Column(db.String)
    contact = db.Column(db.String)
    rewards = db.Column(db.String)
    rewardsaddress = db.Column(db.String)

    def __init__(self, username, password, email=None, points=0, ordered=None, address=None, contact=None, rewards=None, rewardsaddress=None):
        self.username = username
        self.password = password
        self.email = email
        self.points = points
        self.ordered = ordered
        self.address = address
        self.contact = contact
        self.rewards = rewards
        self.rewardsaddress = rewardsaddress

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.points}', '{self.ordered}', '{self.address}', '{self.contact}', '{self.rewards}', '{self.rewardsaddress}')"

class RegisterForm(FlaskForm):
    username = StringField(validators=[
                           InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})

    password = PasswordField(validators=[
                             InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})

    recaptcha = RecaptchaField()

    submit = SubmitField('Register')

    def validate_username(self, username):
        existing_user_username = User.query.filter_by(
            username=username.data).first()
        if existing_user_username:
            raise ValidationError(
                'That username has unfortunately been taken :( Please choose a different username.')

class LoginForm(FlaskForm):
    username = StringField(validators=[
                           InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})

    password = PasswordField(validators=[
                             InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})

    recaptcha = RecaptchaField()

    submit = SubmitField('Login')

class ChangePass(FlaskForm):
    newpass = PasswordField(validators=[
                             InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "New Password"})

    submit = SubmitField('Change Password')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('loginhome'))
    form = RegisterForm()

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        new_user = User(username=form.username.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in!', 'success')
        return redirect(url_for('login'))

    return render_template('register.html', form=form)

@app.route('/login', methods=['POST', 'GET'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('loginhome'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                flash("Login Successful!", 'success')
                return redirect(url_for('loginhome'))
            else:
                flash("Wrong Username/Password", 'danger')
                return render_template('login.html', form=form)
        else:
            flash("Wrong Username/Password", 'danger')
            return render_template('login.html', form=form)
    return render_template('login.html', form=form)


@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    if request.method == "POST":
        #if request.form["email"] != "":
        email = request.form["email"]
        #if request.form["delete"] != "":
            #delete = request.form["delete"]
        #email validator
        if email == current_user.email:
            flash("Changing to the same email doesn't change anything :P", 'info')
        else:
            if email != "":
                try:
                    validate_email(email)
                    current_user.email = email
                    flash("Email Successfully Updated!", 'success')
                    db.session.commit()
                except EmailNotValidError:
                    flash("Please enter a valid email", 'danger')
            elif email == "":
                flash("Please enter something", 'danger')
            #if delete != "":
                #print("a")

    return render_template('dashboard.html')


@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    flash('You have successfully logged out!', 'success')
    return redirect(url_for('login'))

@app.route('/error')
def error():
    return render_template('error.html')

@app.route('/users')
def users():
    return render_template('users.html', values=User.query.all())

@app.route('/delete', methods=['GET', 'POST'])
@login_required
def delete():
    if current_user.email is not None:
        if request.method == "POST":
            delete = request.form["delete"]
            if delete == "DELETE":
                current_user.email = None
                flash("Email Successfully Deleted", 'success')
                db.session.commit()
                return redirect(url_for('dashboard'))
            else:
                flash("Error, check if DELETE is in full caps and spelt correctly.", 'danger')
    else:
        flash("There is no email to delete", 'danger')
        return redirect(url_for('dashboard'))
    return render_template('delete.html')

@app.route('/change', methods=['GET', 'POST'])
@login_required
def change():
    form = ChangePass()

    if form.validate_on_submit():
        if bcrypt.check_password_hash(current_user.password, form.newpass.data):
            flash("Please enter a different password", 'danger')
            return render_template('change.html', form=form)
        else:
            hashed_newpassword = bcrypt.generate_password_hash(form.newpass.data)
            current_user.password = hashed_newpassword
            flash("Password Successfully Updated! Please Re-Login", 'success')
            db.session.commit()
            logout_user()
            return redirect(url_for('login'))
    return render_template('change.html', form=form)

@app.route('/admin', methods=['GET','POST'])
@login_required
def admin():
    id = current_user.id
    if id == 1:
        return render_template('admin.html', values=User.query.all())
    else:
        flash("Sorry, only admins are allowed access here!", 'info')
        return redirect(url_for('loginhome'))

@app.route('/profileexample')
def profileexample():
    return render_template("profileexample.html")

@app.route('/home')
def loginhome():
    return render_template("loginhome.html")

class Inventory(db.Model):
    __bind_key__ = 'inventory'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    price = db.Column(db.Integer, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    category = db.Column(db.String(100), nullable=False)
    date_added = db.Column(db.DateTime, default=datetime.now())
    rewardpic = db.Column(db.String(), nullable=False)

    def __repr__(self):
        return '<Name %r>' % self.name

# Create a form class
class inventoryform(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    price = IntegerField('Price', validators=[DataRequired()])
    quantity = IntegerField('Quantity', validators=[DataRequired()])
    category = StringField('Category', validators=[DataRequired()])
    rewardpic = FileField("Reward Image")
    submit = SubmitField('Submit', validators=[DataRequired()])


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

class Rewards(db.Model):
    __bind_key__ = 'rewards'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    price = db.Column(db.Integer, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    category = db.Column(db.String(100), nullable=False)
    date_added = db.Column(db.DateTime, default=datetime.now())
    rewardpic = db.Column(db.String(), nullable=False)

    def __repr__(self):
        return '<Name %r>' % self.name

# Create a form class
class rewardform(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    price = IntegerField('Price', validators=[DataRequired()])
    quantity = IntegerField('Quantity', validators=[DataRequired()])
    category = StringField('Category', validators=[DataRequired()])
    rewardpic = FileField("Reward Image")
    submit = SubmitField('Submit', validators=[DataRequired()])

@app.route('/manage_rewards')
def rmanage():
    ourrewards = Rewards.query.order_by(Rewards.date_added)
    return render_template('rmanage.html', ourrewards=ourrewards)


@app.route('/rewards_shop')
@login_required
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

            db.session.add(reward)
            db.session.commit()
            name = form.name.data
            form = rewardform(formdata=None)
            flash('Reward Added Successfully', 'success')
            return render_template('addr.html', name=name, form=form)

        except IntegrityError:
            db.session.rollback()
            flash('Error! Name has already been used', 'danger')
            return render_template('addr.html', name=name, form=form)
        except AttributeError:
            db.session.rollback()
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
            db.session.commit()
            flash('Updated Successfully', 'success')
            return render_template('updater.html', form=form, update=update)

        except IntegrityError:
            db.session.rollback()
            flash('Error! Name has already been used', 'danger')
            return render_template('updater.html', form=form, update=update)
        except AttributeError:
            db.session.rollback()
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
        db.session.delete(delete)
        db.session.commit()
        flash('Reward Deleted Successfully', 'success')
        ourrewards = Rewards.query.order_by(Rewards.date_added)
        return render_template('rmanage.html', name=name, form=form, ourrewards=ourrewards)

    except:
        flash('Error! There was a problem deleting the reward''danger')
        return render_template('rmanage.html', name=name, form=form, ourrewards=ourrewards)

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
        flash("Payment Successful!", 'success')
        return redirect(url_for('namtest'))
    return render_template("name.html" , form = form)

@app.route('/namtest')
def namtest():

    return render_template('namtest.html')


with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
