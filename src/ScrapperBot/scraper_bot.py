#### Creamos nuestro script de selenium
"""
En este fichero vamos a crear las funciones que nos van a permitir nutrir la bbdd con las preguntas y respuestas para los trivia tests.

Al iniciar la aplicación por primera vez, llamaremos a estas funciones para poder recopilar los datos.
"""
import random
from flask import jsonify
import selenium                                       
import os                                             
import time                                           
import re                                             
                                                      
from selenium import webdriver                        
from selenium.webdriver.chrome.service import Service 
from selenium.webdriver.chrome.options import Options 
from selenium.webdriver.common.by import By


from src.database.db_mysql import getConnection
from src.Models.models import Category, QuestionsAnswers


# ------------------- CONFIGURACIÓN INICIAL DEL DRIVER  ------------------------------- #  
# 0. URL desde la que vamos a extraer la información                                       
URL = "https://youengage.me/blog/trivia-questions/"  

# 1. Llamamos a la ruta del webdriver en nuestro entorno local                                          
PATH_DRIVER = "/Applications/driver_sel/chromedriver-mac-arm64/chromedriver"                            
CHROME_SERVICE = Service( executable_path = PATH_DRIVER )                                               
options = Options()                                                                                     
# options.add_argument("--incognito") # Abre la ventana del webdriver en incógnito                        
# options.add_argument("--headless") # Ejecuta el scrapeo de la web sin abrir ventana del driver          
                                                                                                        
                                                                                        
#### FUNCIONES
def categoriesExist():
    connection = getConnection()
    cursor = connection.cursor()

    # Comprobamos que las categorias existen en la bbdd
    try:
        cursor.execute("SELECT * FROM categories")
        existing_categories = cursor.fetchall()
        for category in existing_categories:
            print(category.id, category.name)
        
        connection.close()
        return existing_categories
    
    except Exception as e:
        print(type(e).__name__, e)
        return None




def scrapeCategories():
    # # 1. Verificar si las categorías ya existen en la base de datos
    # existing_categories = categoriesExist()
    # category_names = [category[1] for category in existing_categories]

    # if set(category_names).issuperset(set([category_instance['name'] for category_instance in category_list])):
    #     return "Las categorías ya existen en la base de datos"


    # 2. Si las categorías no existen, creamos la instancia de nuestro driver y ajustamos el tamaño de la ventana                         
    driver = webdriver.Chrome(service=CHROME_SERVICE, options=options)                                      
    driver.set_window_size( 550, 950 )
    driver.get(URL)                                                                                                     
    time.sleep(3)

    # Primero aceptamos las cookies                                                                                                             
    try:                                                                                                                
        cookies_site = driver.find_element(By.XPATH, value="/html/body/section/div/div[1]/div[2]/button[1]")            
        cookies_site.click()                                                                                            
        print("Aceptamos la política de cookies.")                                                                      
    except Exception as e:                                                                                              
        print("Algo salió mal")                                                                                         
        print(e, type(e).__name__)                                                                                      
                                                                                                                        
    time.sleep(3)

    # Hacemos scrapping de las categorías y creamos las instancias en la BBDD
    # Tenemos que considerar la casuística de que las categorías ya estén en la BBDD
    try:                                                                                                                                          
        category_list = []                                                                                                                        
        categories = driver.find_elements(By.XPATH, value="/html/body/div[1]/section[2]/div/div/div/div[1]/ol[1]/li")                             
        print("Estas son las categorias que tenemos que registrar en la BBDD:")                                                                   
        for index, category in enumerate(categories):
            if index <= 12:
                category_edit = re.sub(r'\s*Trivia\s*Questions$', '', category.text)
                category_instance = Category(name=category_edit, id=index+1) 

                # En este punto serializamos el objeto para mandarlo a la bbdd
                serialize_category = category_instance.serialize()
                print("Serializamos la categoría: ", serialize_category, type(serialize_category))
                category_list.append(serialize_category)
                
            else:
                continue

        print("\n --------------------\nMi lista de categorías para incluir en la BBDD:\n")
        print(category_list)
        
        
        # Llamamos a la conexión con la bbdd y guardamos las instancias de cada categoria
        connection = getConnection()
        cursor = connection.cursor()
        cursor.executemany("INSERT INTO categories (id, name) VALUES (%(id)s, %(name)s)", category_list)
        connection.commit()
        connection.close()    
        return "-------------- CATEGORÍAS AGREGADAS A LA BBDD --------------"

    except TypeError as e:
        print(type(e).__name__, e)
        return "Type Error"        

    except Exception as e:                               
        print("Algo no ha ido bien", e, type(e).__name__)
        return "{}".format(e)



def scrapeQuestionsAnswers():
    driver = webdriver.Chrome(service=CHROME_SERVICE, options=options)                                      
    driver.set_window_size( 550, 950 )
    driver.get(URL)                                                                                                     
    time.sleep(3)  

    # 0 -> Primero aceptamos las cookies                                                                                                             
    try:                                                                                                                
        cookies_site = driver.find_element(By.XPATH, value="/html/body/section/div/div[1]/div[2]/button[1]")            
        cookies_site.click()                                                                                            
        print("Aceptamos la política de cookies.")                                                                      
    except Exception as e:                                                                                              
        print("Algo salió mal")                                                                                         
        print(e, type(e).__name__)                                                                                      
                                                                                                                        
    time.sleep(3)

    
    # 1 -> Recuperamos las preguntas y respuestas
    try:
        questions_and_answers_list = []
        for category in range(2,15):
            beta_results = driver.find_elements(By.XPATH, value="/html/body/div[1]/section[2]/div/div/div/div[1]/ol[{}]/li".format(category))
            for result in beta_results:
                questions_and_answers_list.append(result.text)

    except Exception as e:
        print("Algo ha salido mal al recuperar las preguntas")
        print(e, type(e).__name__)

    #print("\n\nEste es mi listado de preguntas:", questions_and_answers_list)
    print("\n\nEl número total de preguntas que tengo que manejar son: ", len(questions_and_answers_list))

    # 2 -> Tenemos que formatear los resultados obtenidos.
    # Por cada registro del array, lo subdividimos
    array_first_edit = []
    for register in questions_and_answers_list:
        result = register.split(sep="\n")
        array_first_edit.append(result)
        # print(result)
    
    time.sleep(3)
    for register in array_first_edit:
        if register[1].startswith("Answer"):
            register[1] = register[1][7:].strip()
        else:
            continue
        
        ##### TENEMOS QUE MANEJAR LAS RESPUESTAS ERRÓNEAS, w1 y w2
        if len(register) > 2:
            register[2] = register[2].split(sep=",")
        else:
            continue
    #print("Este es mi array de resultados: ", array_first_edit)

    # 3 -> CREAMOS LAS INSTANCIAS EN LA BASE DE DATOS
    final_results = []
    for index, array_of_data in enumerate(array_first_edit):

        question_text = array_of_data[0]
        right_answer = array_of_data[1]

        # Verificamos si existe un tercer elemento en array_of_data antes de intentar acceder a array_of_data[2]
        if len(array_of_data) > 2:
            # Verificamos que existan dos elementos dentro del array de errores:
            if len(array_of_data[2]) > 1:
                wrong_1 = array_of_data[2][0][7:].strip() 
                wrong_2 = array_of_data[2][1].strip()
            else:
                wrong_1 = array_of_data[2][0][7:].strip()
                wrong_2 = None
        else:
            wrong_1 = None
            wrong_2 = None

        # Creamos las instancias:
        question_instance = QuestionsAnswers(
            id=index,
            question=question_text, 
            ans=right_answer, 
            w1=wrong_1, 
            w2=wrong_2
            )
        # Tenemos que serializar la nueva instancia creada, para poder almacenarla en la bbdd
        serialize_instance = question_instance.serialize()
        final_results.append(serialize_instance)

    print("\n\n---------\nLos resultados en mi array final de resultados son los siguientes:")
    for register in final_results:
        print(register, type(register))

    # Finalizamos guardando los registros del array de resultados finales a la bbdd.
    try:
        connection = getConnection()
        cursor = connection.cursor()

        cursor.executemany("INSERT INTO questions_answers (id, question, ans, w1, w2, category_id) VALUES (%(id)s, %(question)s, %(ans)s, %(w1)s, %(w2)s, %(category_id)s)", final_results)
        connection.commit()
        connection.close()
        return "-------------- PREGUNTAS Y RESPUESTAS AGREGADAS A LA BBDD --------------"
    
    except TypeError as e:
        connection.rollback()
        print(type(e).__name__, e)
        return "TypeError"

    except Exception as e:
        connection.rollback()
        print(type(e).__name__, e)
        return "{}".format(e)


def categorizeQuestions():
    # 1 -> Llamamos a nuestro listado completo de preguntas
    try: 
        connection = getConnection()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM questions_answers")
        all_questions_list: list = cursor.fetchall() # Listado de tuplas
        connection.close()
        
    except Exception as e:
        print(type(e).__name__, e)
        return e

    
    converted_questions_list:list = []
    for question in all_questions_list:
        converted_question = list(question)
        converted_questions_list.append(converted_question)
    
    #print(converted_questions_list)

    connection = getConnection()
    cursor = connection.cursor()
    for converted_question in converted_questions_list:
        if (converted_question[0] >= 1) and (converted_question[0] < 10 ):
            #print(converted_question)
            category_id = 1
            sql_query = ("UPDATE questions_answers SET category_id=%s "
                        "WHERE id BETWEEN %s AND %s")
            val = (category_id, 1, 9)
            cursor.execute(sql_query, val)


        elif (converted_question[0] >= 10) and (converted_question[0] < 20 ):
            #print(converted_question)
            category_id = 2
            sql_query = ("UPDATE questions_answers SET category_id =%s "
                        "WHERE id BETWEEN %s AND %s")
            val = (category_id, 10, 20)
            cursor.execute(sql_query, val)


        elif (converted_question[0] >= 20) and (converted_question[0] < 30 ):
            category_id = 3
            sql_query = ("UPDATE questions_answers SET category_id =%s "
                        "WHERE id BETWEEN %s AND %s")
            val = (category_id, 20, 30)
            cursor.execute(sql_query, val)

            
        elif (converted_question[0] >= 30) and (converted_question[0] < 41 ):
            category_id = 4
            sql_query = ("UPDATE questions_answers SET category_id =%s "
                        "WHERE id BETWEEN %s AND %s")
            val = (category_id, 30, 41)
            cursor.execute(sql_query, val)

        elif (converted_question[0] >= 40) and (converted_question[0] < 50 ):  
            category_id = 5
            sql_query = ("UPDATE questions_answers SET category_id =%s "
                        "WHERE id BETWEEN %s AND %s")
            val = (category_id, 40, 49)
            cursor.execute(sql_query, val)

        elif (converted_question[0] >= 50) and (converted_question[0] < 58 ):
            category_id = 6
            sql_query = ("UPDATE questions_answers SET category_id =%s "
                        "WHERE id BETWEEN %s AND %s")
            val = (category_id, 50, 57)
            cursor.execute(sql_query, val)

        elif (converted_question[0] >= 58) and (converted_question[0] < 68 ):
            category_id = 7
            sql_query = ("UPDATE questions_answers SET category_id =%s "
                        "WHERE id BETWEEN %s AND %s")
            val = (category_id, 58, 67)
            cursor.execute(sql_query, val)
        
        elif (converted_question[0] >= 68) and (converted_question[0] < 78 ):
            category_id = 8
            sql_query = ("UPDATE questions_answers SET category_id =%s "
                        "WHERE id BETWEEN %s AND %s")
            val = (category_id, 68, 77)
            cursor.execute(sql_query, val)

        elif (converted_question[0] >= 78) and (converted_question[0] < 88 ):
            category_id = 9
            sql_query = ("UPDATE questions_answers SET category_id =%s "
                        "WHERE id BETWEEN %s AND %s")
            val = (category_id, 78, 87)
            cursor.execute(sql_query, val)

        elif (converted_question[0] >= 88) and (converted_question[0] < 98 ):
            category_id = 10
            sql_query = ("UPDATE questions_answers SET category_id =%s "
                        "WHERE id BETWEEN %s AND %s")
            val = (category_id, 88, 97)
            cursor.execute(sql_query, val)

        elif (converted_question[0] >= 98) and (converted_question[0] < 108 ):
            category_id = 11
            sql_query = ("UPDATE questions_answers SET category_id =%s "
                        "WHERE id BETWEEN %s AND %s")
            val = (category_id, 98, 107)
            cursor.execute(sql_query, val)
        
        elif (converted_question[0] >= 108) and (converted_question[0] < 118 ):
            category_id = 12
            sql_query = ("UPDATE questions_answers SET category_id =%s "
                        "WHERE id BETWEEN %s AND %s")
            val = (category_id, 108, 117)
            cursor.execute(sql_query, val)
        
        elif (converted_question[0] >= 118) and (converted_question[0] < 127 ):
            category_id = 13
            sql_query = ("UPDATE questions_answers SET category_id =%s "
                        "WHERE id BETWEEN %s AND %s")
            val = (category_id, 118, 126)
            cursor.execute(sql_query, val)
   
        else:
            print("Haz una segunda comprobación")
            
    connection.commit()
    print(cursor.rowcount, "record(s) affected")
    
    connection.close()
    return "Categorías pobladas!"


def OptimizeCategorizeQuestions():
    try:
        connection = getConnection()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM questions_answers")
        all_questions_list = cursor.fetchall()
        connection.close()
    except Exception as e:
        print(type(e).__name__, e)
        return e

    connection = getConnection()
    cursor = connection.cursor()

    categories_ranges = [
        (1, 9), (2, 19), (3, 29), (4, 40), (5, 49),
        (6, 57), (7, 67), (8, 77), (9, 87), (10, 97),
        (11, 107), (12, 117), (13, 126)
    ]

    for converted_question in all_questions_list:
        question_id = converted_question[0]

        for category_id, (start, end) in enumerate(categories_ranges, start=1):
            if start <= question_id < end:
                sql_query = ("UPDATE questions_answers SET category_id = %s "
                             "WHERE id BETWEEN %s AND %s")
                val = (category_id, start, end - 1)
                cursor.execute(sql_query, val)
                break
        else:
            print("Haz una segunda comprobación")

    connection.commit()
    print(cursor.rowcount, "record(s) affected")
    connection.close()
    return "Categorías pobladas!"
    
            
