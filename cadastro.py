import streamlit as st
import sqlite3
import pandas as pd
from banco import criar_tabela
from seguranca import criptografar
from validador import testar_login_sync
import os

# Comando para instalar o navegador no servidor caso ele não exista
os.system("playwright install chromium")

# --- FUNÇÕES DE BANCO DE DADOS ---

def salvar_usuario(nome, senha, funcao):
    try:
        conn = sqlite3.connect('agendamento_host.db')
        c = conn.cursor()
        senha_bloqueada = criptografar(senha)
        c.execute('INSERT INTO usuarios (nome_usuario, senha, funcao) VALUES (?,?,?)', 
                  (nome, senha_bloqueada, funcao))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False
    except Exception as e:
        st.error(f"Erro ao salvar: {e}")
        return False

def atualizar_senha_banco(nome, nova_senha):
    try:
        conn = sqlite3.connect('agendamento_host.db')
        c = conn.cursor()
        nova_senha_bloqueada = criptografar(nova_senha)
        c.execute('''
            UPDATE usuarios 
            SET senha = ? 
            WHERE nome_usuario = ?
        ''', (nova_senha_bloqueada, nome))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Erro ao atualizar: {e}")
        return False

def listar_usuarios():
    conn = sqlite3.connect('agendamento_host.db')
    c = conn.cursor()
    c.execute("SELECT nome_usuario FROM usuarios")
    usuarios = [linha[0] for linha in c.fetchall()]
    conn.close()
    return usuarios

# --- INTERFACE STREAMLIT ---

def main():
    st.set_page_config(page_title="Agendamento HOST", page_icon="👤", layout="centered")
    
    # --- CSS CUSTOMIZADO PARA AUMENTAR A FONTE DAS ABAS ---
    st.markdown("""
        <style>
            /* Altera o tamanho da fonte de todos os botões das abas */
            button[data-baseweb="tab"] p {
                font-size: 20px !important;
                font-weight: bold !important;
            }
            
            /* Opcional: Altera a cor da aba selecionada para destacar mais */
            button[data-baseweb="tab"][aria-selected="true"] p {
                color: #ff4b4b !important;
            }
        </style>
    """, unsafe_allow_html=True)

    # --- CSS PARA OCULTAR MENU, FOOTER E AJUSTAR ABAS ---
    st.markdown("""
        <style>
            /* Ocultar o menu superior (três linhas) e a barra de deploy */
            #MainMenu {visibility: hidden;}
            header {visibility: hidden;}
            footer {visibility: hidden;}
            
            /* Mantém o estilo das abas que já tínhamos */
            button[data-baseweb="tab"] p {
                font-size: 20px !important;
                font-weight: bold !important;
            }
        </style>
    """, unsafe_allow_html=True)
    
    
    criar_tabela()

    st.image("host2.png")
    st.title("Cadastro para agendamento de preenchimento HOST")

    

    # Criação das Abas
    aba_cadastro, aba_update, aba_admin = st.tabs(["🆕 Novo Cadastro", "🔄 Atualizar Senha", "📊 Visualizar"])

    # --- ABA 1: NOVO CADASTRO ---
    with aba_cadastro:
        st.subheader("Cadastrar novo acesso")
        with st.form("form_novo_cadastro", clear_on_submit=True):
            nome = st.text_input("Nome de Usuário (Rede)")
            senha = st.text_input("Senha da Rede", type="password")
            funcao = st.selectbox("Função/Cargo", ["Analista", "Desenvolvedor", "Gerente", "Operador"])
            botao_cadastrar = st.form_submit_button("Validar e Salvar")

        if botao_cadastrar:
            if nome and senha:
                with st.spinner("🤖 Validando credenciais no site..."):
                    valido, msg = testar_login_sync(nome, senha)
                
                if valido:
                    if salvar_usuario(nome, senha, funcao):
                        st.success(f"Usuário **{nome}** cadastrado com sucesso!")
                        #st.balloons()
                    else:
                        st.error("Este usuário já existe no banco de dados.")
                else:
                    st.error(f"Falha na validação: {msg}")
            else:
                st.warning("Preencha todos os campos.")

    
    # --- ABA 2: ATUALIZAR SENHA ---
    with aba_update:
        st.subheader("Atualizar minha senha")
        st.info("Digite seu usuário e a nova senha para validar o acesso.")

        with st.form("form_atualizar_senha", clear_on_submit=True):
            # Mudamos de selectbox para text_input por segurança
            usuario_input = st.text_input("Confirme seu Nome de Usuário (Rede)")
            nova_senha = st.text_input("Nova Senha da Rede", type="password")
            botao_atualizar = st.form_submit_button("Validar e Atualizar")

        if botao_atualizar:
            if usuario_input and nova_senha:
                # 1. Verificar primeiro se o usuário existe no banco
                usuarios_existentes = listar_usuarios()
                
                if usuario_input in usuarios_existentes:
                    with st.spinner(f"🤖 Testando nova senha para {usuario_input}..."):
                        valido, msg = testar_login_sync(usuario_input, nova_senha)
                    
                    if valido:
                        if atualizar_senha_banco(usuario_input, nova_senha):
                            st.success(f"Senha de **{usuario_input}** atualizada com sucesso!")
                    else:
                        st.error(f"A nova senha é inválida no site: {msg}")
                else:
                    # Mensagem genérica para não confirmar se o usuário existe ou não (boa prática de segurança)
                    st.error("Usuário não encontrado ou dados incorretos.")
            else:
                st.warning("Por favor, preencha todos os campos.")



    # --- ABA 3: VISUALIZAÇÃO (DEBUG) ---
    with aba_admin:
        st.subheader("Usuários no Banco Local")
        if st.button("Atualizar Lista"):
            conn = sqlite3.connect('agendamento_host.db')
            df = pd.read_sql_query("SELECT nome_usuario, funcao FROM usuarios", conn)
            st.table(df)
            conn.close()

if __name__ == "__main__":
    main()