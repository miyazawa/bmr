from datetime import datetime
from .base import db


class Bookmark(db.Model):
    __tablename__ = 'bookmarks'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, nullable=False)
    remote_address = db.Column(db.String(64))
    title = db.Column(db.String(255), nullable=False)
    uri = db.Column(db.String(1023), nullable=False)
    urihash = db.Column(db.String(1023), nullable=False)
    description = db.Column(db.String(1023))
    status = db.Column(db.Integer, default=0)
    private = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    updated_at = db.Column(db.DateTime, nullable=False,
                           default=datetime.now, onupdate=datetime.now)

    tag = db.relationship("BookmarkTag")
    page = db.relationship('Page', uselist=False, backref='bookmark')
