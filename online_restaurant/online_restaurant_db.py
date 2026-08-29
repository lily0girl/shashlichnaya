from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)


class Menu(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    photo = db.Column(db.String(300))
    description = db.Column(db.String(300))
    ingredients = db.Column(db.String(300))
    price = db.Column(db.Float, nullable=False)
    weight = db.Column(db.Integer)
    active = db.Column(db.Boolean, default=True)


class Orders(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    dish_name = db.Column(db.String(100))
    quantity = db.Column(db.Integer)
    total_price = db.Column(db.Float)


class Reservation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    date = db.Column(db.String(20))
    time = db.Column(db.String(10))
    guests = db.Column(db.Integer)