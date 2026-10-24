from database import connect_database

conn = connect_database()

if conn:
    conn.close()
    print("Connection closed.")