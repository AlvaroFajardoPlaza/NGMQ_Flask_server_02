from src.database.db_mysql import getConnection


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


def register_user():
    pass
    # if request.method == "POST":
    #     try:
    #         # Para manejar las solicitudes de json en Flask
    #         data = request.get_json()

    #         username = data.get('username')
    #         email = data.get('email')
    #         password = data.get('password')

    #         print("Los datos que hemos recibido son: ", username, email, password)

    #         # Comprobar que el usuario no existe en la bbdd
    #         existing_user = db.session.query(User).filter_by(email=email).first()
    #         if existing_user:
    #             print("\nYa existe un usuario registrado con este email\n")
    #             return jsonify({'message': 'User already exists!'}), 400
            
    #         # Hasheamos contraseña
    #         hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

    #         # Creamos la instancia de usuario en la bbdd
    #         new_user = User(username= username, email=email, password=hashed_password)
    #         db.session.add(new_user)
    #         db.session.commit()
    #         return jsonify({'message':'Successful register!'})
        
    #     except Exception as e:
    #         print(type(e).__name__)
    #         db.session.rollback()
    #         return jsonify({'message': 'Register failed', 'error': str(e)}), 500

    #     finally:
    #         print("Cerramos la session.")
    #         db.session.close()
    
    

def login_user():
    print("\nEntramos en la función de login")
    pass