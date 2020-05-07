import json
from datetime import datetime
from hashlib import sha224
from uuid import uuid4

from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from flask_babel import gettext

from ..models import db, Bookmark, Tag, BookmarkTag, Page
from .auth import login_required
from .tags import get_tag


manage_bp = Blueprint('manage', __name__, url_prefix='/manage')


@manage_bp.route('/')
@login_required
def index():
    return render_template('manage/index.html')


def parse_bookmark(data, bookmark_list=[]):
    if 'children' in data:
        for item in data['children']:
            bookmark_list.append({
                'title': item.get('title', 'No title'),
                'uri': item.get('uri', 'None'),
                'dateAdded': item.get('dateAdded', 'None'),
                'iconuri': item.get('iconuri', 'None'),
                'lastModified': item.get('lastModified', 'None'),
                'tags': item.get('tags', 'None'),
                'typeCode': item.get('typeCode', 0),
            })
            parse_bookmark(item, bookmark_list)
    return bookmark_list


def insert_db(data):
    # for Firefox's backup html
    conn = db.session()
    conn.autoflush = False

    remote_addr = request.remote_addr
    count = 0
    ng = 0

    for entry in data:
        print(entry)
        if entry['typeCode'] != 1:
            continue
        if entry['title'] == 'No title':
            ng = ng + 1
            continue
        if entry['uri'] == 'None':
            print(f"no uri: {entry['title']}")
            ng = ng + 1
            continue

        urihash = sha224(entry['uri'].encode('utf-8')).hexdigest()

        q = conn.query(Bookmark).filter(
            Bookmark.urihash == urihash).first()
        if q is not None:
            # already exist
            print(f"dup: {entry['title']}")
            ng = ng + 1
            continue

        if entry['dateAdded'] == 'None':
            dateAdded = datetime.now()
        else:
            dateAdded = datetime.fromtimestamp(int(entry['dateAdded'] / 1000000))

        if entry['lastModified'] == 'None':
            lastModified = datetime.now()
        else:
            lastModified = datetime.fromtimestamp(
                int(entry['lastModified'] / 1000000))

        tags = entry['tags'].split(",") if entry['tags'] != 'None' else []

        bookmark = Bookmark(
            user_id=g.user.id,
            remote_address=remote_addr,
            title=entry['title'],
            uri=entry['uri'],
            urihash=sha224(entry['uri'].encode('utf-8')).hexdigest(),
            created_at=dateAdded,
            updated_at=lastModified
        )

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
        count = count + 1

    conn.commit()

    return (count, ng)


@manage_bp.route('/import', methods=('GET', 'POST'))
@login_required
def importbookmark():
    bookmark_list = []
    result = None

    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash(gettext('No file part'))
            return redirect(request.url)
        file = request.files['file']
        data = json.loads(file.read())
        bookmark_list = parse_bookmark(data)
        result = insert_db(bookmark_list)

        # TODO: async
        # updated_pages = update_page(g.user.id)
        # updated_pages = get_screenshots(updated_pages)

    return render_template('manage/import.html', result=result)


@manage_bp.route('/update', methods=('GET', 'POST'))
@login_required
def update():
    conn = db.session()
    pages = conn.query(Page).join(Bookmark).filter(Page.status == 0).all()
    # get_screenshots(pages)
    return render_template('manage/index.html')
