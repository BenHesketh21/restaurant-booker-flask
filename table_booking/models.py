from . import db
from . import login_manager
from flask_login import UserMixin

class Tables(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    number_of_seats = db.Column(db.Integer, default=4)
    bookings = db.relationship('Bookings', backref="table_of_booking", lazy=True)

class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    staff = db.Column(db.Boolean, default=False)
    first_name = db.Column(db.String(30))
    last_name = db.Column(db.String(30))
    email = db.Column(db.String(30), unique=True)
    password = db.Column(db.String(200))
    bookings = db.relationship('Bookings', backref="customer", lazy=True)

class Bookings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    table_id = db.Column(db.Integer, db.ForeignKey('tables.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    time_of_booking = db.Column(db.DateTime)
    date_of_booking = db.Column(db.DateTime)


@login_manager.user_loader
def load_user(id):
    return Users.query.get(int(id))
