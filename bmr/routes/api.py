from urllib.parse import unquote

from flask import (
    Blueprint, g, redirect, request, url_for, jsonify, session
)
from werkzeug.security import check_password_hash

from ..models import db, Bookmark, User
from .bookmarks import get_urihash

api_bp = Blueprint('api', __name__)


@api_bp.route('/api/test', methods=('POST',))
# @login_required
def test():
    if request.headers['Content-Type'] != 'application/json; charset=utf-8':
        print(request.headers['Content-Type'])
        return jsonify(res='Invalid header.'), 400

    error = None

    if request.method == 'POST':
        data = request.json
        uri = unquote(data['uri'])
        title = data['title']
        username = data['user']
        password = data['password']

        conn = db.session()
        user = conn.query(User).filter(User.username == username).first()

        if user is None:
            error = 'Authentication failed.'
        elif not check_password_hash(user.password, password):
            error = 'Authentication failed.'

        if error is None:
            session.clear()
            session['user_id'] = user.id

            bookmark = Bookmark(
                user_id=user.id,
                title=title,
                uri=uri,
                urihash=get_urihash(uri)
            )
            conn = db.session()
            conn.add(bookmark)
            conn.commit()
        else:
            return jsonify(message=error), 400

    return jsonify({"message": "ok"})
