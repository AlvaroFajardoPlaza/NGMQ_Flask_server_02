from flask import Flask, request
from flask_cors import CORS, cross_origin
from flask_jwt_extended import JWTManager

import config
import mysql.connector

# Importamos la configuración de nuestra bbdd
from src.database.db_mysql import getConnection

# Importamos las funciones de los módulos de scrapperBot, auth y trivia
from src.ScrapperBot.scraper_bot import OptimizeCategorizeQuestions, scrapeCategories, scrapeQuestionsAnswers, categorizeQuestions
from src.AuthMod.auth_module import decodeToken, getAllUsers, registerUser, loginUser, decodeToken, logOut
from src.TriviaMod.trivia_module import categorizedTriviaTest, getAnswers, getCategories, randomTriviaTest, updateUserScore


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
    # print("Pasamos los datos del login: ", user_data)
    return loginUser(user_data)


@cross_origin
@app.route("/me", methods=['GET', 'POST'])
def decode_token():
    token_data = request.json
    return decodeToken(token_data)


@cross_origin
@app.route("/logout", methods=['GET'])
def log_user_out():
    return logOut()



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
    
    categories_array = request.json # { 'categories': [...]}
    print("Estas son las categorias que deben de entrar en la función: ", categories_array)

    result = categorizedTriviaTest(categories_array)
    return result

# Esta ruta tiene que manejar las respuestas del trivia y modificar el score del usuario
@cross_origin
@app.route("/get_trivia_answers", methods=['GET', 'POST'])
def get_answers_for_trivia():

    userAnswers = request.json
    user_token: dict = {
        'token': request.headers.get('Authorization')
    }
        
    result: str = str(getAnswers(userAnswers))
    print("Este es el resultado que mandamos al front:", result, type(result))

    # La primera parte de la función es correcta, ya hemos enviado la respuesta al usuario. Ahora tenemos que manejar la segunda parte:
    updateUserScore(user_token, result)

    return result


#### Llamada al programa principal
if __name__ == "__main__":

    app.run(debug=True)

