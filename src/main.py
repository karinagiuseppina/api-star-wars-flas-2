"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Planet, Character
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_CONNECTION_STRING')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/user', methods=['GET'])
def handle_hello():

    response_body = {
        "msg": "Hello, this is your GET /user response "
    }

    return jsonify(response_body), 200

@app.route('/create', methods=['GET'])
def create():
    user = User(username='Karina', email = 'prueba@example.com', password='1')
    planet = Planet (name='Earth')
    planet1 = Planet (name='Pluton')
    character1 = Character(name='Luke Skywalker')
    character2 = Character (name='Princess Leia')
    user.favorite_planets.append(planet)
    user.favorite_planets.append(planet1)
    user.favorite_characters.append(character1)
    user.favorite_characters.append(character2)

    db.session.add(user)
    db.session.commit()

    return jsonify([]), 200
    
@app.route('/people', methods=['GET'])
def get_characters():
    characters = Character.query.all()
    characters = list(map (lambda character: character.serialize(), characters))
    return jsonify(characters), 200

@app.route('/people/<int:people_id>', methods=['GET'])
def get_character(people_id):
    character = Character.query.get(people_id)
    return jsonify(character.serialize()), 200

@app.route('/planets', methods=['GET'])
def get_planets():
    planets = Planet.query.all()
    planets = list(map (lambda planet: planet.serialize(), planets))
    return jsonify(planets), 200

@app.route('/planets/<int:planet_id>', methods=['GET'])
def get_planet(planet_id):
    planet = Planet.query.get(planet_id)
    return jsonify(planet.serialize()), 200

@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    users = list(map (lambda user: user.serialize(), users))
    return jsonify(users), 200

@app.route('/users/<int:user_id>/favorites', methods=['GET'])
def get_user_favorites(user_id):
    user = User.query.get(user_id)
    favorites = []
    for character in user.favorite_characters:
        favorites.append(character.name)
    for planet in user.favorite_planets:
        favorites.append(planet.name)

    return jsonify(favorites), 200

@app.route('/favorite/planet/<int:planet_id>', methods=['POST'])
def add_favorite_planet(planet_id):
    planet = Planet.query.get(planet_id)
    user = User.query.get(1)
    user.favorite_planets.append(planet_id)
    db.session.commit()
    return jsonify(planet.serialize()), 200

@app.route('/favorite/people/<int:character_id>', methods=['POST'])
def add_favorite_character(character_id):
    character = Character.query.get(character_id)
    user = User.query.get(1)
    user.favorite_characters.append(character_id)
    db.session.commit()
    return jsonify(character.serialize()), 200

@app.route('/favorite/people/<int:character_id>', methods=['DELETE'])
def delete_favorite_character(character_id):
    character = Character.query.get(character_id)
    user = User.query.get(1)
    character_position = user.favorite_characters.index(character)
    user.favorite_characters.pop(character_position)
    db.session.commit()
    return jsonify(character.serialize()), 200

@app.route('/favorite/planets/<int:planet_id>', methods=['DELETE'])
def delete_favorite_planet(planet_id):
    planet = Planet.query.get(planet_id)
    user = User.query.get(1)
    planet_position = user.favorite_planets.index(planet)
    user.favorite_planets.pop(planet_position)
    db.session.commit()
    return jsonify(planet.serialize()), 200
       
# this only runs if `$ python src/main.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
