from app import app, db
from models import RestaurantPizza, Pizza, Restaurant

with app.app_context():  # Ensure the app context is active
    try:
        print("Deleting data...")

        # Ensure that you're using the session properly
        db.session.query(RestaurantPizza).delete()  # Delete all entries in RestaurantPizza first
        db.session.query(Pizza).delete()  # Delete all entries in Pizza
        db.session.query(Restaurant).delete()  # Delete all entries in Restaurant
        
        # Commit the transaction to the database
        db.session.commit()

        print("Creating restaurants...")
        shack = Restaurant(name="Karen's Pizza Shack", address='address1')
        bistro = Restaurant(name="Sanjay's Pizza", address='address2')
        palace = Restaurant(name="Kiki's Pizza", address='address3')
        restaurants = [shack, bistro, palace]

        print("Creating pizzas...")
        cheese = Pizza(name="Emma", ingredients="Dough, Tomato Sauce, Cheese")
        pepperoni = Pizza(name="Geri", ingredients="Dough, Tomato Sauce, Cheese, Pepperoni")
        california = Pizza(name="Melanie", ingredients="Dough, Sauce, Ricotta, Red peppers, Mustard")
        pizzas = [cheese, pepperoni, california]

        print("Creating RestaurantPizza associations...")
        pr1 = RestaurantPizza(restaurant=shack, pizza=cheese, price=1)
        pr2 = RestaurantPizza(restaurant=bistro, pizza=pepperoni, price=4)
        pr3 = RestaurantPizza(restaurant=palace, pizza=california, price=5)
        restaurantPizzas = [pr1, pr2, pr3]

        # Add all the objects to the session
        db.session.add_all(restaurants)
        db.session.add_all(pizzas)
        db.session.add_all(restaurantPizzas)

        # Commit the transaction
        db.session.commit()

        print("Seeding done!")

    except Exception as e:
        db.session.rollback()  # Rollback on error
        print(f"An error occurred: {e}")
