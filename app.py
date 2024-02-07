from flask import Flask
from flask_cors import CORS, cross_origin
import config
import mysql.connector

# Importamos la configuración de nuestra bbdd
from src.database.db_mysql import getConnection

# Importamos las funciones de los módulos de scrapperBot, auth y trivia
from src.ScrapperBot.scraper_bot import OptimizeCategorizeQuestions, scrapeCategories, scrapeQuestionsAnswers, categorizeQuestions
from src.AuthMod.auth_module import getAllUsers, register_user, login_user
from src.TriviaMod.trivia_module import getCategories, randomTriviaTest


app = Flask(__name__)
CORS(app)


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
@app.route("/register", methods = ['POST'])
def register_new_user():
    return register_user()

@cross_origin
@app.route("/register", methods = ['POST'])
def login():
    return login_user()



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



#### Llamada al programa principal
if __name__ == "__main__":

    app.run(debug=True)

