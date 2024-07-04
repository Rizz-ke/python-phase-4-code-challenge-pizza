#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response, jsonify
from flask_restful import Api, Resource
import os
import warnings

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False  # Updated config key

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)

# Suppress SQLAlchemy 2.0 deprecation warnings
warnings.filterwarnings("ignore", category=DeprecationWarning, module="sqlalchemy")

@app.route("/")
def index():
    return "<h1>Code challenge</h1>"

class RestaurantListResource(Resource):
    def get(self):
        restaurants = Restaurant.query.all()
        return jsonify([restaurant.to_dict() for restaurant in restaurants])

    def post(self):
        data = request.get_json()
        new_restaurant = Restaurant(
            name=data['name'],
            address=data['address']
        )
        db.session.add(new_restaurant)
        db.session.commit()
        return make_response(jsonify(new_restaurant.to_dict()), 201)

class RestaurantResource(Resource):
    def get(self, id):
        restaurant = db.session.get(Restaurant, id)
        if restaurant is None:
            return make_response(jsonify({"error": "Restaurant not found"}), 404)
        restaurant_dict = restaurant.to_dict()
        restaurant_dict['restaurant_pizzas'] = [
            rp.to_dict() for rp in restaurant.pizzas
        ]
        return jsonify(restaurant_dict)

    def patch(self, id):
        data = request.get_json()
        restaurant = db.session.get(Restaurant, id)
        if restaurant is None:
            return make_response(jsonify({"error": "Restaurant not found"}), 404)
        if 'name' in data:
            restaurant.name = data['name']
        if 'address' in data:
            restaurant.address = data['address']
        db.session.commit()
        return make_response(jsonify(restaurant.to_dict()), 200)

    def delete(self, id):
        restaurant = db.session.get(Restaurant, id)
        if restaurant is None:
            return make_response(jsonify({"error": "Restaurant not found"}), 404)
        db.session.delete(restaurant)
        db.session.commit()
        return make_response('', 204)

class PizzaListResource(Resource):
    def get(self):
        pizzas = Pizza.query.all()
        return jsonify([pizza.to_dict() for pizza in pizzas])

    def post(self):
        data = request.get_json()
        new_pizza = Pizza(
            name=data['name'],
            ingredients=data['ingredients']
        )
        db.session.add(new_pizza)
        db.session.commit()
        return make_response(jsonify(new_pizza.to_dict()), 201)

class PizzaResource(Resource):
    def get(self, id):
        pizza = db.session.get(Pizza, id)
        if pizza is None:
            return make_response(jsonify({"error": "Pizza not found"}), 404)
        return jsonify(pizza.to_dict())

    def patch(self, id):
        data = request.get_json()
        pizza = db.session.get(Pizza, id)
        if pizza is None:
            return make_response(jsonify({"error": "Pizza not found"}), 404)
        if 'name' in data:
            pizza.name = data['name']
        if 'ingredients' in data:
            pizza.ingredients = data['ingredients']
        db.session.commit()
        return make_response(jsonify(pizza.to_dict()), 200)

    def delete(self, id):
        pizza = db.session.get(Pizza, id)
        if pizza is None:
            return make_response(jsonify({"error": "Pizza not found"}), 404)
        db.session.delete(pizza)
        db.session.commit()
        return make_response('', 204)

class RestaurantPizzaResource(Resource):
    def post(self):
        data = request.get_json()

        # Check if all required fields are present
        required_fields = ['price', 'restaurant_id', 'pizza_id']
        missing_fields = [field for field in required_fields if field not in data]

        if missing_fields:
            return make_response(jsonify({"errors": [f"Missing fields: {', '.join(missing_fields)}"]}), 400)

        # Check if the price is a positive number between 1 and 30
        if not (1 <= data['price'] <= 30):
            return make_response(jsonify({"errors": ["validation errors"]}), 400)

        # Check if restaurant_id and pizza_id are valid
        restaurant = db.session.get(Restaurant, data['restaurant_id'])
        pizza = db.session.get(Pizza, data['pizza_id'])

        if not restaurant:
            return make_response(jsonify({"errors": ["Restaurant not found"]}), 404)
        if not pizza:
            return make_response(jsonify({"errors": ["Pizza not found"]}), 404)

        try:
            new_restaurant_pizza = RestaurantPizza(
                price=data['price'],
                restaurant_id=data['restaurant_id'],
                pizza_id=data['pizza_id']
            )
            db.session.add(new_restaurant_pizza)
            db.session.commit()
            return make_response(jsonify(new_restaurant_pizza.to_dict()), 201)
        except Exception as e:
            return make_response(jsonify({"errors": ["An error occurred"]}), 400)

api.add_resource(RestaurantListResource, '/restaurants')
api.add_resource(RestaurantResource, '/restaurants/<int:id>')
api.add_resource(PizzaListResource, '/pizzas')
api.add_resource(PizzaResource, '/pizzas/<int:id>')
api.add_resource(RestaurantPizzaResource, '/restaurant_pizzas')

if __name__ == "__main__":
    app.run(port=5555, debug=True)
