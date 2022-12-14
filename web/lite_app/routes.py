from lite_app import app
from flask import render_template, redirect, url_for, flash
from flask_login import login_user, logout_user
from lite_app.models import Users
from lite_app.forms import RegisterForm, LoginForm
from lite_app import db
from datetime import datetime
import requests
import json


@app.route("/", methods=['GET'])
def home_page():
    users = Users.query.all()
    date_r = datetime.now().strftime("%Y%m%d")
    usd = 0
    eur = 0
    try:
        value = requests.get(
            f"https://bank.gov.ua/NBUStatService/v1/statdirectory/exchange?json&date={date_r}")
        if value.status_code == 200:
            for rate in json.loads(value.text):
                if rate.get('cc') == 'USD':
                    usd = rate.get('rate')
                if rate.get('cc') == 'EUR':
                    eur = rate.get('rate')
    except:
        flash("Can't connect to NBU", category='info')
    return render_template('home.html', users=users, usd=usd, eur=eur)


@app.route('/register', methods=['GET', 'POST'])
def register_page():
    form = RegisterForm()
    if form.validate_on_submit():
        user_to_create = Users(username=form.username.data,
                               email_address=form.email_address.data,
                               password_hash=form.password1.data)
        db.session.add(user_to_create)
        db.session.commit()
        return redirect(url_for('login_page'))
    if form.errors != {}:
        for err_msg in form.errors.values():
            flash(err_msg[0], category='danger')
    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login_page():
    form = LoginForm()
    if form.validate_on_submit():
        attempted_user = Users.query.filter_by(username=form.username.data).first()
        if attempted_user and attempted_user.check_password_correction(
                attempted_password=form.password.data):
            login_user(attempted_user)
            flash(f"You are logged in as: {attempted_user.username}", category='success')
            return redirect(url_for('home_page'))
        else:
            flash(f"Not correct login or password", category='danger')
    return render_template('login.html', form=form)


@app.route('/logout')
def logout_page():
    logout_user()
    flash("You have been logged out", category='info')
    return redirect(url_for('home_page'))