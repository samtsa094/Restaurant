from flask import Flask, render_template, request, redirect, flash, session
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb+srv://vaivai:1RJJ1JifgOc8VCos@cluster0.ualrt.mongodb.net/Restaurant"
app.config["SECRET_KEY"] = "safe^&*hdgahksdg"
mongo = PyMongo(app)
@app.route("/", methods = ["GET", "POST"])
def index():
    if "user_id" not in session:
        session["user_id"] = mongo.db.Carts.insert_one({"cart": []}).inserted_id
    cart_count = len(mongo.db.Carts.find_one({"_id": ObjectId(session["user_id"])})["cart"])
    foods = list(mongo.db.Foods.find())
    return render_template("index.html", foods = foods, cart_count = cart_count)
@app.route("/owner_shop", methods = ["GET", "POST"])
def owner_shop():
    foods = list(mongo.db.Foods.find())
    return render_template("owner_shop.html", foods = foods)
@app.route("/login", methods = ["GET", "POST"])
def login():
    if request.form.get("email") == "samtsa094@fusdk12.net":
        if request.form.get("password") == "207Emory!":
            flash("Login successful")
            return redirect("/owner_shop")
        else:
            flash("Password is incorrect")
            return redirect("/")
    return redirect("/")
@app.route("/logout", methods = ["GET", "POST"])
def logout():
    session.clear()
    flash("Logout successful")
    return redirect("/")
@app.route("/add_food", methods = ["GET", "POST"])
def add_food():
    flash("Food added successfully")
    form_id = request.form.get("form_id")
    if form_id == "add_food_form":
        document = {}
        document["name"] = request.form.get("name")
        document["description"] = request.form.get("description")
        document["price"] = int(request.form.get("price"))
        document["quantity"] = int(request.form.get("quantity"))
        document["link"] = request.form.get("link")
        mongo.db.Foods.insert_one(document)
        return redirect("/owner_shop")
@app.route("/add_stock/<id>", methods = ["GET", "POST"])
def add_stock(id):
    food = mongo.db.Foods.find_one({"_id": ObjectId(id)})
    flash(f"{request.form.get('quantity')} {food['name']}(s) added to stock")
    mongo.db.Foods.update_one({"_id": ObjectId(id)}, {"$inc": {"quantity": int(request.form.get("quantity"))}})
    return redirect("/owner_shop")
@app.route("/delete/<id>")
def delete(id):
    flash("Successfully deleted the food")
    mongo.db.Foods.delete_one({"_id": ObjectId(id)})
    return redirect("/owner_shop")
@app.route("/add_cart/<id>", methods = ["GET", "POST"])
def add_cart(id):
    mongo.db.Foods.update_one({"_id": ObjectId(id)}, {"$inc": {"quantity": -1 * int(request.form.get("quantity"))}})
    food = mongo.db.Foods.find_one({"_id": ObjectId(id)})
    flash(f"Successfully added {request.form.get('quantity')} {food['name']}(s) to your cart")
    food_to_add = {}
    food_to_add["name"] = food["name"]
    food_to_add["quantity"] = int(request.form.get("quantity"))
    food_to_add["price"] = food["price"]
    mongo.db.Carts.update_one({"_id": ObjectId(session["user_id"])}, {"$addToSet": {"cart": food_to_add}})
    return redirect("/")
@app.route("/view_cart", methods = ["GET", "POST"])
def view_cart():
    cart = mongo.db.Carts.find_one({"_id": ObjectId(session["user_id"])})["cart"]
    total = 0
    for i in cart:
        total += (i["quantity"] * i["price"])
    return render_template("checkout.html", cart = cart, total = total)
@app.route("/checkout", methods = ["GET", "POST"])
def checkout():
    session.pop("user_id")
    return redirect("/")
if __name__ == "__main__":
    app.run(debug = True)