from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate  # Add Flask-Migrate for database migrations
from sqlalchemy.orm import relationship

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///yourdatabase.db'  # Adjust database URI as needed
db = SQLAlchemy(app)
migrate = Migrate(app, db)  # Initialize Flask-Migrate

# Models

class Restaurant(db.Model):
    __tablename__ = 'restaurants'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    address = db.Column(db.String)

    # Relationship with RestaurantPizza
    restaurant_pizzas = relationship("RestaurantPizza", back_populates="restaurant")

    def to_dict(self, only=None):
        data = {
            "id": self.id,
            "name": self.name,
            "address": self.address
        }
        if only:
            return {key: data[key] for key in only}
        return data

    def __repr__(self):
        return f"<Restaurant {self.name}>"

class Pizza(db.Model):
    __tablename__ = 'pizzas'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    ingredients = db.Column(db.String)

    # Relationship with RestaurantPizza
    restaurant_pizzas = relationship("RestaurantPizza", back_populates="pizza")

    def to_dict(self, only=None):
        data = {
            "id": self.id,
            "name": self.name,
            "ingredients": self.ingredients
        }
        if only:
            return {key: data[key] for key in only}
        return data

    def __repr__(self):
        return f"<Pizza {self.name}>"

class RestaurantPizza(db.Model):
    __tablename__ = 'restaurant_pizzas'

    id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Integer, nullable=False)
    pizza_id = db.Column(db.Integer, db.ForeignKey('pizzas.id'))
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurants.id'))

    # Relationships
    pizza = relationship("Pizza", back_populates="restaurant_pizzas")
    restaurant = relationship("Restaurant", back_populates="restaurant_pizzas")

    def to_dict(self):
        return {
            "id": self.id,
            "price": self.price,
            "pizza_id": self.pizza_id,
            "restaurant_id": self.restaurant_id,
            "pizza": self.pizza.to_dict(only=["id", "name", "ingredients"]),
            "restaurant": self.restaurant.to_dict(only=["id", "name", "address"])
        }

    def __repr__(self):
        return f"<RestaurantPizza ${self.price}>"

# Routes

@app.route('/restaurants', methods=['GET'])
def get_restaurants():
    restaurants = Restaurant.query.all()
    return jsonify([restaurant.to_dict(only=["id", "name", "address"]) for restaurant in restaurants])

@app.route('/restaurants/<int:id>', methods=['GET'])
def get_restaurant_by_id(id):
    restaurant = Restaurant.query.get(id)
    if restaurant:
        return jsonify({
            "id": restaurant.id,
            "name": restaurant.name,
            "address": restaurant.address,
            "restaurant_pizzas": [rp.to_dict() for rp in restaurant.restaurant_pizzas]
        })
    else:
        return jsonify({"error": "Restaurant not found"}), 404

@app.route('/restaurants/<int:id>', methods=['DELETE'])
def delete_restaurant(id):
    restaurant = Restaurant.query.get(id)
    if restaurant:
        # Delete associated RestaurantPizzas first
        for rp in restaurant.restaurant_pizzas:
            db.session.delete(rp)
        db.session.delete(restaurant)
        db.session.commit()
        return '', 204  
    else:
        return jsonify({"error": "Restaurant not found"}), 404

@app.route('/pizzas', methods=['GET'])
def get_pizzas():
    pizzas = Pizza.query.all()
    return jsonify([pizza.to_dict(only=["id", "name", "ingredients"]) for pizza in pizzas])

@app.route('/restaurant_pizzas', methods=['POST'])
def create_restaurant_pizza():
    data = request.get_json()

    # Validate required fields
    price = data.get("price")
    pizza_id = data.get("pizza_id")
    restaurant_id = data.get("restaurant_id")

    if not price or not pizza_id or not restaurant_id:
        return jsonify({"errors": ["Price, pizza_id, and restaurant_id are required."]}), 400

    # Validation for price
    if price < 1 or price > 30:
        return jsonify({"errors": ["Price must be between 1 and 30."]}), 400

    pizza = Pizza.query.get(pizza_id)
    restaurant = Restaurant.query.get(restaurant_id)

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
        return jsonify({"errors": ["Invalid pizza or restaurant ID."]}), 400

if __name__ == "__main__":
    app.run(debug=True)

# 200: OK – The request was successful.
# 201: Created – The resource was successfully created.
# 204: No Content – The request was successful, but there is no content to return.
# 400: Bad Request – The server could not understand the request due to invalid syntax.
# 404: Not Found – The requested resource could not be found.
# 422: Unprocessable Entity – The server understands the request, but it can't process the instructions
