import os
from cryptography.fernet import Fernet


def obter_chave():
    if not os.path.exists("secret.key"):
        chave = Fernet.generate_key()
        with open("secret.key", "wb") as key_file:
            key_file.write(chave)
    return open("secret.key", "rb").read()

CHAVE = obter_chave()
cipher = Fernet(CHAVE)

def criptografar(texto):
    return cipher.encrypt(texto.encode()).decode()

def descriptografar(texto_cripto):
    return cipher.decrypt(texto_cripto.encode()).decode()