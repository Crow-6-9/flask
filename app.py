from flask import Flask, render_template, request, redirect, session
from flask_mysqldb import MySQL

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# MySQL configuration
app.config['MYSQL_HOST'] = 'localhost'  # Change 'localhost' or your host address as needed
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'ecom'

mysql = MySQL(app)

# Index Route
@app.route('/')
def index():
    return render_template('index.html')

# Signup Route
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        cursor = mysql.connection.cursor()
        cursor.execute('INSERT INTO users (username, password) VALUES (%s, %s)', (username, password))
        mysql.connection.commit()
        cursor.close()

        return redirect('/login')
    return render_template('signup.html')

# Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM users WHERE username = %s AND password = %s', (username, password))
        user = cursor.fetchone()

        if user:
            session['username'] = username
            session['cart'] = []  # Initialize an empty cart for the session
            return redirect('/home')
        else:
            return 'Invalid username or password'
    return render_template('login.html')

# Home Route
@app.route('/home', methods=['GET', 'POST'])
def home():
    if 'username' not in session:
        return redirect('/login')

    # Static products list
    products = [
        {'id': 1, 'name': 'Shirt', 'price': 25.0, 'quantity': 10},
        {'id': 2, 'name': 'Jacket', 'price': 50.0, 'quantity': 5},
        {'id': 3, 'name': 'Pants', 'price': 30.0, 'quantity': 8},
    ]

    # Handle adding products to the cart
    if request.method == 'POST':
        product_id = request.form.get('product_id')
        quantity = request.form.get('quantity')

        if product_id and quantity and quantity.isdigit():  # Check if the fields are valid
            quantity = int(quantity)  # Convert to integer

            # Find the product based on ID
            product = next((prod for prod in products if prod['id'] == int(product_id)), None)

            if product and quantity <= product['quantity']:  # Check if the product is in stock
                # Add to cart
                cart_item = next((item for item in session['cart'] if item['name'] == product['name']), None)
                if cart_item:
                    cart_item['quantity'] += quantity  # Update quantity if item exists
                else:
                    session['cart'].append({
                        'name': product['name'],
                        'price': product['price'],
                        'quantity': quantity
                    })
                return redirect('/cart')

    return render_template('home.html', products=products)

# Cart Route
@app.route('/cart', methods=['GET', 'POST'])
def cart():
    if 'username' not in session:
        return redirect('/login')

    cart_items = session.get('cart', [])
    total = sum(item['quantity'] * item['price'] for item in cart_items)

    if request.method == 'POST':
        # Place Order
        order_details = ", ".join([f"{item['name']} (Qty: {item['quantity']})" for item in cart_items])
        return render_template('order_placed.html', order_details=order_details, total=total)

    return render_template('cart.html', cart_items=cart_items, total=total)

# Logout Route
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

if __name__ == '__main__':
    app.run(debug=True)
