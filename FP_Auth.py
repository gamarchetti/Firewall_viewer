import requests
import json
import os
from config import fmc_host, verify_ssl, fmc_password, fmc_username

# Global variable to store the token
access_token = None

def get_valid_token(force_refresh=False):
    """
    Obtém um token de acesso válido do FMC.
    Se um token já existir, retorna o token existente.
    Se o token não existir ou force_refresh for True, obtém um novo token.
    """
    global access_token
    if access_token and not force_refresh:
        print("Reutilizando token existente.")
        return access_token

    # Get credentials from config.py
    fmc_user = fmc_username  # Use the correct variable name from config.py
    fmc_pass = fmc_password  # Use the correct variable name from config.py

    if not fmc_user or not fmc_pass:
        print("Credenciais não encontradas no arquivo config.py.")
        return None

    auth_url = f"https://{fmc_host}/api/fmc_platform/v1/auth/generatetoken"
    headers = {"Content-Type": "application/json"}
    auth_data = json.dumps({"username": fmc_user, "password": fmc_pass})

    try:
        print(f"Obtendo novo token de: {auth_url}")  # Debugging
        auth_response = requests.post(auth_url, auth=(fmc_username, fmc_password), headers=headers, verify=verify_ssl)
        auth_response.raise_for_status()
        access_token = auth_response.headers.get("X-auth-access-token")
        print(f"Token obtido: {access_token}")  # Debugging
        return access_token
    except requests.exceptions.RequestException as e:
        print(f"Erro ao obter token: {e}")
        return None

if __name__ == '__main__':
    token = get_valid_token()
    if token:
        print("Token obtido com sucesso:", token)
    else:
        print("Falha ao obter o token.")