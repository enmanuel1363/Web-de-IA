from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
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

from functools import wraps

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'id_rol' not in session or session['id_rol'] != 1:
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def home():
    return render_template('index.html')#  redirige a la pagina index.html que es la pagina principal

@app.route('/admin')
@admin_required  
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
            session['id'] = user['id']
            session['id_rol'] = user['id_rol']
            session['nombre'] = user['nombre']
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
            return jsonify({'success': False, 'message': 'Las contraseñas no coinciden'})

        cursor = mysql.connection.cursor()

        # Verifica que no exista un usuario con ese email
        cursor.execute('SELECT * FROM usuario WHERE email = %s', (email,))
        existing_user = cursor.fetchone()

        if existing_user:
            cursor.close()
            return jsonify({'success': False, 'message': 'El correo ya está registrado'})

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
@admin_required
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

@app.route('/eliminar_usuario/<int:id>')
@admin_required
def eliminar_usuario(id):
    cursor = mysql.connection.cursor()
    cursor.execute('DELETE FROM usuario WHERE id = %s', (id,))
    mysql.connection.commit()
    cursor.close()
    return redirect(url_for('listar_usuarios'))

@app.route('/editar_usuario/<int:id>', methods=['POST'])
@admin_required
def editar_usuario(id):
    cursor = mysql.connection.cursor()
    if request.method == 'POST':
        nombre = request.form['nombre']
        email = request.form['email']
        cursor.execute('UPDATE usuario SET nombre = %s, email = %s WHERE id = %s', (nombre, email, id))
        mysql.connection.commit()
        cursor.close()
        return jsonify({'success': True, 'message': 'Usuario actualizado correctamente'})


@app.route('/productos')
@admin_required
def listar_productos_agregados():
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT id, nombre_producto, precio, descripcion FROM productos')
    productos = cursor.fetchall()
    cursor.close()
    return render_template('Productos.html', productos=productos)

@app.route('/agregar_producto')
@admin_required
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

@app.route('/eliminar_producto/<int:id>')
def eliminar_producto(id):
    cursor = mysql.connection.cursor()
    cursor.execute('DELETE FROM productos WHERE id = %s', (id,))
    mysql.connection.commit()
    cursor.close()
    return redirect(url_for('listar_productos_agregados'))

@app.route('/editar_producto/<int:id>', methods=['GET', 'POST'])
def editar_producto(id):
    cursor = mysql.connection.cursor()
    if request.method == 'POST':
        nombre_producto = request.form['nombre_producto']
        precio = request.form['precio']
        descripcion = request.form['descripcion']
        cursor.execute('UPDATE productos SET nombre_producto = %s, precio = %s, descripcion = %s WHERE id = %s', (nombre_producto, precio, descripcion, id))
        mysql.connection.commit()
        cursor.close()
        return redirect(url_for('listar'))
    else:
        cursor.execute('SELECT id, nombre_producto, precio, descripcion FROM productos WHERE id = %s', (id,))
        producto = cursor.fetchone()
        cursor.close()
        return render_template('editar_producto.html', producto=producto)
    
    
    return redirect(url_for('login'))

@app.route('/cambiar_password', methods=['POST'])
def cambiar_password():
    if 'id' in session:
        if request.method == 'POST':
            current_password = request.form['current_password']
            new_password = request.form['new_password']
            confirm_password = request.form['confirm_password']

            cursor = mysql.connection.cursor()
            cursor.execute('SELECT password FROM usuario WHERE id = %s', (session['id'],))
            user = cursor.fetchone()

            if user and user['password'] == current_password:
                if new_password == confirm_password:
                    cursor.execute('UPDATE usuario SET password = %s WHERE id = %s', (new_password, session['id']))
                    mysql.connection.commit()
                    cursor.close()
                    return jsonify({'success': True, 'message': 'Contraseña actualizada correctamente'})
                else:
                    return jsonify({'success': False, 'message': 'Las nuevas contraseñas no coinciden'})
            else:
                return jsonify({'success': False, 'message': 'La contraseña actual es incorrecta'})

    return redirect(url_for('login'))

@app.route('/editar_perfil', methods=['POST'])
def editar_perfil():
    if 'id' in session:
        if request.method == 'POST':
            nombre = request.form['nombre']
            email = request.form['email']

            cursor = mysql.connection.cursor()
            cursor.execute('UPDATE usuario SET nombre = %s, email = %s WHERE id = %s', (nombre, email, session['id']))
            mysql.connection.commit()
            cursor.close()

            # Actualizar el nombre en la sesión
            session['nombre'] = nombre

            return jsonify({'success': True, 'message': 'Perfil actualizado correctamente', 'usuario': {'nombre': nombre, 'email': email}})
    
    return redirect(url_for('login'))
    
@app.route('/perfil')
def perfil():
    if 'id' not in session:
        return redirect(url_for('login'))

    cursor = mysql.connection.cursor()
    
    # Obtener información del usuario
    cursor.execute('SELECT * FROM usuario WHERE id = %s', (session['id'],))
    usuario = cursor.fetchone()

    if not usuario:
        cursor.close()
        return redirect(url_for('login'))

    # Asignar nombre del rol
    if usuario['id_rol'] == 1:
        usuario['rol_nombre'] = 'Administrador'
    elif usuario['id_rol'] == 2:
        usuario['rol_nombre'] = 'Cliente'
    else:
        usuario['rol_nombre'] = 'Desconocido'

    # Obtener todos los productos/cursos
    cursor.execute('SELECT * FROM productos')
    cursos = cursor.fetchall()

    cursor.close()
    return render_template('perfil.html', usuario=usuario, cursos=cursos)

@app.route('/eliminar_curso_perfil/<int:id>')
def eliminar_curso_perfil(id):
    cursor = mysql.connection.cursor()
    cursor.execute('DELETE FROM productos WHERE id = %s', (id,))
    mysql.connection.commit()
    cursor.close()
    return redirect(url_for('perfil'))

@app.route('/editar_curso_perfil/<int:id>', methods=['GET', 'POST'])
def editar_curso_perfil(id):
    cursor = mysql.connection.cursor()
    if request.method == 'POST':
        nombre_producto = request.form['nombre_producto']
        precio = request.form['precio']
        descripcion = request.form['descripcion']
        cursor.execute('UPDATE productos SET nombre_producto = %s, precio = %s, descripcion = %s WHERE id = %s', (nombre_producto, precio, descripcion, id))
        mysql.connection.commit()
        cursor.close()
        return jsonify({'success': True, 'message': 'Curso actualizado correctamente'})
    else:
        cursor.execute('SELECT id, nombre_producto, precio, descripcion FROM productos WHERE id = %s', (id,))
        curso = cursor.fetchone()
        cursor.close()
        return render_template('editar_curso_perfil.html', curso=curso)
   
if __name__=='__main__':
    app.run(debug=True, port=8000)#  ejecuta la aplicacion en el puerto 8000 y en modo debug