from flask import Flask, jsonify, request, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flasgger import Swagger, swag_from
# import datetime
import os

app = Flask(__name__)
DB_PATH = ''

#konfigurasi database (default)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + DB_PATH
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

#Konfigurasi Swagger (default)
app.config['SWAGGER'] = {
    'title': 'Car Rental API',
    'uiversion': 3,
    'header': [],
    'specs': [
        {
            'endpoint': 'apispec_1',
            'route': '/apispec_1.json',
            'rule_filter': lambda rule: True,
            'model_filter': lambda rule: True,
        }
    ],
    'static_url_path': '/flasgger_static',
    'swagger_ui': True,
    'specs_route':'/apidocs/'
}
swagger = Swagger(app)
db = SQLAlchemy(app)

# Cars Model
class Cars(db.Model):
    car_id = db.Column(db.Integer, primary_key=True)
    model = db.Column(db.String(255), nullable=False)
    price_per_day = db.Column(db.DECIMAL(16,2), nullable=False)
    availability = db.Column(db.Boolean, default=False, nullable=False)

# Rentals Model
class Rentals(db.Model):
    rental_id = db.Column(db.Integer, primary_key=True)
    car_id = db.Column(db.Integer, db.ForeignKey('cars.car_id'), nullable=False)
    customer_name = db.Column(db.String(255), nullable=False)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    total_price = db.Column(db.DECIMAL(16,2), nullable=False)
    availability = db.Column(db.Boolean, default=False, nullable=False)
    
@app.before_first_request
def create_tables():
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

# Koneksi API
## Create
# @app.route('/car/add_new', methods=['POST'])
# @swag_from('swagger_docs/add_new_car.yaml')
# def add_new_car_api():
#     data = request.json
#     new_car = Cars(
#         model = data['model'],
#         price_per_day = data['price_per_day']
#         # quantity default true
#     )
#     db.session.add(new_car)
#     db.session.commit()
#     return jsonify ({'message': 'Success! A new car has been added to the data.'}), 201


#Fungsi menambahkan data
@app.route('/car/add_new', methods=['GET', 'POST'])
def add_new_car():
    if request.method == "POST":
        model = request.form.get('model')
        price_per_day = request.form.get('price_per_day')
        if not model or not price_per_day:
            return render_template('add_new_car.html')

        new_car = Cars(
            model = model,
            price_per_day = price_per_day
        )

        db.session.add(new_car)
        db.session.commit()
        return render_template('confirmation.html')
        
    return render_template('add_new_car.html')

# Koneksi API Delete
@app.route('/car/delete/<int:car_id>', methods=['DELETE'])
@swag_from('swagger_docs/delete_car.yaml')
def delete_car(car_id):
    try:
        car_delete = Cars.query.filter_by(car_id = car_id).first

@app.route('/car/delete', methods=['GET', 'POST'])
def delete_car():
    car_list = []
    try:
        print("masuk try")
        if request.method == 'GET':
            cars = Cars.query.all()
            car_list = cars
    except Exception as e:
        error_message = f"There is an error: {e}"
        # print(error_message)
    finally:
        print("finally")
        print(car_list)
        for car in car_list:
            print(car.model, car.price_per_day, car.availability)
            print(car.car_id)
        return render_template('delete_car.html', car_list=car_list)


if __name__ == '__main__':
    app.run(debug=True, port=5050)
