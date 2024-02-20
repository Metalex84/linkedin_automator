from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

def validar_usuario(usuario, contraseña):
    if usuario == 'admin' and contraseña == 'admin':
        return True
    else:
        return False

@app.route('/')
def inicio():
    return render_template('login.html')

@app.route('/login', methods=['POST', 'GET'])
def login():
    usuario = request.form['usuario']
    contraseña = request.form['contraseña']
    if validar_usuario(usuario, contraseña):
        return redirect(url_for('bienvenida', usuario=usuario, contraseña=contraseña))
    else:
        return render_template('login.html', mensaje='Usuario o contraseña incorrectos')
@app.route('/bienvenida/<usuario>')
def bienvenida(usuario):
    return render_template('bienvenida.html', usuario=usuario)

if __name__ == '__main__':
    app.run(debug=True)