from flask import jsonify, request, session
from flask_jwt_extended import create_access_token
from src.database.db_mysql import getConnection
import re
from werkzeug.security import generate_password_hash, check_password_hash


#### Al conectarnos a la bbdd, tenemos que recordar cerrar la conexión con connection.close


# Función para extraer a todos los usuarios de la bbdd
def getAllUsers():
    connection = getConnection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()

    result = []
    for user in users:
        result.append(user)
        print("El usuario {}, {} -> Email: {}".format(user[0], user[1], user[2]))
    
    connection.close()

    return result


"""
A la hora de registrar a los usuarios, empleamos JWT para generar un token de seguridad que nos permita validar peticiones desde el front.
Dentro del token compartiremos unicamente el username.

No compartimos ni password, ni email en el token para evitar brechas de seguridad."""

def registerUser(newUserData):

    if request.method == "POST":
        try:
            # Para manejar las solicitudes de json en Flask
            data = newUserData
            username = data.get('username')
            email = data.get('email')
            password = data.get('password')

            print("Los datos que hemos recibido son: ", username, email, password)

            # Comprobar que el usuario no existe en la bbdd
            connection = getConnection()
            cursor = connection.cursor()

            cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
            existing_user = cursor.fetchone()
            regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'

            if existing_user:
                print("\nYa existe un usuario registrado con este email\n")
                return jsonify({'message': 'User already exists!'}), 400
            elif not (re.fullmatch(regex, email)):
                print("Invalid email")
                return jsonify({'message': 'Invalid email format'}), 400
            elif not username or not password or not email:
                return jsonify({ 'message': 'Bad request'}), 400
            else:
                # Hasheamos la contra y creamos instancia
                hashed_password = generate_password_hash(password)
                new_user = {
                    'username': username,
                    'email': email,
                    'password': hashed_password
                }
                cursor.execute("INSERT INTO users (username, email, password) VALUES (%s, %s, %s)", (username, email, hashed_password))
                connection.commit()

                # Una vez que hemos creado el nuevo usuario, generamos su token y lo devolvemos al front.
                token = create_access_token(identity=username)
                return jsonify( new_user, {'message': 'New user registered!',
                                           'token': token }), 200
        
        except Exception as e:
            print(type(e).__name__)
            connection.rollback()
            return jsonify({'message': 'Register failed', 'error': str(e)}), 500

        finally:
            print("Cerramos la session.")
            connection.close()

    

def loginUser(user_data):
    data = user_data
    
    # Necesitamos el username dentro de un array para manejarlo en la query.
    username:list = [] 
    username.append(data.get('username'))

    # Necesitamos la password como string
    password: str = data.get('password')
    
    print("\nLos datos que manda el usuario son: ", username, password)
    
    try: 
        connection = getConnection()
        cursor = connection.cursor()

        # Dentro de la query, los parametros que mandamos en el username deben ir dentro de un array.
        cursor.execute("SELECT * FROM users WHERE username=%s", (username))
        found_user = cursor.fetchone()
        print("Tenemos al usuario: ", found_user)
        print("Esta es la contraseña alojada en la bbdd", found_user[3])

        if not found_user:
            return jsonify({ 'message': 'Bad request - User not found'}), 400
        else:
            # Si encontramos al usuario, comprobamos contraseña
            db_password = found_user[3]
            if check_password_hash(db_password, password) == True:
                print("User and password are correct!")
                token = create_access_token(identity=found_user[1]) # Dentro del token metemos el username y su id
                return jsonify({'message': 'Login Success!',
                                'token': token }), 200
            else:
                return jsonify({'message': 'Password is not correct'}), 400
    
    except Exception as e:
        print(type(e).__name__, e)
        connection.rollback()
        return jsonify({'message': 'Error en la solicitud'}), 400
    
    finally:
        print("Cerramos la conexión!")
        connection.close()