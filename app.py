from flask import Flask, request
from flask_cors import CORS, cross_origin
from flask_jwt_extended import JWTManager

import config
import mysql.connector

# Importamos la configuración de nuestra bbdd
from src.database.db_mysql import getConnection

# Importamos las funciones de los módulos de scrapperBot, auth y trivia
from src.ScrapperBot.scraper_bot import OptimizeCategorizeQuestions, scrapeCategories, scrapeQuestionsAnswers, categorizeQuestions
from src.AuthMod.auth_module import getAllUsers, registerUser, loginUser
from src.TriviaMod.trivia_module import categorizedTriviaTest, getAnswers, getCategories, randomTriviaTest


app = Flask(__name__)
CORS(app)

app.config["JWT_SECRET_KEY"] = "Nebraska adora los bocaditos de atún"
jwt = JWTManager(app)



#### Primera ruta al inicial nuestro servidor Flask
@cross_origin
@app.route("/", methods=['GET'])
def home():
    return "Hey there! Si no has nutrido la bbdd, necesitas correr al scraper_bot para guardar todas las preguntas de la trivia!"

@cross_origin
@app.route("/users", methods=['GET'])
def get_all_users():
    return getAllUsers()


#### Rutas de autenticación de usuarios
@cross_origin
@app.route("/register", methods = ['GET', 'POST'])
def register_new_user():
    new_user_data = request.json
    # print("Estos son los datos que se envían por el form:", new_user_data)
    return registerUser(new_user_data)


@cross_origin
@app.route("/login", methods = ['GET','POST'])
def login_user():
    user_data = request.json
    return loginUser(user_data)



#### Rutas privadas para recopilar las categorias, así como las preguntas y respuestas para nuestra trivia. Vinculadas al scrapper_bot
@cross_origin
@app.route("/__scrape_categories", methods=['GET','POST'])
def populate_categories():
    result = scrapeCategories()
    return result

@cross_origin
@app.route("/__scrape_questions", methods=['GET','POST'])
def populate_questions_answers():
    result = scrapeQuestionsAnswers()
    return result

@cross_origin
@app.route("/categorize_questions", methods=['GET', 'POST'])
def populate_questions_categories():
    result = categorizeQuestions()
    # result = OptimizeCategorizeQuestions()
    return result


#### Rutas privadas generar las llamadas al Trivia Module
@cross_origin
@app.route("/categories", methods=['GET'])
def get_all_categories():
    result = getCategories()
    return result

@cross_origin
@app.route("/random_trivia", methods=['GET'])
def random_trivia_test():
    result = randomTriviaTest()
    return result


@cross_origin()
@app.route("/categorized_trivia", methods=['GET', 'POST'])
def categorized_trivia_test(): 
    
    categories_obj = request.json # { 'categories': [...]}
    print("Estas son las categorias que deben de entrar en la función: ", categories_obj)

    array_categories = categories_obj['categories']
    result = categorizedTriviaTest(array_categories)
    return result

# Esta ruta tiene que manejar las respuestas del trivia y modificar el score del usuario
@cross_origin
@app.route("/get_correct_answers", methods=['GET'])
def get_answers_for_trivia(trivia):
    result = getAnswers(trivia)
    return result



#### Llamada al programa principal
if __name__ == "__main__":

    app.run(debug=True)

