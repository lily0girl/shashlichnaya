from flask import Flask, render_template, request, redirect, session
from online_restaurant_db import db, Users, Menu, Orders, Reservation
from werkzeug.utils import secure_filename
import os


app = Flask(__name__)

app.secret_key = "shashlik"
app.config["UPLOAD_FOLDER"] = "static/menu"


app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///restaurant.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)


with app.app_context():

    db.create_all()

    if Menu.query.count() == 0:

        dish1 = Menu(
            name="Шашлик зі свинини",
            photo="https://images.unsplash.com/photo-1529193591184-b1d58069ecdd",
            description="Соковитий шашлик зі свинини, приготований на вугіллі.",
            ingredients="Свинина, цибуля, спеції",
            price=12,
            weight=250
        )

        dish2 = Menu(
            name="Шашлик з курки",
            photo="https://images.unsplash.com/photo-1532550907401-a500c9a57435",
            description="Ніжний курячий шашлик з ароматними спеціями.",
            ingredients="Куряче філе, цибуля, спеції",
            price=10,
            weight=250
        )

        dish3 = Menu(
            name="Люля-кебаб",
            photo="https://images.unsplash.com/photo-1558030006-450675393462",
            description="Соковитий люля-кебаб з яловичини.",
            ingredients="Яловичина, зелень, спеції",
            price=11,
            weight=220
        )

        dish4 = Menu(
            name="Овочі гриль",
            photo="https://images.unsplash.com/photo-1544025162-d76694265947",
            description="Свіжі овочі, приготовані на грилі.",
            ingredients="Перець, кабачок, помідори",
            price=6,
            weight=180
        )

        dish5 = Menu(
            name="Картопля по-селянськи",
            photo="https://images.unsplash.com/photo-1518013431117-eb1465fa5752",
            description="Ароматна картопля з хрусткою скоринкою.",
            ingredients="Картопля, часник, спеції",
            price=5,
            weight=200
        )

        db.session.add_all([
            dish1,
            dish2,
            dish3,
            dish4,
            dish5
        ])

        db.session.commit()


@app.route("/")
def index():

    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        old_user = Users.query.filter_by(username=username).first()

        if old_user:
            return "Такий користувач вже існує"

        user = Users(
            username=username,
            password=password
        )

        db.session.add(user)
        db.session.commit()

        return redirect("/login")

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        user = Users.query.filter_by(
            username=username,
            password=password
        ).first()

        if user:

            session["user_id"] = user.id
            session["username"] = user.username

            return redirect("/")

        return "Неправильний логін або пароль"

    return render_template("login.html")


@app.route("/logout")
def logout():

    session.pop("user_id", None)
    session.pop("username", None)

    return redirect("/")


@app.route("/menu")
def menu():

    dishes = Menu.query.filter_by(active=True).all()

    return render_template(
        "menu.html",
        dishes=dishes
    )


@app.route("/position/<int:id>")
def position(id):

    dish = Menu.query.get(id)

    return render_template(
        "position.html",
        dish=dish
    )


@app.route("/add_to_cart/<int:id>")
def add_to_cart(id):

    cart = session.get("cart", {})

    dish_id = str(id)

    if dish_id in cart:

        if cart[dish_id] < 10:
            cart[dish_id] += 1

    else:

        cart[dish_id] = 1

    session["cart"] = cart

    print("Кошик:", cart)

    return redirect("/menu")


@app.route("/cart")
def cart():

    cart_data = session.get("cart", {})

    dishes = []

    total = 0

    for dish_id, quantity in cart_data.items():

        dish = Menu.query.get(int(dish_id))

        if dish:

            price = dish.price * quantity
            total += price

            dishes.append({
                "dish": dish,
                "quantity": quantity,
                "price": price
            })

    return render_template(
        "cart.html",
        dishes=dishes,
        total=total
    )


@app.route("/increase/<int:id>")
def increase(id):

    cart = session.get("cart", {})

    dish_id = str(id)

    if dish_id in cart:

        if cart[dish_id] < 10:
            cart[dish_id] += 1

    session["cart"] = cart

    return redirect("/cart")


@app.route("/decrease/<int:id>")
def decrease(id):

    cart = session.get("cart", {})

    dish_id = str(id)

    if dish_id in cart:

        if cart[dish_id] > 1:
            cart[dish_id] -= 1

    session["cart"] = cart

    return redirect("/cart")


@app.route("/remove/<int:id>")
def remove(id):

    cart = session.get("cart", {})

    dish_id = str(id)

    if dish_id in cart:
        del cart[dish_id]

    session["cart"] = cart

    return redirect("/cart")


@app.route("/create_order")
def create_order():

    if "user_id" not in session:
        return redirect("/login")

    cart = session.get("cart", {})

    if not cart:
        return redirect("/cart")

    for dish_id, quantity in cart.items():

        dish = Menu.query.get(int(dish_id))

        if dish:

            order = Orders(
                user_id=session["user_id"],
                dish_name=dish.name,
                quantity=quantity,
                total_price=dish.price * quantity
            )

            db.session.add(order)

    db.session.commit()

    session["cart"] = {}

    return redirect("/orders")


@app.route("/orders")
def orders():

    if "user_id" not in session:
        return redirect("/login")

    user_orders = Orders.query.filter_by(
        user_id=session["user_id"]
    ).all()

    return render_template(
        "orders.html",
        orders=user_orders
    )


@app.route("/order/<int:id>")
def order(id):

    if "user_id" not in session:
        return redirect("/login")

    user_order = Orders.query.filter_by(
        id=id,
        user_id=session["user_id"]
    ).first()

    if not user_order:
        return redirect("/orders")

    return render_template(
        "order.html",
        order=user_order
    )


@app.route("/cancel_order/<int:id>")
def cancel_order(id):

    if "user_id" not in session:
        return redirect("/login")

    user_order = Orders.query.filter_by(
        id=id,
        user_id=session["user_id"]
    ).first()

    if user_order:

        db.session.delete(user_order)
        db.session.commit()

    return redirect("/orders")


@app.route("/reservation", methods=["GET", "POST"])
def reservation():

    if "user_id" not in session:
        return redirect("/login")

    if request.method == "POST":

        date = request.form["date"]
        time = request.form["time"]
        guests = request.form["guests"]

        new_reservation = Reservation(
            user_id=session["user_id"],
            date=date,
            time=time,
            guests=guests
        )

        db.session.add(new_reservation)
        db.session.commit()

        return redirect("/")

    return render_template("reservation.html")


@app.route("/admin/reservations")
def admin_reservations():

    if "username" not in session or session["username"] != "admin":
        return "Доступ заборонено"

    reservations = Reservation.query.all()

    return render_template(
        "admin_reservations.html",
        reservations=reservations
    )


@app.route("/admin/reservations/delete/<int:id>")
def delete_reservation(id):

    if "username" not in session or session["username"] != "admin":
        return "Доступ заборонено"

    reservation = Reservation.query.get(id)

    if reservation:

        db.session.delete(reservation)
        db.session.commit()

    return redirect("/admin/reservations")



@app.route("/add_position", methods=["GET", "POST"])
def add_position():

    if "username" not in session or session["username"] != "Admin":
        return "Доступ заборонено"

    if request.method == "POST":

        name = request.form["name"]
        description = request.form["description"]
        ingredients = request.form["ingredients"]
        price = float(request.form["price"])
        weight = int(request.form["weight"])

        photo = request.files["photo"]

        filename = secure_filename(photo.filename)

        photo.save(
            os.path.join(
                app.config["UPLOAD_FOLDER"],
                filename
            )
        )

        dish = Menu(
            name=name,
            photo="/static/menu/" + filename,
            description=description,
            ingredients=ingredients,
            price=price,
            weight=weight,
            active=True
        )

        db.session.add(dish)
        db.session.commit()

        return redirect("/menu")

    return render_template("add_position.html")


if __name__ == "__main__":
    app.run(debug=True)