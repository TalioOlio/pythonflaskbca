import sqlite3
from sqlalchemy import create_engine, Column, Integer, String, MetaData, Table, ForeignKey, DateTime, DECIMAL, Boolean

DATABASE_URI = 'sqlite:///rental.db'
engine = create_engine(DATABASE_URI, echo=True)
metadata = MetaData()

# Data Master: cars (car_id, model, 
# price_per_day, availability)


# Cars
cars = Table('cars', metadata,
    Column('car_id', Integer, primary_key=True),
    Column('model', String),
    Column('price_per_day', DECIMAL(16,2)),
    Column('availability', Boolean, default=True)
    )

# Rentals
rentals = Table('rentals', metadata,
    Column('rental_id', Integer, primary_key=True),
    Column('car_id', String, ForeignKey('cars.car_id')),
    Column('customer_name', String),
    Column('start_date', DateTime),
    Column('end_date', DateTime),
    Column('total_price', DECIMAL(16,2))
)

metadata.create_all(engine)
print("rental.db and tables has been successfully created")
