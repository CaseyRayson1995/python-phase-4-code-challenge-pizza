from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from models import db, Restaurant, Pizza, RestaurantPizza

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'  # Change to your database URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
migrate = Migrate(app, db)

# GET /restaurants
@app.route('/restaurants', methods=['GET'])
def get_restaurants():
    restaurants = Restaurant.query.all()
    return jsonify([restaurant.to_dict(only=["id", "name", "address"]) for restaurant in restaurants])

# GET /restaurants/<int:id>
@app.route('/restaurants/<int:id>', methods=['GET'])
def get_restaurant_by_id(id):
    restaurant = db.session.get(Restaurant, id)  # Use session.get instead of query.get
    if restaurant:
        return jsonify({
            "id": restaurant.id,
            "name": restaurant.name,
            "address": restaurant.address,
            "restaurant_pizzas": [rp.to_dict() for rp in restaurant.restaurant_pizzas]
        })
    else:
        return jsonify({"error": "Restaurant not found"}), 404

# DELETE /restaurants/<int:id>
@app.route('/restaurants/<int:id>', methods=['DELETE'])
def delete_restaurant(id):
    restaurant = db.session.get(Restaurant, id)  # Use session.get instead of query.get
    if restaurant:
        # Delete associated RestaurantPizzas first
        for rp in restaurant.restaurant_pizzas:
            db.session.delete(rp)
        db.session.delete(restaurant)
        db.session.commit()
        return '', 204
    else:
        return jsonify({"error": "Restaurant not found"}), 404

# GET /pizzas
@app.route('/pizzas', methods=['GET'])
def get_pizzas():
    pizzas = Pizza.query.all()
    return jsonify([pizza.to_dict(only=["id", "name", "ingredients"]) for pizza in pizzas])

# POST /restaurant_pizzas
@app.route('/restaurant_pizzas', methods=['POST'])
def create_restaurant_pizza():
    data = request.get_json()
    price = data.get("price")
    pizza_id = data.get("pizza_id")
    restaurant_id = data.get("restaurant_id")

    if not price or not pizza_id or not restaurant_id:
        return jsonify({"errors": ["validation errors"]}), 400  # Generalized error message

    # Validation for price
    if price < 1 or price > 30:
        return jsonify({"errors": ["validation errors"]}), 400  # Generalized error message

    pizza = db.session.get(Pizza, pizza_id)  # Use session.get instead of query.get
    restaurant = db.session.get(Restaurant, restaurant_id)  # Use session.get instead of query.get

    if pizza and restaurant:
        restaurant_pizza = RestaurantPizza(price=price, pizza_id=pizza_id, restaurant_id=restaurant_id)
        db.session.add(restaurant_pizza)
        db.session.commit()
        return jsonify({
            "id": restaurant_pizza.id,
            "price": restaurant_pizza.price,
            "pizza": pizza.to_dict(only=["id", "name", "ingredients"]),
            "restaurant": restaurant.to_dict(only=["id", "name", "address"]),
            "pizza_id": pizza_id,
            "restaurant_id": restaurant_id
        }), 201
    else:
        return jsonify({"errors": ["validation errors"]}), 400  # Generalized error message


if __name__ == "__main__":
    app.run(debug=True)
