import mysql.connector

def connect_database():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="MySQL@123",
            database="medical_store"
        )

        print("MySQL Database Connected Successfully!")
        return conn

    except mysql.connector.Error as e:
        print("Database connection failed:", e)
        return None