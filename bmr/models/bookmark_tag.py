from .base import db


class BookmarkTag(db.Model):
    __tablename__ = 'bookmarks_tags'

    tag_id = db.Column('tag_id', db.Integer, db.ForeignKey(
        'tags.id'), primary_key=True)
    bookmark_id = db.Column(db.Integer, db.ForeignKey(
        'bookmarks.id'), primary_key=True)

    bookmark = db.relationship("Bookmark", back_populates="tag")
    tag = db.relationship("Tag", back_populates="bookmark")
