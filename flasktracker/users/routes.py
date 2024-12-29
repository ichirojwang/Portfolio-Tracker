from flask import Blueprint, url_for, render_template, redirect, flash, request
from flask_login import login_user, login_required, current_user, logout_user

from flasktracker import db, bcrypt
from flasktracker.users.forms import SignUpForm, LogInForm, UpdateAccountForm, UpdateYearEligibleForm
from flasktracker.users.models import User

users = Blueprint('users', __name__)


@users.route('/signup', methods=["GET", "POST"])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('users.home'))

    form = SignUpForm()
    if form.validate_on_submit():
        # hashing password with bcrypt
        hashed_password: str = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        new_user: User = User(form.name.data, form.email.data, hashed_password)

        # adding to database
        db.session.add(new_user)
        db.session.commit()

        flash(f"Account created for {form.name.data}.", "success")
        return redirect(url_for('users.login'))

    return render_template("signup.html", form=form)


@users.route('/login', methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('users.home'))

    form = LogInForm()
    if form.validate_on_submit():
        user: User = User.query.filter_by(email=form.email.data).first()
        # if user found, verify with hashed password
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            # if the user came from a login required page
            next_page = request.args.get('next', url_for('users.home'))
            return redirect(next_page)
        else:
            flash("Invalid credentials.", "warning")

    return render_template("login.html", form=form)


@users.route('/')
def send_home():
    return redirect(url_for('users.home'))


@users.route('/home')
@login_required
def home():
    return render_template("home.html")


@users.route('/profile', methods=["GET", "POST"])
@login_required
def profile():
    form = UpdateAccountForm()
    year_form = UpdateYearEligibleForm()
    if form.validate_on_submit():
        if current_user.name != form.name.data or current_user.email != form.email.data:
            current_user.name = form.name.data
            current_user.email = form.email.data
            db.session.commit()
            flash("Account successfully updated!", "success")
        return redirect(url_for('users.profile'))
    return render_template("profile.html", form=form, year_form=year_form)


@users.route('/profile/update/year', methods=["POST"])
@login_required
def update_profile_year():
    year_form = UpdateYearEligibleForm()
    if year_form.validate_on_submit():
        if year_form.year.data < 2009 or year_form.year.data > 2100:
            flash("Invalid year.", "warning")
        elif current_user.year_eligible != year_form.year.data:
            current_user.year_eligible = year_form.year.data
            db.session.commit()
            flash("Year has been updated!", "success")
    return redirect(url_for('users.profile'))


@users.route('/settings')
@login_required
def settings():
    return render_template("settings.html")


@users.route('/logout')
def logout():
    logout_user()
    return redirect(url_for("main.welcome"))
