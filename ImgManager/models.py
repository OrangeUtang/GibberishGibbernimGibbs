from ImgManager import db, login_manager
from flask_login import UserMixin


def row2dict(row):
    return {c.name: str(getattr(row, c.name)) for c in row.__table__.columns if c.name is not "password"}


@login_manager.user_loader
def load_user(user_id):
    return Person.query.get(int(user_id))


class Person(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text(), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    albums = db.relationship('Album', backref='owner', lazy=True)

    def __repr__(self):
        return "<Person {}: {}>".format(self.id, self.name)


class Album(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=False, nullable=False)
    person_id = db.Column(db.Integer, db.ForeignKey('person.id'), nullable=False)
    pictures = db.relationship('Picture', backref='album', lazy=True)

    def __repr__(self):
        return "<Album {}: {}, {}>".format(self.id, self.name, self.person_id)


class Picture(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True, nullable=False)
    album_id = db.Column(db.Integer, db.ForeignKey('album.id'), nullable=False)
    path = db.Column(db.String(20), nullable=False, default='default.jpg')

    def __repr__(self):
        return "<Album {}: {}, {}, {}>".format(self.id, self.name, self.album_id, self.path)
