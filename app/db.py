# 150240721
# Berkay Emre Keskin
# BLG317E

import mysql.connector
import os
from flask import Flask
from mysql.connector import Error
from dotenv import load_dotenv

app = Flask(__name__)

# ----------------------------- DATABASE CONFIG -----------------------------
def create_connection():
    """Creates a connection to the MySQL database."""
    load_dotenv()
    try:
        connection = mysql.connector.connect(
            host=os.getenv('DB_HOST'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASS'),
            database=os.getenv('DB_NAME')
        )
        if connection.is_connected():
            print("Successfully connected to the database")
        return connection
    except Error as e:
        print(f"Error while connecting to MySQL: {e}")
        return None
