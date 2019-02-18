from flask_sqlalchemy import SQLAlchemy
import sqlalchemy
from flask import jsonify, make_response, request
from ImgManager import app, db, bcrypt
from ImgManager.models import row2dict, Person, Album, Picture
from flask_login import login_user, current_user, logout_user, login_required


@app.errorhandler(404)
def page_not_found(e):
    return make_response(jsonify({"code": 404, "msg": "404: Not Found"}), 404)


@app.route('/')
def soen487_a1():
    return jsonify({"title": "SOEN487 Assignment 1",
                    "student": {"id": "40035704", "name": "Joel Dusablon Senécal"}})


@app.route("/person")
def get_all_person():
    person_list = Person.query.all()
    return jsonify([row2dict(person) for person in person_list])


@app.route("/person/<person_id>")
def get_person(person_id):
    # id is a primary key, so we'll have max 1 result row
    person = Person.query.filter_by(id=person_id).first()
    if person:
        return jsonify(row2dict(person))
    else:
        return make_response(jsonify({"code": 404, "msg": "Cannot find this person id."}), 404)


@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return make_response(jsonify({"code": 403, "msg": "You are logged in please log out to register"}), 403)

    # getting request info
    name = request.form.get("name")
    pw = request.form.get("password")

    # check info for errors
    if not name or not pw:
        return make_response(jsonify({"code": 403, "msg": "Cannot put person. Missing mandatory fields."}), 403)

    if Person.query.filter_by(name=name).first():
        return make_response(jsonify({"code": 403, "msg": "Cannot put person. Name is already taken."}), 403)

    # if valid, add to db
    hpw = bcrypt.generate_password_hash(pw).decode('utf-8')
    user = Person(name=name, password=hpw)
    db.session.add(user)
    db.session.commit()

    return jsonify({"code": 200, "msg": "success"})


@app.route("/login", methods=['GET', 'POST'])
def login():
    # checking if already logged in
    if current_user.is_authenticated:
        return make_response(jsonify({"code": 403, "msg": "Already logged in"}), 403)

    name = request.form.get("name")
    pw = request.form.get("password")

    # data field check
    if not name or not pw:
        return make_response(jsonify({"code": 403, "msg": "Cannot Login, invalid fields"}), 403)

    user = Person.query.filter_by(name=name).first()

    # existing user check
    if not user:
        return make_response(jsonify({"code": 403, "msg": "Cannot login, invalid account"}), 403)

    # password and username combination check
    if user and bcrypt.check_password_hash(user.password, pw):
        user.id = str(getattr(user, 'id'))
        login_user(user)
        return jsonify({"code": 200, "msg": "success"})

    else:
        return make_response(jsonify({"code": 403, "msg": "Cannot login, invalid password"}), 403)


@app.route("/logout", methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return jsonify({"code": 200, "msg": "success"})


@app.route("/album",  methods={'GET'})
def get_all_album():
    album_list = Album.query.all()
    return jsonify([row2dict(album) for album in album_list])


@app.route("/pictures", methods={'GET'})
def get_all_pictures():
    picture_list = Picture.query.all()
    return jsonify([row2dict(picture) for picture in picture_list])


@app.route("/createAlbum", methods={'POST'})
@login_required
def create_new_Album():
    # getting request info
    name = request.form.get("name")
    person_id = current_user.id

    if not name or not person_id:
        return make_response(jsonify({"code": 403, "msg": "Cannot put person. Missing mandatory fields."}), 403)

    if Album.query.filter_by(name=name).first():
        return make_response(jsonify({"code": 403, "msg": "Cannot create a second album with that name."}), 403)

    # if valid, add to db
    album = Album(name=name, person_id=person_id)
    db.session.add(album)
    db.session.commit()

    return jsonify({"code": 200, "msg": "success"})


@app.route("/test")
def dbtest():
    name = 'paul'
    pw = "manafort"
    hpw = bcrypt.generate_password_hash(pw).decode('utf-8')
    user = Person(name=name, password=hpw)
    db.session.add(user)
    db.session.commit()
    return jsonify({"code": 200, "msg": "success"})