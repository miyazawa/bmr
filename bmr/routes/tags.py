from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)

from ..models import db, Bookmark, User, Page, Tag, BookmarkTag
from .auth import login_required


tag_bp = Blueprint('tag', __name__)


def get_tag(conn, tag):
    return conn.query(Tag).join(User, Tag.user_id == User.id).filter(
        User.id == g.user.id).filter(Tag.name == tag).first()


@tag_bp.route('/tag')
def index():
    session = db.session()
    tags = session.query(Tag).group_by(Tag.name).all()

    return render_template('tag/index.html', tags=tags)


@tag_bp.route('/tag/<string:tag>')
def tag_view(tag):
    session = db.session()
    bookmarks = session.query(BookmarkTag).join(Tag).join(Bookmark).filter(Tag.name == tag).all()
    return render_template('tag/bookmark.html', tag=tag, bookmarks=bookmarks)
