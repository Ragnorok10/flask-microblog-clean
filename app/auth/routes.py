#This serves as kind of a central (high way exchange) it routes certain pages to other
#usuall html to here then to other logic scripts, it handles data flow and generating certain
#attributes on an html page

#THIS IS AUTH RELATED ROUTES

#Imports
from flask import render_template, redirect, url_for, flash, request
from urllib.parse import urlsplit
from flask_login import login_user, logout_user, current_user
from flask_babel import _
import sqlalchemy as sa
from app import db
from app.auth import bp
from app.auth.forms import LoginForm, RegistrationForm, \
    ResetPasswordRequestForm, ResetPasswordForm
from app.models import User
from app.auth.email import send_password_reset_email

#routes

#Login route - this is called a view function because it's a function that passes it into the html script where it is then displayed and VIEWABLE
@bp.route('/login', methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(User).where(User.username == form.username.data))
        if user is None or not user.check_password(form.password.data):
            flash(_('Invalid username or password'))
            return redirect(url_for('auth.login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or urlsplit(next_page).netloc != '':
            next_page = url_for('main.index')
        return redirect(next_page) #this line if login authenticated redirects to the index (home) page
    return render_template('auth/login.html', title=_('Sign In'), form=form)

#Logout route - this will be used for users to logout
@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))

#Registeration Route - will be used for users to Register an account
@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash(_('Congratulations, you are now a registered user!'))
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', title=_('Register'), form=form)

#Reset Password Request Route: - this route will handle the request part, up until the user enters their email in which then the result will send them an email
@bp.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(User).where(User.email == form.email.data)) #this seaches the DB to see if the inputed user email matches an existing one in the DB to submit
        if user:
            send_password_reset_email(user) #this will send the e-mail to the user if previous step authenticated
        flash(_('Check your email for the instructions to reset your password'))
        return redirect(url_for('auth.login')) # Will redirect user to login page because while they reset their password
    return render_template('auth/reset_password_request.html',
                           title=_('Reset Password'), form=form)

# Reset Password Link Route - this is for once the user clicks on the link within the email, it will open an html page as well as direct the data appropriately
@bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.index')) #if user is already signed in, they are sent back home
    user = User.verify_reset_password_token(token) #imported from User class in Models.py
    if not user:
        return redirect(url_for('main.index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data) #this takes the new password that was inputed on the html page
        db.session.commit() #uploads new password database
        flash(_('Your password has been reset.'))
        return redirect(url_for('auth.login')) #returns user to login screen.
    return render_template('auth/reset_password.html', form=form)


