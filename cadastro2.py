import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from seguranca import criptografar
from validador import testar_login_sync

# --- CONEXÃO COM GOOGLE SHEETS ---
conn = st.connection("gsheets", type=GSheetsConnection)

def salvar_usuario(nome, senha, funcao):
    try:
        # 1. Lê os dados atuais da planilha
        df_existente = conn.read(ttl=0) # ttl=0 garante que lê o dado mais fresco
        
        # 2. Verifica se o usuário já existe
        if nome in df_existente['nome_usuario'].values:
            return False, "Usuário já cadastrado."
            
        # 3. Prepara o novo registro
        senha_bloqueada = criptografar(senha)
        novo_usuario = pd.DataFrame([{
            "nome_usuario": nome,
            "senha": senha_bloqueada,
            "funcao": funcao
        }])
        
        # 4. Concatena e atualiza a planilha
        df_atualizado = pd.concat([df_existente, novo_usuario], ignore_index=True)
        conn.update(data=df_atualizado)
        return True, "Sucesso"
    except Exception as e:
        return False, str(e)

def atualizar_senha_sheets(nome, nova_senha):
    try:
        df = conn.read(ttl=0)
        if nome in df['nome_usuario'].values:
            nova_senha_bloqueada = criptografar(nova_senha)
            # Atualiza a senha na linha correspondente
            df.loc[df['nome_usuario'] == nome, 'senha'] = nova_senha_bloqueada
            conn.update(data=df)
            return True
        return False
    except:
        return False

# Para listar os usuários no Update e Visualizar
def listar_usuarios():
    df = conn.read(ttl=0)
    return df['nome_usuario'].tolist()