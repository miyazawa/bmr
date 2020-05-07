from .base import db, init_db
from .bookmark import Bookmark
from .bookmark_tag import BookmarkTag
from .tag import Tag
from .page import Page
from .user import User


def init_app(app):
    db.init_app(app)
    init_db(app)
