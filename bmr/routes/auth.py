import functools
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash
from flask_babel import gettext

from ..models import db, User

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


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
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        # db = get_db()
        error = None

        conn = db.session()
        user = conn.query(User).filter(User.username == username).all()

        if not username:
            error = gettext('Username is required.')
        elif not password:
            error = gettext('Password is required.')
        elif len(user) != 0:
            error = 'User {} is already registered.'.format(username)

        if error is None:
            new_user = User(username=username, password=generate_password_hash(
                password), email=email)
            conn.add(new_user)
            conn.commit()
            return redirect(url_for('auth.login'))

        flash(error)

    return render_template('auth/register.html')


@auth_bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        error = None

        conn = db.session()
        user = conn.query(User).filter(User.username == username).first()

        if user is None or not check_password_hash(user.password, password):
            error = gettext('Incorrect username or password.')

        if error is None:
            session.clear()
            session['user_id'] = user.id
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html')


@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view
