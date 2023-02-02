from dotenv import load_dotenv
import os
import pymysql
from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
#secret key
app.secret_key = 'novaglez'

@app.route('/')
def main():
    return "SCE WEB..."

@app.route('/articulos')
def articulos():
    user_id = session.get('user_id')

    if user_id == None:
        # user not authenticated, return to login page
        return redirect(url_for('login'))

    load_dotenv()
    #ssl certiticate
    ssl_cert = os.getcwd() + "/cacert.pem"

    #conexion
    db = pymysql.connect(
    host=os.getenv("HOST"),
    database=os.getenv("DATABASE"),
    user=os.getenv("USER"),
    password=os.getenv("PASSWORD"),
    ssl_ca=ssl_cert)

    #cursor
    cursor = db.cursor()

    cursor.execute("SELECT IdArticulo, Nombre, PrecioImpDetalle1 FROM Articulo")
    data = cursor.fetchall()
    db.close()

    return render_template('products.html', products=data)

@app.route("/search", methods=["GET"])
def search():
    nombre = request.args.get("nombre")
    load_dotenv()
    #ssl certiticate
    ssl_cert = os.getcwd() + "/cacert.pem"
    
    if(nombre != ""):
        #conexion
        db = pymysql.connect(
        host=os.getenv("HOST"),
        database=os.getenv("DATABASE"),
        user=os.getenv("USER"),
        password=os.getenv("PASSWORD"),
        ssl_ca=ssl_cert)

        cursor = db.cursor()
        sql = "SELECT IdArticulo, Nombre, PrecioImpDetalle1 FROM Articulo WHERE nombre LIKE %s"
        cursor.execute(sql, ("%" + nombre + "%",))
        results = cursor.fetchall()

        return render_template("search_results.html", results=results)
    else:
        return render_template("search_results.html")

@app.route("/search_articulo")
def search_page():
    user_id = session.get('user_id')

    if user_id:
         return render_template("search_articulo.html")
    else:
        # user not authenticated, return to login page
        return redirect(url_for('login'))
   

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        return redirect(url_for('authenticate'))
    return render_template('login.html')

@app.route('/authenticate', methods=['GET', 'POST'])
def authenticate():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        load_dotenv()
        #ssl certiticate
        ssl_cert = os.getcwd() + "/cacert.pem"

        #conexion
        db = pymysql.connect(
        host=os.getenv("HOST"),
        database=os.getenv("DATABASE"),
        user=os.getenv("USER"),
        password=os.getenv("PASSWORD"),
        ssl_ca=ssl_cert)

        cursor = db.cursor()
        cursor.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, password))
        result = cursor.fetchone()

        if result:
            # user authenticated, store the user's information in the session
            session['username'] = username
            session['user_id'] = result[0]
            return redirect(url_for('dashboard'))
        else:
            # user not authenticated, return to login page
            return redirect(url_for('login'))
    return redirect(url_for('login'))

@app.route("/dashboard")
def dashboard():
    user_id = session.get('user_id')

    if user_id:
         return render_template("dashboard.html")
    else:
        # user not authenticated, return to login page
        return redirect(url_for('login'))

@app.route("/register_user")
def register_user():
    user_id = session.get('user_id')

    if user_id:
        return render_template("create_user.html")
    else:
        # user not authenticated, return to login page
        return redirect(url_for('login'))
        


@app.route('/create_user', methods=['POST'])
def create_user():
    username = request.form['username']
    email = request.form['email']
    password = request.form['password']

    load_dotenv()
    #ssl certiticate
    ssl_cert = os.getcwd() + "/cacert.pem"

    #conexion
    db = pymysql.connect(
    host=os.getenv("HOST"),
    database=os.getenv("DATABASE"),
    user=os.getenv("USER"),
    password=os.getenv("PASSWORD"),
    ssl_ca=ssl_cert)
    
    with db.cursor() as cursor:
        query = "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)"
        cursor.execute(query, (username, email, password))
        db.commit()
    
    return "User created successfully."

@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('user_id', None)
    return redirect(url_for('login'))
    

if __name__ == '__main__':
    app.run(debug=True, port=os.getenv("PORT", default=5000))