from hashlib import sha224
from urllib.parse import urlparse

from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, abort
)
from flask_paginate import Pagination, get_page_parameter
from flask_babel import gettext

from ..models import db, Bookmark, User, Page, Tag, BookmarkTag
from .auth import login_required
from .tags import get_tag
# from ._forms import search_form


bookmark_bp = Blueprint('bookmark', __name__)


@bookmark_bp.route('/', methods=('GET', 'POST'))
# @login_required
def index():
    conn = db.session()

    if request.method == 'GET':
        bookmarks = conn.query(Bookmark).join(
            User, Bookmark.user_id == User.id).order_by(Bookmark.id).all()

    if request.method == 'POST':
        query = request.form['search']
        bookmarks = conn.query(Bookmark).join(
            User, Bookmark.user_id == User.id).filter(Bookmark.title.like(f"%{query}%"), Bookmark.private == 0).all()
        from sqlalchemy.dialects import sqlite
        print(conn.query(Bookmark).join(
            User, Bookmark.user_id == User.id).filter(Bookmark.title.like(f"%{query}%")).statement.compile(dialect=sqlite.dialect()))

    page = request.args.get(get_page_parameter(), type=int, default=1)
    res = bookmarks[(page - 1) * 10: page * 10]
    pagination = Pagination(page=page, total=len(bookmarks), per_page=10, css_framework='bootstrap4')

    return render_template('bookmark/index.html', bookmarks=res, pagination=pagination)


@bookmark_bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        uri = request.form['uri']
        description = request.form['description']
        tags = request.form['tags'].split(" ")
        error = None

        if not title:
            error = gettext('Title is required.')

        if not url_validator(uri):
            error = gettext('Invalid URL.')

        if error is not None:
            flash(error)
        else:
            bookmark = Bookmark(
                user_id=g.user.id,
                remote_address=request.remote_addr,
                title=title,
                uri=uri,
                description=description,
                urihash=get_urihash(uri)
            )

            conn = db.session()

            for t in tags:
                tag = get_tag(conn, t)
                if tag is None:
                    # new tag
                    tag = Tag(name=t, user_id=g.user.id)
                    conn.add(tag)

                bookmark_tag = BookmarkTag()
                bookmark_tag.tag = tag
                bookmark.tag.append(bookmark_tag)

            conn.add(bookmark)

            conn.commit()
            return redirect(url_for('bookmark.index'))

    return render_template('bookmark/new.html')


@bookmark_bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    bookmark = get_bookmark(id)
    tags_before = [t.tag.name for t in bookmark.tag]

    if request.method == 'POST':
        title = request.form['title']
        uri = request.form['uri']
        description = request.form['description']
        tags = request.form['tags'].splitlines()

        error = None

        if not title:
            error = gettext('Title is required.')

        if error is not None:
            flash(error)
        else:
            update_bookmark(bookmark, title, uri, description, tags_before, tags)
            return redirect(url_for('bookmark.index'))

    return render_template('bookmark/update.html', bookmark=bookmark)


@bookmark_bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_bookmark(id)
    conn = db.session()
    conn.query(Bookmark).filter(Bookmark.id == id).delete()
    conn.commit()
    return redirect(url_for('bookmark.index'))


def url_validator(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except AttributeError:
        return False


def get_urihash(uri):
    return sha224(uri.encode('utf-8')).hexdigest()


def get_bookmark(id, check_author=True):
    conn = db.session()
    bookmark_user = conn.query(Bookmark, User).join(
        Bookmark, Bookmark.user_id == User.id).filter(Bookmark.id == id).first()

    if bookmark_user is None:
        abort(404, "Bookmark id {0} doesn't exist.".format(id))

    if check_author and bookmark_user.User.id != g.user.id:
        abort(403)

    return bookmark_user.Bookmark


def update_bookmark(bookmark, title, uri, description, tags_before, tags):
    conn = db.session()
    query = conn.query(Bookmark).filter(Bookmark.id == id)
    bookmark = query.first()

    query.update({
        "title": title,
        "uri": uri,
        "description": description
    })

    # tag mentenance: delete
    diff = set(tags_before) - set(tags)
    if len(list(diff)) > 0:
        # delete
        for t in diff:
            for tag in bookmark.tag:
                if tag.name == t:
                    bookmark.tag.remove(tag)

    # tag mentenance: add
    if tags != [""] and (set(tags) - set(tags_before)):
        # add
        print("need add")
        for t in tags:
            tag = get_tag(conn, t)

            if tag is None:
                tag = Tag(name=t, user_id=g.user.id)
                conn.add(tag)
            bookmark_tag = BookmarkTag()
            bookmark_tag.tag = tag
            bookmark.tag.append(bookmark_tag)

    conn.commit()
