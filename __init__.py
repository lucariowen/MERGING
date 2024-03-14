from flask import Flask, render_template, url_for, redirect, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from flask_bcrypt import Bcrypt
from email_validator import validate_email, EmailNotValidError

app = Flask(__name__)
bcrypt = Bcrypt(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'thisisasecretkey'
app.config['RECAPTCHA_PUBLIC_KEY'] = "6LdqlXUkAAAAAHVX8Ax_YuatX0XWzLxvj_tnxWx7"
app.config['RECAPTCHA_PRIVATE_KEY'] = "6LdqlXUkAAAAAM42XqKH27dw9WQu1kdsM8wF-jgF"
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

    def __init__(self, username, password, email=None, points=0, ordered=None, address=None, contact=None):
        self.username = username
        self.password = password
        self.email = email
        self.points = points
        self.ordered = ordered
        self.address = address
        self.contact = contact

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.points}', '{self.ordered}', '{self.address}', '{self.contact}')"

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
    username = StringField()#validators=[
                           #InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})

    password = PasswordField()#validators=[
                             #InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})

    recaptcha = RecaptchaField()

    submit = SubmitField('Login')

class ChangePass(FlaskForm):
    newpass = PasswordField(validators=[
                             InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "New Password"})

    submit = SubmitField('Change Password')

@app.route('/')
def home():
    return render_template('home.html')

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
        return redirect(url_for('dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                flash("Login Successful!", 'success')
                return redirect(url_for('dashboard'))
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
                existingemail = User.query.filter_by(
                email=email).first()
                if existingemail:
                    flash("Duplicate Email", 'danger')
                else:
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

# dogtest


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

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=False)
