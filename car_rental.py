from flask import Flask, jsonify, request, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
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
            price_per_day = price_per_day,
            availability = True
        )

        db.session.add(new_car)
        db.session.commit()
        return render_template('confirmation.html')
        
    return render_template('add_new_car.html')

# # Display All Cars
@app.route('/car/list', methods=['GET'])
def display_cars():
    car_list = []
    try:
        if request.method == 'GET':
            car_list = Cars.query.all()
    except Exception as e:
        error_message = f"There is an error: {e}"
        print(error_message)
    finally:
        return render_template('display_cars.html', car_list=car_list)

# Koneksi API Delete
@app.route('/car/delete/<int:car_id>', methods=['DELETE'])
@swag_from('swagger_docs/delete_car.yaml')
def delete_car_with_id(car_id):
    try:
        car_delete = Cars.query.filter_by(car_id = car_id).first()
        
        if car_delete:
            db.session.delete(car_delete)
            db.session.commit()
            return jsonify ({'message': f'The car with car ID {car_id} has been successfully deleted'}), 200
        else:
            return jsonify ({'message': f'Can not find the car with car ID {car_id}'}), 404
    except Exception as e:
        return jsonify({'message': f"There is an error: {e}"}), 500

@app.route('/car/delete', methods=['GET', 'POST'])
def delete_car():
    car_list = []
    try:
        if request.method == 'GET':
            car_list = Cars.query.all()
    except Exception as e:
        error_message = f"There is an error: {e}"
        print(error_message)
    finally:
        return render_template('delete_car.html', car_list=car_list)


## Transaction
@app.route('/transaction/create', methods=['GET', 'POST'])
def create_transaction():
    try:
        car_list = []
        if request.method == 'GET':
            car_list = Cars.query.all()
        if request.method == "POST":
            # car_list = Cars.query.all()
            car_id = request.form.get('car_id')
            customer_name = request.form.get('customer_name')
            start_date = request.form.get('start_date')
            end_date = request.form.get('end_date')
            car = db.session.get(Cars, car_id)
            print(request.form, car_id)
            if not car:
                return render_template('create_transaction.html', car_list=car_list, error='There is no available car')
            if not customer_name or not start_date or not end_date:
                return render_template('create_transaction.html', car_list=car_list, error='Required')
            print(car)
            
            new_transaction = Rentals(
                car_id = car_id,
                customer_name = customer_name,
                start_date = datetime.strptime(start_date, "%Y-%m-%d"),
                end_date = datetime.strptime(end_date, "%Y-%m-%d"),
                total_price = (datetime.strptime(end_date, "%Y-%m-%d") - datetime.strptime(start_date, "%Y-%m-%d")).days,*car.price_per_day
            )
            car.availability = False
            db.session.add(new_transaction)
            db.session.commit()
            return render_template('display_transactions.html') #setelah insert ke db, pergi kemana
        return render_template('index.html') #setelah insert ke db, pergi kemana
        
    except Exception as e:
        return jsonify({'message': f"There is an error: {e}"}), 500
    finally:
        return render_template('create_transaction.html', car_list=car_list)
        
# # Display All Transactions
@app.route('/transaction/list', methods=['GET'])
def display_transactions():
    transaction_list = []
    try:
        if request.method == 'GET':
            transaction_list = Rentals.query.all()
    except Exception as e:
        error_message = f"There is an error: {e}"
        print(error_message)
    finally:
        return render_template('display_transactions.html', transaction_list=transaction_list)

# Delete Transactions 
@app.route('/transaction/delete/<int:rental_id>', methods=['DELETE'])
@swag_from('swagger_docs/delete_transaction.yaml')
def delete_transaction_with_id(rental_id):
    try:
        transaction_delete = db.session.get(Rentals, rental_id)
        car = db.session.get(Cars, transaction_delete.car_id)
        
        if transaction_delete:
            car.availability = True
            db.session.delete(transaction_delete)
            db.session.commit()
            return jsonify ({'message': f'The car with car ID {rental_id} has been successfully deleted'}), 200
        else:
            return jsonify ({'message': f'Can not find the car with car ID {rental_id}'}), 404
    except Exception as e:
        return jsonify({'message': f"There is an error: {e}"}), 500

@app.route('/transaction/delete', methods=['GET', 'POST'])
def delete_transaction():
    transaction_list = []
    try:
        if request.method == 'GET':
            transaction_list = Rentals.query.all()
    except Exception as e:
        error_message = f"There is an error: {e}"
        print(error_message)
    finally:
        return render_template('delete_transaction.html', transaction_list=transaction_list)

if __name__ == '__main__':
    # app.run(debug=True) 
    app.run(debug=True, port=5050)
