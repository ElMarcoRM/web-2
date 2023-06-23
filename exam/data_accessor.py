from datetime import datetime, timedelta
import sqlite3



def add_to_cart(user, id):
    connection = sqlite3.connect('db.sqlite3')
    cursor = connection.cursor()
    try:
        create_car = "INSERT INTO app_cart (Car_id, quantity, user_id) VALUES (%s, 1, %s)"%(id, user)
        cursor.execute(create_car)
        connection.commit()
    except Exception as ex:
        print("AZAZA: ", ex)
    finally:
        connection.close()
