"""
En el módulo de Trivia reside toda la lógica para llamar a las preguntas que tenemos alojadas en nuestra tabla en la bbdd.

Este módulo define las funciones encargadas de crear los tipo tests de manera random y también la función para comprobar los resultados.
"""
import random
from random import shuffle

from flask import jsonify
from src.AuthMod.auth_module import decodeToken
from src.database.db_mysql import getConnection


def getCategories():

    connection = getConnection()
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM categories")
    categories_list = cursor.fetchall()

    return categories_list



def randomTriviaTest():

    connection = getConnection()
    cursor = connection.cursor(dictionary=True) # Obtenemos resultados como dict

    # 1. Recibir todas las preguntas, configurar un JOIN en la llamada al traer las category_id, para en realidad llamar a su nombre.
    cursor.execute("SELECT questions_answers.*, categories.name FROM questions_answers INNER JOIN categories ON questions_answers.category_id=categories.id")
    all_questions: list = list(cursor.fetchall()) # Recibimos una lista de tuplas
    # print(all_questions)

    # 2. Seleccionar de manera aleatoria 10 sin que se repitan sus ids con random sample, para que los elementos no se repitan
    selected_questions = random.sample(all_questions, 10)
    print("Estas son las 10 preguntas seleccionadas: ", selected_questions)

    final_random_trivia: list = []
    for select in selected_questions:
        register = {
            "id_pregunta" : select['id'],
            "pregunta" : select['question'],
            "ans1" : select['ans'],
            "ans2" : select['w1'],
            "ans3" : select['w2'],
            "category" : select['name'],
        }
        final_random_trivia.append(register)
    
    connection.close()
    print(final_random_trivia)
    return final_random_trivia



def categorizedTriviaTest(categories: list):
    # 0. Recibimos las categorías dentro de un array [1, 2, 3,...]. Covertimos la cadena de numeros a strings
    numbers_to_str: list = [str(num) for num in categories]    

    # 1. Llamamos a la conexión y solicitamos las preguntas que coincidan con los ids de las categorías
    connection = getConnection()
    cursor = connection.cursor(dictionary=True)

    # Utilizamos la variable numbers_str para extraer nuestras preguntas, empleamos ORDER BY RAND con un limite de 10 para extraer 10 preguntas al azar
    query = "SELECT qa.id AS id_pregunta, qa.ans AS ans1, qa.question AS pregunta, qa.w1 AS ans2, qa.w2 AS ans3, c.name AS category FROM questions_answers AS qa " \
            "INNER JOIN categories AS c ON qa.category_id=c.id " \
            "WHERE qa.category_id IN (%s) ORDER BY RAND() LIMIT 10"
    
    in_p = ', '.join(list(map(lambda x: '%s', numbers_to_str)))
    query = query % in_p

    cursor.execute(query, numbers_to_str)
    all_questions: list = cursor.fetchall()

    connection.close()
    print("\n\nNuestro trivia categórico: ", all_questions, len(all_questions))
    return all_questions


# Dentro de esta función manejamos las respuestas al trivia test
# Además de devolver la respuesta del score al usuario, tenemos que actualizar los datos del usuario
def getAnswers(userAnswers: dict):
    try:
        connection = getConnection()
        cursor = connection.cursor(dictionary=True)
        print("\n\nSi, tenemos las respuestas enviadas por el user: ", userAnswers, type(userAnswers))
        
        # print("\n\nTenemos al usuario?", user)
        
        # Extraemos las preguntas de la bbdd, tomando los valores o keys de dentro del diccionario, recuperamos las preguntas de la bbdd y las comparamos con las que envía el usuario
        final_trivia_score = 0

        for question_id, user_answer in userAnswers.items():
            query: str = "SELECT * FROM questions_answers WHERE id=%s"
            cursor.execute(query, (question_id,))
            ddbb_question = cursor.fetchone()

            if ddbb_question['ans'] == user_answer:
                final_trivia_score += 1
            else:
                print("La respuesta no fue correcta")

        # print("\n\nEl resultado final al triviatest es: ", final_trivia_score, type(final_trivia_score))
        return final_trivia_score
    
    except TypeError as e:
        print(type(e).__name__, e)
        return e
    except Exception as e:
        print(type(e).__name__, e)
        return e

# Esta función, llama a los datos del usuario y los actualiza
def updateUserScore(user_token: str, scoreResult: str):
    print("\n\nRecibimos el user y el score???\n", user_token, "\nY este es el resultado al triviaTest:", scoreResult )

    try:    
        if len(user_token) > 0:
            user_data = decodeToken(user_token)

            if isinstance(user_data, dict):
                connection = getConnection()
                cursor = connection.cursor()
                # Conseguimos los datos del usuario, los modificamos y los volvemos a enviar
                cursor.execute("SELECT * FROM users WHERE id=%s", (user_data['id'], ))
                user_found = cursor.fetchone()
                connection.close()

                print("Hemos encontrado al usuario que actualizar???", user_found)

                # Actualizar la puntuación del usuario en la base de datos.
                # Recuerda, que ambas columnas las estás tratando como integers
                user_score: int = 0
                user_trivias_completed: int = 0

                if (user_found[4] == None) and (user_found[5] == None):
                    user_score = int(scoreResult)
                    user_trivias_completed = 1
                else:
                    user_score = user_found[4] + int(scoreResult)
                    user_trivias_completed = user_found[5] + 1

                print("\n\nEl nuevo score del usuario {} es: {}. Trivias completados: {}".format(user_found[1], user_score, user_trivias_completed))

                connection = getConnection()
                cursor = connection.cursor()
                cursor.execute("UPDATE users SET score=%s, trivias_completed=%s WHERE id=%s", (user_score, user_trivias_completed, user_found[0]))

                connection.commit()
                connection.close()

                print("Puntuación del usuario actualizada exitosamente.")
                return jsonify(success=True, message="Puntuación actualizada exitosamente.")
            else:
                print("No se pudo obtener datos del usuario.")
                return jsonify(success=False, message="Error al obtener datos del usuario.")

        else:
            print("Token de usuario vacío")
            return jsonify(success=False, message="Token de usuario vacío.")
    
    except Exception as e:
        print(type(e).__name__, e)
        return jsonify(success=False, message="Error al actualizar la puntuación del usuario.")
    






   
   

    


