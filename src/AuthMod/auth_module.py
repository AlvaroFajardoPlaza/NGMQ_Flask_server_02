from flask import jsonify, request, session
from flask_jwt_extended import create_access_token, decode_token
import jwt
from src.database.db_mysql import getConnection
import re
from werkzeug.security import generate_password_hash, check_password_hash


#### Al conectarnos a la bbdd, tenemos que recordar cerrar la conexión con connection.close


# Función para extraer a todos los usuarios de la bbdd.
# Esta función viene a mostrar el resultado del trivia poll.
def getAllUsers():
    connection = getConnection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    connection.close()

    # Tenemos que manejar la respuesta de users, ya que son tuplas
    result = []
    for user in users:
        #Por cada usuario, vamos a crear un objeto que añadiremos después al array de results
        beta_user = {
            'username': user[1],
            'score': user[4],
            'trivias_completed': user[5],
            'percentage': 0,
        }
        if (beta_user['trivias_completed'] != None ) and (beta_user['score'] != None):
            beta_user['percentage'] = round((beta_user['score'] / beta_user['trivias_completed']) * 10, 3)
        else:
            beta_user['percentage'] = 0

        result.append(beta_user)
    
    # Antes de devolver el resultado, lo ordenamos
    result_sorted = sorted(result, key=lambda x: x['percentage'], reverse=True)

    print("\n\n Resultado final de usuarios: ", result_sorted)
    return result_sorted


# Función para devolver un solo usuario cuando lo busquemos por su username
def findByUsername(username: str):
    try:
        print("Recibimos el username????", username, type(username))

        connection = getConnection()
        cursor = connection.cursor()

        cursor.execute("SELECT * FROM users WHERE username=%s", (username))
        user_found = cursor.fetchone()

        print("Hemos encontrado al usuario")
        connection.close()

    except Exception as e:
        print(type(e).__name__, e)
        connection.close()
        return jsonify({'message': 'Error en la solicitud', 'error': e}), 400 



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


# Esta función va a recoger el token que mandamos desde el front y a devolver los datos del usuario para autenticarlo.
def decodeToken(encoded_jwt):
    
    try:
        # 1. Llamamos a la función decode_token
        if encoded_jwt == None:
            print("No tenemos token en local storage, salimos de la función.")

        else: 
            response = decode_token(encoded_jwt['token'])
            # De la response, que es de tipo object, tenemos que coger el key-value 'sub', ya que es donde está alojado el username.
            # Después, hacemos la llamada a la bbdd, para traer los datos de score y trivias completados y alojarlo en el observable User$
            username_in_token = [response['sub']]
            # print("Hemos conseguido el username alojado dentro del token?", username_in_token)

            connection = getConnection()
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM users WHERE username=%s", (username_in_token[0], ))
            
            user_logged = cursor.fetchone()
            # print("Tenemos al usuario????", user_logged)
            if user_logged:
                return {
                    'id': user_logged[0],
                    'username': user_logged[1],
                    'email': user_logged[2],
                    'score': user_logged[4],
                    'trivias_completed': user_logged[5],
                }
            else:
                return "No hemos encontrado al usuario"
    except jwt.exceptions.ExpiredSignatureError:
        return "Ha expirado el token... hay que volver a iniciar sesión."
    except jwt.exceptions.DecodeError:
        return "Token no válido"
    except Exception as e:
        print(type(e).__name__, e)



# Funcion de Log out para el user
# Esta función la manejamos desde el front directamente.
def logOut():
    print("Tenemos que eliminar el token del local_storage y devolver al usuario a la pantalla de HOME.")