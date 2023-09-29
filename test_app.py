import unittest
from flask_testing import TestCase
from flask import url_for
from car_rental import app, db, Cars, Rentals  # Import modul-modul yang diperlukan

# Kelas MyTest untuk melakukan testing pada aplikasi
class MyTest(TestCase):

    # Metode untuk membuat aplikasi dalam mode testing
    def create_app(self):
        app.config['TESTING'] = True  # Mengaktifkan mode testing
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///rental.db'  # Menggunakan database in-memory untuk testing
        return app

    # Metode yang dijalankan sebelum setiap test
    def setUp(self):
        db.create_all()  # Membuat semua tabel dalam database

    # Metode yang dijalankan setelah setiap test
    def tearDown(self):
        db.session.remove()  # Menghapus sesi database
        db.drop_all()  # Menghapus semua tabel dalam database

    # Test untuk endpoint index '/'
    def test_index(self):
        response = self.client.get('/') 
        self.assert200(response)  # Memastikan response adalah 200 OK
        self.assert_template_used('index.html')  # Memastikan template yang digunakan adalah 'index.html'

    # Test untuk menambah mobil baru
    def test_add_new_car(self):
        # Melakukan request POST ke '/car/_add_new' dengan data mobil baru
        response = self.client.post('/rental', json={
            'model': 'Toyota Corolla',
            'price_per_day': 2000000,
        })
        self.assertStatus(response, 201)  # Memastikan response adalah 201 Created
        car = Cars.query.first()  # Mengambil mobil pertama dari database
        self.assertEqual(Cars.model, 'Toyota Corolla') 

    # Test untuk menghapus mobil dari car_list
    def test_delete_karyawan(self):
        new_car = Cars(model='Ford Mustang', price_per_day=10000000)
        db.session.add(new_car)
        db.session.commit()

        # Melakukan request DELETE
        response = self.client.delete(f'/car/delete/{new_car.car_id}')
        self.assert200(response)  # Memastikan response adalah 200 OK
        self.assertIsNone(Cars.query.get(new_car.car_id))  # Memastikan data dnegan id tersebut sudah dihapus

    # Test untuk mendapatkan semua mobil
    def test_display_all_cars(self):
        car1 = Cars(model='Toyota Corolla', price_per_day=2000000)
        car2 = Cars(model='Ford Mustang', price_per_day=10000000)
        db.session.add(car1)
        db.session.add(car2)
        db.session.commit()

        # Melakukan request GET ke '/car/list'
        response = self.client.get('/car/list')
        self.assert200(response)  # Memastikan response adalah 200 OK
        self.assert_template_used('display_cars.html') 
        self.assertIn(b'Toyota Corolla', response.data) 
        self.assertIn(b'Ford Mustang', response.data)  
        
    # Test untuk mendapatkan semua Transaksi rental
    def test_display_all_transactions(self):
        transaction1 = Rentals(customer_name='Talia', start_date='2023-09-29', end_date='2023-09-30', total_price=2000000)
        transaction2 = Rentals(customer_name='Lia', start_date='2023-09-29', end_date='2023-09-30', total_price=10000000)
        db.session.add(transaction1)
        db.session.add(transaction2)
        db.session.commit()

        response = self.client.get('/transaction/list')
        self.assert200(response)  # Memastikan response adalah 200 OK
        self.assert_template_used('display_transactions.html') 
        self.assertIn(b'Talia', response.data) 
        self.assertIn(b'Lia', response.data)  

if __name__ == '__main__':
    unittest.main()  