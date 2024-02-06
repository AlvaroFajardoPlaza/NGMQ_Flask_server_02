import mysql.connector
# from decouple import config

MYSQL_HOST = "localhost"
MYSQL_USER = "root"
MYSQL_PASSWORD = ""
MYSQL_DB = "NGMQ_flask_test02" 
HEX_SECRET_KEY = "orion"

"""
Dentro de este archivo tenemos la llamada a la conexión a nuestra BBDD MYSQL
"""

def getConnection():
    try:
        connection = mysql.connector.connect(
            user = MYSQL_USER, 
            password = MYSQL_PASSWORD, 
            host = MYSQL_HOST, 
            database = MYSQL_DB
            )
        
        # if connection.is_connected():
        #     print("Estamos conectados a la bbdd!")
        # else:
        #     print("No nos hemos podido conectar...")    

        return connection

    except Exception as e:
        print(type(e).__name__, e)



