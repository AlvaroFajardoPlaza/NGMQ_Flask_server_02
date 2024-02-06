"""
En el módulo de Trivia reside toda la lógica para llamar a las preguntas que tenemos alojadas en nuestra tabla en la bbdd.

Este módulo define las funciones encargadas de crear los tipo tests de manera random y también la función para comprobar los resultados.
"""
import random
from random import shuffle
from src.database.db_mysql import getConnection


def getCategories():

    connection = getConnection()
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM categories")
    categories_list = cursor.fetchall()

    return categories_list



def randomTriviaTest():

    connection = getConnection()
    cursor = connection.cursor()

    # 1. Recibir todas las preguntas
    cursor.execute("SELECT * FROM questions_answers")
    all_questions: list = list(cursor.fetchall()) # Recibimos una lista de tuplas
    # print(all_questions)

    # 2. Seleccionar de manera aleatoria 10 sin que se repitan sus ids con random sample, para que los elementos no se repitan
    selected_questions = random.sample(all_questions, 10)

    final_random_trivia: list = []
    for select in selected_questions:
        register = {
            "id_pregunta" : select[0],
            "pregunta" : select[1],
            "ans1" : select[2],
            "ans2" : select[3],
            "ans3" : select[4],
            "category" : select[5],
        }
        final_random_trivia.append(register)
    
    print(final_random_trivia)
    return final_random_trivia



    # for x in range(10):
    #     question = ()
    #     if question:
    #         selected_questions_ids.add(question[0])
    #         register = {
    #             "id_pregunta" : question[0],
    #             "pregunta" : question[1],
    #             "ans1" : question[2],
    #             "ans2" : question[3],
    #             "ans3" : question[4],
    #             "category" : question[5],
    #         }
    #         random_test.append(register)
    #     else:
    #         print("No hay más preguntas disponibles en la bbdd")



