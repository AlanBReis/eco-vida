from flask import Flask, render_template, request, redirect, jsonify, flash, session
import sqlite3
from flask_mail import Mail, Message
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta'  # Necessário para usar flash messages

# Configurações para envio de email
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'seu_email@gmail.com'  # Insira seu e-mail
app.config['MAIL_PASSWORD'] = 'sua_senha_de_app'     # Insira sua senha de app

mail = Mail(app)

# Função para inicializar o banco de dados SQLite
def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  username TEXT UNIQUE, 
                  password TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS posts
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  user_id INTEGER, 
                  title TEXT, 
                  content TEXT, 
                  FOREIGN KEY (user_id) REFERENCES users(id))''')
    c.execute('''CREATE TABLE IF NOT EXISTS comments
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  name TEXT, 
                  comment TEXT, 
                  likes INTEGER DEFAULT 0, 
                  dislikes INTEGER DEFAULT 0)''')
    conn.commit()
    conn.close()

# Inicialize o banco de dados ao iniciar o app
init_db()

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'], method='sha256')
        
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        try:
            c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
            flash('Registro realizado com sucesso! Faça login.', 'success')
            return redirect('/login')
        except sqlite3.IntegrityError:
            flash('Nome de usuário já existe.', 'danger')
            return redirect('/register')
        finally:
            conn.close()
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("SELECT id, password FROM users WHERE username = ?", (username,))
        user = c.fetchone()
        
        if user and check_password_hash(user[1], password):
            session['user_id'] = user[0]
            flash('Login realizado com sucesso!', 'success')
            return redirect('/')
        else:
            flash('Usuário ou senha inválidos.', 'danger')
            return redirect('/login')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('Você saiu com sucesso.', 'success')
    return redirect('/')

@app.route('/post/new', methods=['GET', 'POST'])
def new_post():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        user_id = session.get('user_id')

        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("INSERT INTO posts (user_id, title, content) VALUES (?, ?, ?)", (user_id, title, content))
        conn.commit()
        conn.close()

        flash('Post criado com sucesso!', 'success')
        return redirect('/')

    return render_template('new_post.html')

@app.route('/post/delete/<int:post_id>', methods=['POST'])
def delete_post(post_id):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("DELETE FROM posts WHERE id = ?", (post_id,))
    conn.commit()
    conn.close()

    flash('Post excluído com sucesso!', 'success')
    return redirect('/')

@app.route('/', methods=['GET', 'POST'])
def home():
    # Exibindo posts salvos
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT posts.id, title, content, username FROM posts JOIN users ON posts.user_id = users.id ORDER BY posts.id DESC")
    posts = c.fetchall()
    conn.close()

    user_id = session.get('user_id')  # Obtendo o ID do usuário da sessão
    user = None  # Inicializa a variável user como None

    if user_id:
        # Se o usuário estiver logado, busque o nome de usuário
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("SELECT username FROM users WHERE id = ?", (user_id,))
        user = c.fetchone()
        conn.close()

    return render_template('index.html', posts=posts, user=user)


if __name__ == '__main__':
    app.run(debug=True)
