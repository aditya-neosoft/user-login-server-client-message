import zmq
from flask import render_template,Flask,flash, request, redirect,url_for, json
from app import app,db
from app.forms import LoginForm, RegistrationForm
from flask_login import current_user, login_user,logout_user
from app.models import User


context = zmq.Context()
socket = context.socket(zmq.SUB)

@app.route('/')
@app.route('/index')
def index():
    socket.setsockopt(zmq.SUBSCRIBE, b"")
    socket.connect('tcp://localhost:5555')
    user = {'username': current_user.username if current_user.is_authenticated else ''}
    return render_template('index.html', title='Home', user=user,)



# @app.route('/login')
# def login():
#     form = LoginForm()
#     return render_template('login.html', title='Sign In', form=form)



@app.route('/login', methods=['GET', 'POST'])
def login():

    if current_user.is_authenticated:

        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for('index'))
    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)



@app.route('/message')
def message():
    message = socket.recv()

    response = app.response_class(
        response=json.dumps({'message': message.decode("utf-8")}),
        status=200,
        mimetype='application/json'
    )
    return response