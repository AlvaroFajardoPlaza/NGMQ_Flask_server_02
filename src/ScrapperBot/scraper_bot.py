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
        all_questions_list = cursor.fetchall()
        connection.close()
        
    except Exception as e:
        print(type(e).__name__, e)
        return e

    # print(type(all_questions_list))
    # print(all_questions_list)
    # Tenemos que trnasformar cada tupla en un array o lista
    
    connection = getConnection()
    cursor = connection.cursor()
    for question in all_questions_list:
        converted_question = list(question)

        try:
            category_id = 0 

            if 1 <= converted_question[0] < 11:
                category_id = 1
                cursor.execute("UPDATE questions_answers SET category_id=%s WHERE id>=1 AND id<11", category_id)
            elif 11 <= converted_question[0] < 21:
                category_id = 2
            elif 21 <= converted_question[0] < 31:
                category_id = 3 
            
            if 31 <= converted_question[0] < 42:
                category_id = 4
            elif 42 <= converted_question[0] < 51:
                category_id = 5
            elif 51 <= converted_question[0] < 59:
                category_id = 6 
            
            if 59 <= converted_question[0] < 69:
                category_id = 7
            elif 69 <= converted_question[0] < 79:
                category_id = 8
            elif 79 <= converted_question[0] < 89:
                category_id = 9

            if 89 <= converted_question[0] < 99:
                category_id = 10
            elif 99 <= converted_question[0] < 109:
                category_id = 11
            elif 109 <= converted_question[0] < 119:
                category_id = 12
            elif 119 <= converted_question[0] < 128:
                category_id = 13
            else:
                print("Haz una segunda comprobación")
 

        except Exception as e:
            print(type(e).__name__, e)
            return "{}".format(e)

        connection.commit()
        connection.close()
        return "Categorías pobladas!"
    

        #    try:
        #     if (converted_question[0] >= 1) and (converted_question[0] < 11):
        #         cursor.execute("INSERT INTO questions_answers (category_id) VALUES (1)")
        #     elif (converted_question[0] >= 11) and (converted_question[0] < 21):
        #         cursor.execute("INSERT INTO questions_answers (category_id) VALUES (2)")
        #     elif (converted_question[0] >= 21) and (converted_question[0] < 31):
        #         cursor.execute("INSERT INTO questions_answers (category_id) VALUES (3)")
            
        #     elif (converted_question[0] >= 31) and (converted_question[0] < 41):
        #         cursor.execute("INSERT INTO questions_answers (category_id) VALUES (4)")
        #     elif (converted_question[0] >= 41) and (converted_question[0] < 50):
        #         cursor.execute("INSERT INTO questions_answers (category_id) VALUES (5)")
        #     elif (converted_question[0] >= 50) and (converted_question[0] < 59):
        #         cursor.execute("INSERT INTO questions_answers (category_id) VALUES (6)")
            
        #     elif (converted_question[0] >= 59) and (converted_question[0] < 69):
        #         cursor.execute("INSERT INTO questions_answers (category_id) VALUES (7)")
        #     elif (converted_question[0] >= 69) and (converted_question[0] < 79):
        #         cursor.execute("INSERT INTO questions_answers (category_id) VALUES (8)")
        #     elif (converted_question[0] >= 79) and (converted_question[0] < 89):
        #         cursor.execute("INSERT INTO questions_answers (category_id) VALUES (9)")
            
        #     elif (converted_question[0] >= 89) and (converted_question[0] < 99):
        #         cursor.execute("INSERT INTO questions_answers (category_id) VALUES (10)")
        #     elif (converted_question[0] >= 99) and (converted_question[0] < 109):
        #         cursor.execute("INSERT INTO questions_answers (category_id) VALUES (11)")
        #     elif (converted_question[0] >= 109) and (converted_question[0] < 119):
        #         cursor.execute("INSERT INTO questions_answers (category_id) VALUES (12)")
        #     elif (converted_question[0] >= 119) and (converted_question[0] < 128):
        #         cursor.execute("INSERT INTO questions_answers (category_id) VALUES (13)")
        #     else: 
        #         print("Revisa los ids de las preguntas. Algo fue mal")
            
