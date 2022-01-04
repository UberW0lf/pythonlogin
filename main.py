from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re


app = Flask(__name__)

# clave secreta
app.secret_key = 'root'

# detalles de la DB
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'pythonlogin'

# Iniciar mysql
mysql = MySQL(app)

# http://localhost:5000/pythonlogin/ - pagina de login
@app.route('/pythonlogin/', methods=['GET', 'POST'])
def login():
    # mensaje de error
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        # crear variables para facil acceso
        username = request.form['username']
        password = request.form['password']
        # verificar si cuenta existe usando mysql
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = %s AND password = %s', (username, password,))
        account = cursor.fetchone()
        if account:
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            # Redireccionar a home
            return redirect(url_for('home'))
        else:
            # Cuenta no existe
            msg = 'Usuario o contraseña incorrecta!'
    return render_template('index.html', msg=msg)

# http://localhost:5000/python/logout - pagina de logout
@app.route('/pythonlogin/logout')
def logout():
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   # Redireccionar a login
   return redirect(url_for('login'))

# http://localhost:5000/pythinlogin/register - pagina de registro
@app.route('/pythonlogin/register', methods=['GET', 'POST'])
def register():
    # mensaje de error
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        # verificar si cuenta ya existe
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = %s', (username,))
        account = cursor.fetchone()
        # si cuenta existe y verificaciones de validacion
        if account:
            msg = 'Esta cuenta ya existe!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'E-mail invalido!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Usuario debe contener solamente letras y numeros!'
        elif not username or not password or not email:
            msg = 'Por favor llenar informaciones!'
        else:
            # cuenta no existe y los datos son validos, se crea la cuenta
            cursor.execute('INSERT INTO accounts VALUES (NULL, %s, %s, %s)', (username, password, email,))
            mysql.connection.commit()
            msg = 'Te has registrado!'
    elif request.method == 'POST':
        # informaciones estan vacias
        msg = 'Por favor llenar informaciones!'
    return render_template('register.html', msg=msg)

# http://localhost:5000/pythinlogin/home - pagina home, solo para usuarios logados
@app.route('/pythonlogin/home')
def home():
    # verificar si usuario esta logado
    if 'loggedin' in session:
        # si esta logado entra a home
        return render_template('home.html', username=session['username'])
    # no esta logado vuelve a login
    return redirect(url_for('login'))

# http://localhost:5000/pythinlogin/profile - pagina de perfil, solo para usuarios logados
@app.route('/pythonlogin/profile')
def profile():
    # verificar si usuario esta logado
    if 'loggedin' in session:
        # extraemos todas las informaciones del usuario para mostrarlas en el perfil
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE id = %s', (session['id'],))
        account = cursor.fetchone()
        return render_template('profile.html', account=account)
    # usuario no esta logado vuelve a login
    return redirect(url_for('login'))

@app.route('/pythonlogin/home/registerrestaurant', methods=['GET', 'POST'])
def registerrestaurant():
    # mensaje de error
    msg = ''
    # verificar si usuario esta logado
    if 'loggedin' in session:
        if request.method == 'POST' and 'name' in request.form and 'country' in request.form and 'type' in request.form:
            name = request.form['name']
            country = request.form['country']
            type = request.form['type']
            # verificar si cuenta ya existe
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT * FROM restaurant WHERE name = %s', (name,))
            restaurant = cursor.fetchone()
            # si cuenta existe y verificaciones de validacion
            if restaurant:
                msg = 'Este restaurante ya existe!'
            # elif not re.match(r'[A-Za-z0-9]+', name):
            #     msg = 'El nombre del restaurante debe contener solamente letras y numeros!'
            # elif not re.match(r'[A-Za]+', country):
            #     msg = 'El nombre del país debe contener solamente letras!'
            # elif not re.match(r'[A-Za]+', type):
            #     msg = 'El tipo de restaurante debe contener solamente letras!'
            elif not name or not country or not type:
                msg = 'Por favor llenar informaciones!'
            else:
                # restaurante no existe y los datos son validos, se crea la cuenta
                cursor.execute('INSERT INTO restaurant VALUES (NULL, %s, %s, %s)', (name, country, type,))
                mysql.connection.commit()
                msg = 'Has registrado tu restaurante!'
        elif request.method == 'POST':
            # informaciones estan vacias
            msg = 'Por favor llenar informaciones!'
        return render_template('registerrestaurant.html', msg=msg)
# usuario no esta logado
    return redirect(url_for('login'))

# borrar restaurante
@app.route('/pythonlogin/home/deleterestaurant', methods=['GET', 'POST'])
def deleterestaurant():
    if 'loggedin' in session:

        msg = ''

        if request.method == 'POST' and 'rid' in request.form:
            rid = request.form['rid']
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('DELETE FROM restaurant WHERE rid = %s', (rid, ))
            mysql.connection.commit()
            msg = 'Has borrado el restaurante!'

        return render_template('deleterestaurant.html',  msg=msg)

    return redirect(url_for('login'))

# Ver restaurantes
@app.route('/pythonlogin/home/readrestaurant', methods=['GET'])
def readrestaurant():
    if 'loggedin' in session:
        msg = ''

        if request.method == 'GET':
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT * FROM restaurant')
            restaurant = cursor.fetchall()
            mysql.connection.commit()

        return render_template('readrestaurant.html',  restaurant=restaurant)

    return redirect(url_for('login'))