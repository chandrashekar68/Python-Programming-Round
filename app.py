from flask import Flask, request, jsonify, render_template, redirect,url_for
import sqlite3

app = Flask(__name__)

# Create database(SQLite)
def init_db():
    with sqlite3.connect('database.db') as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS seasonal_flavors (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            flavor TEXT NOT NULL UNIQUE)''')
        conn.execute('''CREATE TABLE IF NOT EXISTS ingredient_inventory (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            ingredient TEXT NOT NULL UNIQUE,
                            stock INTEGER NOT NULL CHECK(stock >= 0))''')
        conn.execute('''CREATE TABLE IF NOT EXISTS customer_suggestions (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            name TEXT NOT NULL,
                            flavor TEXT NOT NULL,
                            allergy_concerns TEXT)''')
        conn.commit()

@app.route('/')
def index():
    return render_template('index.html')

# Seasonal flavor offerings

@app.route('/add_flavor', methods=['GET', 'POST'])
def add_flavor():
    if request.method == 'POST':
        new_flavor = request.form.get('flavor')

        if not new_flavor:
            return render_template('add_flavor.html', error='Flavor name cannot be empty')

        with sqlite3.connect('database.db') as conn:
            cursor = conn.execute("SELECT * FROM seasonal_flavors WHERE flavor = ?", (new_flavor,))
            if cursor.fetchone():
                return render_template('add_flavor.html', error='Flavor already exists')

            conn.execute("INSERT INTO seasonal_flavors (flavor) VALUES (?)", (new_flavor,))
            conn.commit()
        return render_template('add_flavor.html', message='Flavor added successfully')

    return render_template('add_flavor.html')

@app.route('/list_flavors')
def list_flavors():
    with sqlite3.connect('database.db') as conn:
        cursor = conn.execute("SELECT * FROM seasonal_flavors")
        flavors = [{'id': row[0], 'flavor': row[1]} for row in cursor.fetchall()]
    return render_template('list_flavors.html', flavors=flavors)




# Ingredient inventory
@app.route('/add_ingredient', methods=['GET', 'POST'])
def add_ingredient():
    if request.method == 'POST':
        ingredient = request.form.get('ingredient')
        stock = request.form.get('stock')

        if not ingredient or stock is None:
            return render_template('add_ingredient.html', error='Ingredient name and stock are required')

        try:
            stock = int(stock)
        except ValueError:
            return render_template('add_ingredient.html', error='Stock must be a number')

        if stock < 0:
            return render_template('add_ingredient.html', error='Stock cannot be negative')

        with sqlite3.connect('database.db') as conn:
            cursor = conn.execute("SELECT * FROM ingredient_inventory WHERE ingredient = ?", (ingredient,))
            if cursor.fetchone():
                return render_template('add_ingredient.html', error='Ingredient already exists')

            conn.execute("INSERT INTO ingredient_inventory (ingredient, stock) VALUES (?, ?)", (ingredient, stock))
            conn.commit()
        return render_template('add_ingredient.html', message='Ingredient added successfully')

    return render_template('add_ingredient.html')

@app.route('/list_ingredients')
def list_ingredients():
    with sqlite3.connect('database.db') as conn:
        cursor = conn.execute("SELECT * FROM ingredient_inventory")
        ingredients = [{'id': row[0], 'ingredient': row[1], 'stock': row[2]} for row in cursor.fetchall()]
    return render_template('list_ingredients.html', ingredients=ingredients)




# Customer suggestions
@app.route('/add_suggestion', methods=['GET', 'POST'])
def add_suggestion():
    if request.method == 'POST':
        name = request.form.get('name')
        flavor = request.form.get('flavor')
        allergy_concerns = request.form.get('allergy_concerns')

        if not name or not flavor:
            return render_template('add_suggestion.html', error='Name and flavor are required')

        with sqlite3.connect('database.db') as conn:
            conn.execute("INSERT INTO customer_suggestions (name, flavor, allergy_concerns) VALUES (?, ?, ?)",
                         (name, flavor, allergy_concerns))
            conn.commit()
        return render_template('add_suggestion.html', message='Suggestion added successfully')

    return render_template('add_suggestion.html')

@app.route('/list_suggestions')
def list_suggestions():
    with sqlite3.connect('database.db') as conn:
        cursor = conn.execute("SELECT * FROM customer_suggestions")
        suggestions = [{'id': row[0], 'name': row[1], 'flavor': row[2], 'allergy_concerns': row[3]} 
                       for row in cursor.fetchall()]
    return render_template('list_suggestions.html', suggestions=suggestions)

@app.route('/delete_flavor/<int:flavor_id>', methods=['POST'])
def delete_flavor(flavor_id):
    with sqlite3.connect('database.db') as conn:
        cursor = conn.execute("SELECT * FROM seasonal_flavors WHERE id = ?", (flavor_id,))
        if cursor.fetchone() is None:
            return "Flavor not found", 404

        conn.execute("DELETE FROM seasonal_flavors WHERE id = ?", (flavor_id,))
        conn.commit()
    return redirect(url_for('list_flavors'))  # Redirect to list after deletion
@app.route('/update_flavor/<int:flavor_id>', methods=['GET', 'POST'])
def update_flavor(flavor_id):
    if request.method == 'POST':
        new_flavor_name = request.form.get('flavor')

        if not new_flavor_name:
            return render_template('update_flavor.html', error='Flavor name cannot be empty', flavor_id=flavor_id)

        with sqlite3.connect('database.db') as conn:
            # Check for duplicates
            cursor = conn.execute("SELECT * FROM seasonal_flavors WHERE flavor = ?", (new_flavor_name,))
            if cursor.fetchone():
                return render_template('update_flavor.html', error='Flavor already exists', flavor_id=flavor_id)

            # Update the flavor
            conn.execute("UPDATE seasonal_flavors SET flavor = ? WHERE id = ?", (new_flavor_name, flavor_id))
            conn.commit()
        return redirect(url_for('list_flavors'))  # Redirect to list after update

    # On GET, render the update form with the existing flavor name
    with sqlite3.connect('database.db') as conn:
        cursor = conn.execute("SELECT flavor FROM seasonal_flavors WHERE id = ?", (flavor_id,))
        flavor = cursor.fetchone()

        if flavor is None:
            return "Flavor not found", 404

    return render_template('update_flavor.html', flavor=flavor[0], flavor_id=flavor_id)

@app.route('/delete_ingredient/<int:ingredient_id>', methods=['POST'])
def delete_ingredient(ingredient_id):
    with sqlite3.connect('database.db') as conn:
        cursor = conn.execute("SELECT * FROM ingredient_inventory WHERE id = ?", (ingredient_id,))
        if cursor.fetchone() is None:
            return "Ingredient not found", 404

        conn.execute("DELETE FROM ingredient_inventory WHERE id = ?", (ingredient_id,))
        conn.commit()

    return redirect(url_for('list_ingredients'))  # Redirect after deletion

@app.route('/update_ingredient/<int:ingredient_id>', methods=['GET', 'POST'])
def update_ingredient(ingredient_id):
    if request.method == 'POST':
        new_ingredient_name = request.form.get('ingredient')
        new_stock = request.form.get('stock')

        if not new_ingredient_name or new_stock is None:
            return render_template('update_ingredient.html', error='Ingredient name and stock are required', ingredient_id=ingredient_id)

        try:
            new_stock = int(new_stock)
        except ValueError:
            return render_template('update_ingredient.html', error='Stock must be a number', ingredient_id=ingredient_id)

        if new_stock < 0:
            return render_template('update_ingredient.html', error='Stock cannot be negative', ingredient_id=ingredient_id)

        with sqlite3.connect('database.db') as conn:
            # Check for duplicates, but ignore the current ingredient
            cursor = conn.execute("SELECT * FROM ingredient_inventory WHERE ingredient = ? AND id != ?", (new_ingredient_name, ingredient_id))
            if cursor.fetchone():
                return render_template('update_ingredient.html', error='Ingredient already exists', ingredient_id=ingredient_id)

            # Update the ingredient
            conn.execute("UPDATE ingredient_inventory SET ingredient = ?, stock = ? WHERE id = ?", 
                         (new_ingredient_name, new_stock, ingredient_id))
            conn.commit()

        return redirect(url_for('list_ingredients'))  # Redirect after update

    # On GET, render the update form with the existing ingredient name and stock
    with sqlite3.connect('database.db') as conn:
        cursor = conn.execute("SELECT ingredient, stock FROM ingredient_inventory WHERE id = ?", (ingredient_id,))
        ingredient = cursor.fetchone()

        if ingredient is None:
            return "Ingredient not found", 404

    return render_template('update_ingredient.html', ingredient=ingredient[0], stock=ingredient[1], ingredient_id=ingredient_id)

@app.route('/delete_suggestion/<int:suggestion_id>', methods=['POST'])
def delete_suggestion(suggestion_id):
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        
        # Delete the suggestion from the database
        cursor.execute("DELETE FROM customer_suggestions WHERE id = ?", (suggestion_id,))
        conn.commit()
    
    return redirect(url_for('list_suggestions'))  # Redirect after deletion


if __name__ == '__main__':
    init_db()  
    app.run(debug=True)


