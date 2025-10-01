from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mysqldb import MySQL
app=Flask(__name__)

app.secret_key = 'appsecretkey' #clave secreta para la sesion

mysql=MySQL() #inicializa la conexion a la DB

# conexion a la DB
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_PORT'] = 3306
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'ventas'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'


mysql.init_app(app) #inicializa la conexion a la DB

@app.route('/')
def home():
    return render_template('index.html')#  redirige a la pagina index.html que es la pagina principal

@app.route('/admin')  
def admin():
    return render_template('admin.html')

@app.route('/accesologin', methods=['GET', 'POST'])
def accesologin():
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        email = request.form['email']
        password = request.form['password']

        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM usuario WHERE email = %s AND password = %s', (email, password))
        user = cursor.fetchone()
        cursor.close()

        if user:
            session['id_rol'] = user['id_rol']
            if user['id_rol'] == 1:
                return render_template('admin.html')
            elif user['id_rol'] == 2:
                return render_template('index.html')
        else:
            flash('Usuario o contraseña incorrecta')
            return render_template('login.html')


    
    return render_template('login.html')

@app.route('/inicio')
def inicio():
    return render_template('index.html')#  redirige a la pagina index.html al momento de darle al boton inicio

@app.route('/contacto')
def contacto():
    return render_template('contacto.html')#  redirige a la pagina contacto.html

@app.route('/contactopost', methods=['GET', 'POST'])
def contactopost():
    usuario={ #Diccionaroio para almacenar los datos del formulario
         'nombre': '',
         'email': '',
         'mensaje': ''
    }
    if request.method == 'POST':
       
       usuario['nombre'] = request.form.get('nombre')
       usuario['email'] = request.form.get('email')
       usuario['mensaje'] = request.form.get('mensaje')
    return render_template('Contactopost.html', user=usuario)   

@app.route('/about')
def about():
    return render_template('about.html')#  redirige a la pagina about.html

@app.route('/login')
def login():
    return render_template('login.html')#  redirige a la pagina login.html donde te puedes logear

@app.route('/logout')
def logout():
    session.clear()  # Limpia la sesión
    return redirect(url_for('inicio'))

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    # Obtiene el valor del parámetro 'next' de la URL, si existe
    next_page = request.args.get('next')
    if request.method == 'POST':
        # Obtiene los datos del formulario de registro
        nombre = request.form.get('nombre')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        # Valida que las contraseñas coincidan
        if password != confirm_password:
            return render_template('Registro.html', error='Las contraseñas no coinciden', next=next_page)

        cursor = mysql.connection.cursor()

        # Verifica que no exista un usuario con ese email
        cursor.execute('SELECT * FROM usuario WHERE email = %s', (email,))
        existing_user = cursor.fetchone()

        if existing_user:
            cursor.close()
            return render_template('Registro.html', error='El correo ya está registrado', next=next_page)

        # Inserta el nuevo usuario en la base de datos con un rol por defecto
        cursor.execute('INSERT INTO usuario (nombre, email, password, id_rol) VALUES (%s, %s, %s, %s)',
                       (nombre, email, password, 2))
        mysql.connection.commit()
        cursor.close()

        # Redirige a la página de listar_usuarios si el parámetro 'next' es 'listar_usuarios'
        if next_page == 'listar_usuarios':
            return redirect(url_for('listar_usuarios'))
        else:
            # Si no, redirige a la página de login
            return redirect(url_for('login'))
    
    # Renderiza la plantilla de registro, pasando el parámetro 'next'
    return render_template('Registro.html', next=next_page)

@app.route('/listar_usuarios')
def listar_usuarios():
    # Crea un cursor para ejecutar consultas a la base de datos
    cursor = mysql.connection.cursor()
    # Ejecuta una consulta para obtener todos los usuarios
    cursor.execute('SELECT id, nombre, email, password FROM usuario')
    # Obtiene todos los resultados de la consulta
    usuarios = cursor.fetchall()
    # Cierra el cursor
    cursor.close()
    # Renderiza la plantilla de listar_usuarios, pasando la lista de usuarios
    return render_template('Listar_Usuarios.html', usuarios=usuarios)


@app.route('/productos')
def listar_productos_agregados():
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT id, nombre_producto, precio, descripcion FROM productos')
    productos = cursor.fetchall()
    cursor.close()
    return render_template('Productos.html', productos=productos)

@app.route('/agregar_producto')
def agregar_producto():
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT id, nombre_producto, precio, descripcion FROM productos')
    productos = cursor.fetchall()
    cursor.close()
    return render_template('agregar_producto.html', productos=productos)

@app.route('/guardar_producto', methods=['POST'])
def guardar_producto():
    if request.method == 'POST':
        nombre_producto = request.form['nombre_producto']
        precio = request.form['precio']
        descripcion = request.form['descripcion']
        cursor = mysql.connection.cursor()
        cursor.execute('INSERT INTO productos (nombre_producto, precio, descripcion) VALUES (%s, %s, %s)', (nombre_producto, precio, descripcion))
        mysql.connection.commit()
        cursor.close()
        return redirect(url_for('agregar_producto'))
   
if __name__=='__main__':
    app.run(debug=True, port=8000)#  ejecuta la aplicacion en el puerto 8000 y en modo debug