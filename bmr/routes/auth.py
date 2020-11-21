from datetime import timedelta
import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash
from flask_babel import gettext, lazy_gettext
from wtforms import Form, BooleanField, StringField, PasswordField, validators
from wtforms.csrf.session import SessionCSRF

from ..models import db, User

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


class RegistrationForm(Form):
    username = StringField(
        label=lazy_gettext('Username'),
        validators=[
            validators.DataRequired(),
            validators.Length(min=4, max=25),
            validators.Regexp('^[A-Za-z0-9-_.]+$')
        ])
    email = StringField(
        label=lazy_gettext('Email Address'),
        validators=[
            validators.DataRequired(),
            validators.Length(min=6, max=35),
            validators.Email()
        ])
    password = PasswordField(
        label=lazy_gettext('New Password'),
        validators=[
            validators.DataRequired(),
            validators.EqualTo('confirm', message=lazy_gettext('Passwords must match')),
            validators.Regexp('^[a-zA-Z0-9!#$%&()*+,.:;=?@\[\]^_{}-]+$')
        ])
    confirm = PasswordField(label=lazy_gettext('Repeat Password'))
    accept_tos = BooleanField(
        label=lazy_gettext('I accept the TOS'),
        validators=[validators.DataRequired()])


class LoginForm(Form):
    username = StringField(
        label=lazy_gettext('Username'),
        validators=[validators.Length(min=4, max=25)],
        render_kw={"placeholder": lazy_gettext('Username')})
    password = PasswordField(
        label=lazy_gettext('Password'),
        validators=[validators.DataRequired()],
        render_kw={"placeholder": lazy_gettext('Password')})


@auth_bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        conn = db.session()
        g.user = conn.query(User).filter(User.id == user_id).first()


@auth_bp.route('/register', methods=('GET', 'POST'))
def register():
    form = RegistrationForm(request.form)

    if request.method == 'POST' and form.validate():
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        error = None

        conn = db.session()
        user = conn.query(User).filter(User.username == username).all()

        if not username:
            error = gettext('Username is required.')
        elif not password:
            error = gettext('Password is required.')
        elif len(user) != 0:
            error = gettext('User %(name)s is already registered.', name=username)

        if error is None:
            new_user = User(username=username, password=generate_password_hash(
                password), email=email)
            conn.add(new_user)
            conn.commit()
            return redirect(url_for('auth.login'))

        flash(error)

    return render_template('auth/register.html', form=form)


@auth_bp.route('/login', methods=('GET', 'POST'))
def login():
    form = LoginForm(request.form)

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        error = None

        if not username:
            error = gettext('Username is required.')

        conn = db.session()
        user = conn.query(User).filter(User.username == username).first()

        if user is None or not check_password_hash(user.password, password):
            error = gettext('Incorrect username or password.')

        if error is None:
            session.clear()
            session['user_id'] = user.id
            return redirect(url_for('bookmark.index'))

        flash(error)

    return render_template('auth/login.html', form=form)


@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('bookmark.index'))


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view
