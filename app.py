from flask import Flask, render_template, request, redirect, jsonify, flash
import sqlite3
from flask_mail import Mail, Message

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

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        name = request.form['name']
        comment = request.form['comment']
        
        # Salvando o comentário no banco de dados
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("INSERT INTO comments (name, comment) VALUES (?, ?)", (name, comment))
        conn.commit()
        conn.close()
        
        # Enviar notificação por e-mail
        msg = Message("Novo Comentário no Site",
                      sender="seu_email@gmail.com",
                      recipients=["destinatario@gmail.com"])  # E-mail para onde será enviada a notificação
        msg.body = f"Nome: {name}\nComentário: {comment}"
        mail.send(msg)

        flash('Comentário enviado com sucesso!', 'success')
        return redirect('/')
    
    # Exibindo os comentários salvos
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    # c.execute("SELECT id, name, comment, likes, dislikes FROM comments ORDER BY id DESC")
    # comments = c.fetchall()
    conn.close()
    
    # Transformar a lista de comentários em uma lista de dicionários
    # comments = [
    #     {"id": comment[0], "name": comment[1], "text": comment[2], "likes": comment[3], "dislikes": comment[4]}
    #     for comment in comments
    # ]

    # Retornando uma lista de comentários vazia para teste
    comments = []

    return render_template('index.html', comments=comments)

@app.route('/vote', methods=['POST'])
def vote():
    comment_id = request.json.get('id')
    vote_type = request.json.get('type')  # 'like' ou 'dislike'
    
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    if vote_type == 'like':
        c.execute("UPDATE comments SET likes = likes + 1 WHERE id = ?", (comment_id,))
    elif vote_type == 'dislike':
        c.execute("UPDATE comments SET dislikes = dislikes + 1 WHERE id = ?", (comment_id,))
    conn.commit()
    c.execute("SELECT likes, dislikes FROM comments WHERE id = ?", (comment_id,))
    likes, dislikes = c.fetchone()
    conn.close()
    
    return jsonify({'likes': likes, 'dislikes': dislikes})

if __name__ == '__main__':
    app.run(debug=True)
