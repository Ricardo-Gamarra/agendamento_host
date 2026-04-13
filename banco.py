import sqlite3

def criar_tabela():
    conn = sqlite3.connect('agendamento_host.db')
    c = conn.cursor()
    # Usamos TEXT ou BLOB para a senha criptografada
    c.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            nome_usuario TEXT PRIMARY KEY,
            senha TEXT,
            funcao TEXT
        )
    ''')
    conn.commit()
    conn.close()

#criar_tabela()