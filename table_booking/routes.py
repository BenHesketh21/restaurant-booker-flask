from . import app, db, bcrypt, api
from flask import redirect, url_for, request, jsonify
from flask_login import login_required, current_user, login_user, logout_user
from flask_restplus import Resource, fields
from .models import Tables, Users, Bookings
from .forms import NewTableForm, BookTableForm, LoginForm, RegistrationForm, UpdateAccountForm
import datetime

# Bookings

a_booking = api.model('Booking', {
    "table": fields.Integer('The Table'),
    "user": fields.Integer('The User'),
    "time": fields.String('The Time'),
    "date": fields.String('The Date')
})

a_booking_check = api.model('Booking Check', {
    "number_of_customers": fields.Integer("Number of Guests"),
    "time": fields.String('The Time'),
    "date": fields.String('The Date')
})

a_table = api.model('Table', {
    "id": fields.Integer('The Table Number'),
    "number_of_seats": fields.Integer('The Number of Seats')
})

a_customer = api.model('Customer', {
    "first_name": fields.String('First Name'),
    "last_name": fields.String('Last Name'),
    "email": fields.String('Email'),
    "password": fields.String('Password'),
    "staff": fields.Boolean("Staff Member?")
})

a_customer_without_pass = api.model('Customer Without Password', {
    "first_name": fields.String('First Name'),
    "last_name": fields.String('Last Name'),
    "email": fields.String('Email'),
    "staff": fields.Boolean("Staff Member?")
})

a_customer_auth = api.model('Customer Email', {
    "email": fields.String('Email'),
    "password": fields.String('Password')
})

a_customer_email = api.model('Customer Auth', {
    "email": fields.String('Email')
})

@api.route('/bookings')
class BookingsCrud(Resource):
    def get(self):
        bookings = Bookings.query.all()
        response = []
        for booking in bookings:
            booking_dict = dict(
                id=booking.id,
                time=booking.time_of_booking,
                date=booking.date_of_booking,
                table=booking.table_id,
                users=booking.user_id
            )
            response.append(booking_dict)
        return jsonify(response)

    @api.expect(a_booking)
    def post(self):
        new_booking = api.payload
        booking = Bookings(
            time_of_booking=datetime.datetime.strptime(new_booking['time'], "%H:%M:%S"),
            date_of_booking=datetime.datetime.strptime(new_booking['date'], "%d/%m/%Y"),
            table_id=new_booking['table'],
            user_id=new_booking['user']
        )
        db.session.add(booking)
        db.session.commit()
        response = dict(
                id=booking.id,
                time=booking.time_of_booking,
                date=booking.date_of_booking,
                table=booking.table_id,
                users=booking.user_id
        )
        return jsonify(response)

@api.route('/bookings/available')
class BookingsAvailable(Resource):
    @api.expect(a_booking_check)
    def post(self):
        requested = api.payload
        requested_time = datetime.datetime.strptime(requested['time'], "%H:%M:%S")
        requested_date = datetime.datetime.strptime(requested['date'], "%d/%m/%Y")
        plus_hour = requested_time + datetime.timedelta(hours=1)
        minus_hour = requested_time + datetime.timedelta(hours=-1)
        tables = Tables.query.all()
        available = False
        message = "No suitable tables are available at the moment."
        bookings = Bookings.query.filter(Bookings.time_of_booking.between(minus_hour,plus_hour)).filter(Bookings.date_of_booking==requested_date).group_by(Bookings.table_id).all()
        taken_tables = []
        for booking in bookings:
            taken_tables.append(booking.table_id)
        for table in tables:
            if requested['number_of_customers'] == table.number_of_seats and table.id not in taken_tables:
                available = True
                message = "Table available"
                return jsonify(dict(
                    available=available, 
                    message=message,
                    table=table.id
                ))
        
        return jsonify(dict(
            available=available, 
            message=message
        ))

@api.route('/tables')
class TablesCr(Resource):
    def get(self):
        tables = Tables.query.all()
        response = []
        for table in tables:
            table_dict = dict(
                id=table.id,
                number_of_seats=table.number_of_seats
            )
            response.append(table_dict)
        return jsonify(response)

    @api.expect(a_table)
    def post(self):
        new_table = api.payload
        table = Tables(
            id=new_table['id'],
            number_of_seats=new_table['number_of_seats']
        )
        db.session.add(table)
        db.session.commit()
        return jsonify(new_table)

@api.route('/tables/<int:id>')
class TablesRUD(Resource):
    def get(self, id):
        table = Tables.query.filter_by(id=id).first()
        table_dict = dict(
            id=table.id,
            number_of_seats=table.number_of_seats
        )
        return jsonify(table_dict)

    @api.expect(a_table)
    def put(self, id):
        table = Tables.query.filter_by(id=id).first()
        updated_table = api.payload
        table.id = updated_table['id']
        table.number_of_seats = updated_table['number_of_seats']
        db.session.commit()
        return jsonify(updated_table)

    def delete(self, id):
        table = Tables.query.filter_by(id=id).first()
        db.session.delete(table)
        db.session.commit()
        deleted_table = dict(
            id=table.id,
            number_of_seats=table.number_of_seats
        )
        return jsonify(deleted_table)  

@api.route('/customers')
class CustomersCR(Resource):
    def get(self):
        customers = Users.query.all()
        response = []
        for customer in customers:
            cust_dict = dict(
                id=customer.id,
                first_name=customer.first_name,
                last_name=customer.last_name,
                email=customer.email,
                staff=customer.staff
            )
            response.append(cust_dict)
        return jsonify(response)

    @api.expect(a_customer)
    def post(self):
        new_customer = api.payload
        customer = Users(
            first_name=new_customer['first_name'],
            last_name=new_customer['last_name'],
            email=new_customer['email'],
            password=bcrypt.generate_password_hash(new_customer['password']),
            staff=new_customer['staff']
        )
        db.session.add(customer)
        db.session.commit()
        response = dict(
            id=customer.id,
            first_name=customer.first_name,
            last_name=customer.last_name,
            email=customer.email
        )
        return jsonify(response)

@api.route('/customers/<int:id>')
class CustomersRUD(Resource):
    def get(self, id):
        customer = Users.query.filter_by(id=id).first()
        response = dict(
            id=customer.id,
            first_name=customer.first_name,
            last_name=customer.last_name,
            email=customer.email,
            staff=customer.staff
        )
        return jsonify(response)

    @api.expect(a_customer_without_pass)
    def put(self, id):
        customer = Users.query.filter_by(id=id).first()
        updated_customer = api.payload
        customer.first_name = updated_customer['first_name']
        customer.last_name = updated_customer['last_name']
        customer.email = updated_customer['email']
        customer.staff = updated_customer['staff']
        db.session.commit()
        response = dict(
            id=customer.id,
            first_name=customer.first_name,
            last_name=customer.last_name,
            email=customer.email,
            staff=customer.staff
        )
        return jsonify(response)

    def delete(self, id):
        customer = Users.query.filter_by(id=id).first()
        bookings = Bookings.query.filter_by(user_id=id).all()
        for booking in bookings:
            db.session.delete(booking)
        db.session.delete(customer)
        db.session.commit()
        response = dict(
            id=customer.id,
            first_name=customer.first_name,
            last_name=customer.last_name,
            email=customer.email,
            staff=customer.staff
        )
        return jsonify(response)  

@api.route('/customer/email')
class CustomerEmail(Resource):
    @api.expect(a_customer_email)
    def post(self):
        email = api.payload['email']
        customers = Users.query.all()
        for customer in customers:
            if customer.email == email:
                return jsonify(dict(exists=True, id=customer.id))
        return jsonify(dict(exists=False, id=None)) 

@api.route('/customer/auth/<int:id>')
class CustomerAuth(Resource):
    @api.expect(a_customer_auth)
    def post(self, id):
        customer_attempt = api.payload
        customer_saved = Users.query.filter_by(id=id).first()
        if bcrypt.check_password_hash(customer_saved.password, customer_attempt['password']) and customer_saved.email == customer_attempt['email']:
            return jsonify(dict(authenticated=True))
        return jsonify(dict(authenticated=False))

'''
@app.route('/bookings')
def bookings():
    bookings = Bookings.query.all()
    response = []
    for booking in bookings:
        booking_dict = dict(
            id=booking.id,
            time=booking.time_of_booking,
            date=booking.date_of_booking,
            table=booking.table_id,
            users=booking.user_id
        )
        response.append(booking_dict)
    return jsonify(response)

@app.route('/bookings/add', methods=['POST'])
def add_booking():
    new_booking = request.get_json()[0]
    booking = Bookings(
        time_of_booking=datetime.datetime.strptime(new_booking['time'], "%H:%M:%S"),
        date_of_booking=datetime.datetime.strptime(new_booking['date'], "%d/%m/%Y"),
        table_id=new_booking['table'],
        user_id=new_booking['user']
    )
    db.session.add(booking)
    db.session.commit()
    response = dict(
            id=booking.id,
            time=booking.time_of_booking,
            date=booking.date_of_booking,
            table=booking.table_id,
            users=booking.user_id
    )
    return jsonify(response)

@app.route('/bookings/update/<int:id>', methods=['PUT'])
def bookings_update(id):
    return False

@app.route('/bookings/available', methods=['POST'])
def bookings_available():
    requested = request.get_json()[0]
    requested_time = datetime.datetime.strptime(requested['time'], "%H:%M:%S")
    requested_date = datetime.datetime.strptime(requested['date'], "%d/%m/%Y")
    plus_hour = requested_time + datetime.timedelta(hours=1)
    minus_hour = requested_time + datetime.timedelta(hours=-1)
    tables = Tables.query.all()
    available = False
    message = "No suitable tables are available at the moment."
    bookings = Bookings.query.filter(Bookings.time_of_booking.between(minus_hour,plus_hour)).filter(Bookings.date_of_booking==requested_date).group_by(Bookings.table_id).all()
    taken_tables = []
    for booking in bookings:
        taken_tables.append(booking.table_id)
    for table in tables:
        if requested['number_of_customers'] == table.number_of_seats and table.id not in taken_tables:
            available = True
            message = "Table available"
            return jsonify(dict(
                available=available, 
                message=message,
                table=table.id
            ))
    
    return jsonify(dict(
        available=available, 
        message=message
    ))

# Tables

@app.route('/tables')
def tables_all():
    tables = Tables.query.all()
    response = []
    for table in tables:
        table_dict = dict(
            id=table.id,
            number_of_seats=table.number_of_seats
        )
        response.append(table_dict)
    return jsonify(response)

@app.route('/tables/<int:id>')
def tables(id):
    table = Tables.query.filter_by(id=id).first()
    table_dict = dict(
        id=table.id,
        number_of_seats=table.number_of_seats
    )
    return jsonify(table_dict)

@app.route('/tables/add', methods=['POST'])
def add_table():
    new_table = request.get_json()[0]
    table = Tables(
        id=new_table['id'],
        number_of_seats=new_table['number_of_seats']
    )
    db.session.add(table)
    db.session.commit()
    return jsonify(new_table)

@app.route('/tables/update/<int:id>', methods=['PUT'])
def tables_update(id):
    table = Tables.query.filter_by(id=id).first()
    updated_table = request.get_json()[0]
    table.id = updated_table['id']
    table.number_of_seats = updated_table['number_of_seats']
    db.session.commit()
    return jsonify(updated_table)

@app.route('/tables/delete/<int:id>', methods=['DELETE'])
def tables_delete(id):
    table = Tables.query.filter_by(id=id).first()
    db.session.delete(table)
    db.session.commit()
    deleted_table = dict(
        id=table.id,
        number_of_seats=table.number_of_seats
    )
    return jsonify(deleted_table)

# Customers

@app.route('/customers/<int:id>', methods=['GET'])
def customer(id):
    customer = Users.query.filter_by(id=id).first()
    response = dict(
        id=customer.id,
        first_name=customer.first_name,
        last_name=customer.last_name,
        email=customer.email,
        staff=customer.staff
    )
    return jsonify(response)

@app.route('/customers', methods=['GET'])
def customers_all():
    customers = Users.query.all()
    response = []
    for customer in customers:
        cust_dict = dict(
            id=customer.id,
            first_name=customer.first_name,
            last_name=customer.last_name,
            email=customer.email,
            staff=customer.staff
        )
        response.append(cust_dict)
    return jsonify(response)

@app.route('/customers/add', methods=['POST'])
def customer_add():
    new_customer = request.get_json()[0]
    customer = Users(
        first_name=new_customer['first_name'],
        last_name=new_customer['last_name'],
        email=new_customer['email'],
        password=bcrypt.generate_password_hash(new_customer['password']),
        staff=new_customer['staff']
    )
    db.session.add(customer)
    db.session.commit()
    response = dict(
        id=customer.id,
        first_name=customer.first_name,
        last_name=customer.last_name,
        email=customer.email
    )
    return jsonify(response)

@app.route('/customers/login/<int:id>', methods=['POST'])
def customer_login(id):
    customer_attempt = request.get_json()[0]
    customer_saved = Users.query.filter_by(id=id).first()
    if bcrypt.check_password_hash(customer_saved.password, customer_attempt['password']) and customer_saved.email == customer_attempt['email']:
        return jsonify(dict(authenticated=True))
    return jsonify(dict(authenticated=False)), 401

@app.route('/customers/email', methods=['POST'])
def customer_email():
    email = request.get_json()[0]['email']
    customers = Users.query.all()
    for customer in customers:
        if customer.email == email:
            return jsonify(dict(exists=True)), 409
    return jsonify(dict(exists=False))

@app.route("/customers/delete/<int:id>", methods=["DELETE"])
def account_delete(id):
    customer = Users.query.filter_by(id=id).first()
    bookings = Bookings.query.filter_by(user_id=id).all()
    for booking in bookings:
        db.session.delete(booking)
    db.session.delete(customer)
    db.session.commit()
    response = dict(
        id=customer.id,
        first_name=customer.first_name,
        last_name=customer.last_name,
        email=customer.email,
        staff=customer.staff
    )
    return jsonify(response)

@app.route('/customers/update/<int:id>', methods=['PUT'])
def customers_update(id):
    customer = Users.query.filter_by(id=id).first()
    updated_customer = request.get_json()[0]
    customer.first_name = updated_customer['first_name']
    customer.last_name = updated_customer['last_name']
    customer.email = updated_customer['email']
    db.session.commit()
    response = dict(
        id=customer.id,
        first_name=customer.first_name,
        last_name=customer.last_name,
        email=customer.email,
        staff=customer.staff
    )
    return jsonify(response)

'''
