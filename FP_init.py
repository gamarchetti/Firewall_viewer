import os
import json
import requests
import time
import sys

def get_domain_uuid_once(fmc_host, token, verify_ssl):
    """
    Obtém o UUID do domínio usando o endpoint correto para a versão 7.2.5.
    """
    url = f"{fmc_host}/api/fmc_platform/v1/info/domain"
    headers = {"Content-Type": "application/json", "X-auth-access-token": token}
    try:
        response = requests.get(url, headers=headers, verify=verify_ssl)
        response.raise_for_status()
        domain_info = response.json()
        if 'items' in domain_info and domain_info['items']:
            domain_uuid = domain_info['items'][0].get('uuid')
            if domain_uuid:
                print(f"UUID do domínio obtido: {domain_uuid}")
                return domain_uuid
            else:
                print("UUID do domínio não encontrado no item da resposta da API.")
                return None
        else:
            print("A lista 'items' não foi encontrada ou está vazia na resposta da API.")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Erro ao obter informações do domínio: {e}")
        return None

def get_firepower_token(fmc_host, fmc_username, fmc_password, verify_ssl):
    """
    Obtém um token de acesso do Firepower Management Center (FMC) e o retorna.
    """
    auth_url = f"{fmc_host}/api/fmc_platform/v1/auth/generatetoken"
    headers = {"Content-Type": "application/json"}
    try:
        response = requests.post(auth_url, auth=(fmc_username, fmc_password), headers=headers, verify=verify_ssl)
        response.raise_for_status()
        token = response.headers.get('X-auth-access-token')
        if token:
            return token
        else:
            print("Erro ao obter token: Nenhum token retornado.")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Erro ao obter token do Firepower: {e}")
        return None

def create_config_file(fmc_host_input, fmc_username_input, fmc_password_input, verify_ssl=False):
    """
    Cria o arquivo config.py com as informações básicas do FMC e o domainUUID.
    """
    # Remove o https:// caso o usuário tenha digitado
    fmc_host_without_prefix = fmc_host_input.replace("https://", "").replace("http://", "")

    token = get_firepower_token(f"https://{fmc_host_without_prefix}", fmc_username_input, fmc_password_input, verify_ssl)
    domain_uuid = None
    if token:
        domain_uuid = get_domain_uuid_once(f"https://{fmc_host_without_prefix}", token, verify_ssl)

    config_data = {
        "fmc_host": fmc_host_without_prefix,
        "fmc_username": fmc_username_input,
        "fmc_password": fmc_password_input,
        "verify_ssl": verify_ssl,
        "device_uuids": {},
        "domain_uuid": domain_uuid if domain_uuid else None,
        "fmc_token": token if token else '',
        "token_generation_time": int(time.time()) if token else 0
    }
    with open("config.py", "w") as f:
        f.write(f"fmc_host = '{config_data['fmc_host']}'\n")
        f.write(f"fmc_username = '{config_data['fmc_username']}'\n")
        f.write(f"fmc_password = '{config_data['fmc_password']}'\n")
        f.write(f"verify_ssl = {config_data['verify_ssl']}\n")
        f.write(f"device_uuids = {json.dumps(config_data['device_uuids'], indent=4)}\n")
        f.write(f"domain_uuid = '{config_data['domain_uuid']}'\n")
        f.write(f"fmc_token = '{config_data['fmc_token']}'\n")
        f.write(f"token_generation_time = {config_data['token_generation_time']}\n")
    print("Arquivo config.py criado com as informações do FMC, UUID do domínio e token inicial.")

# Obtém o diretório onde o script está localizado
script_directory = os.path.dirname(os.path.abspath(__file__))

# Muda o diretório de trabalho atual para o diretório do script
os.chdir(script_directory)

print(f"Diretório do script: {script_directory}")
print(f"Diretório de trabalho atual: {os.getcwd()}")

if not os.path.exists("config.py"):
    fmc_host_input = input("Por favor, digite o IP ou FQDN do seu Firepower Management Center (FMC): ")
    fmc_username_input = input("Por favor, digite seu nome de usuário do FMC: ")
    fmc_password_input = input("Por favor, digite sua senha do FMC: ")
    create_config_file(fmc_host_input, fmc_username_input, fmc_password_input)
else:
    print("Arquivo config.py já existe. Se precisar atualizar as configurações, apague este arquivo e execute novamente.")