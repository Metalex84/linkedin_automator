from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Datos de ejemplo para la autenticación
usuarios = {'usuario': 'contraseña'}

@app.route('/')
def inicio():
    return render_template('login.html')

@app.route('/login', methods=['POST', 'GET'])
def login():
    usuario = request.form['usuario']
    contraseña = request.form['contraseña']
    
    if usuario in usuarios and usuarios[usuario] == contraseña:
        return redirect(url_for('bienvenida', usuario=usuario))
    else:
        return render_template('login.html', mensaje='Usuario o contraseña incorrectos')

@app.route('/bienvenida/<usuario>')
def bienvenida(usuario):
    return render_template('bienvenida.html', usuario=usuario)

if __name__ == '__main__':
    app.run(debug=True)