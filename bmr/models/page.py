from datetime import datetime
from .base import db


class Page(db.Model):
    __tablename__ = 'pages'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    uuid = db.Column(db.String(36), default='')
    text = db.Column(db.String(1023))
    status = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    updated_at = db.Column(db.DateTime, nullable=False,
                           default=datetime.now, onupdate=datetime.now)

    # user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    bookmark_id = db.Column(db.Integer, db.ForeignKey('bookmarks.id'), nullable=False)
    bookmark_ = db.relationship('Bookmark', back_populates="page")