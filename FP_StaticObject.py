# FP_StaticObject.py
import requests
import json
import os
from config import fmc_host, verify_ssl, domain_uuid  # Certifique-se de que estas variáveis estão no seu config.py
from FP_Auth import get_valid_token  # Certifique-se de que este arquivo existe e tem a função get_valid_token

def get_static_objects():
    """
    Obtém todos os objetos estáticos do Firepower e seus detalhes (incluindo literals para NetworkGroups).
    """
    if not domain_uuid:
        print("UUID do domínio não encontrado no arquivo config.py. Execute FP_init.py novamente.")
        return None

    token = get_valid_token()
    if not token:
        print("Não foi possível obter um token válido.")
        return None

    headers = {"Content-Type": "application/json", "X-auth-access-token": token}
    all_static_objects = []
    static_object_types = [
        ("networks", "Objetos de Rede"),
        ("hosts", "Objetos de Host"),
        ("networkgroups", "Grupos de Rede"),
        ("networkaddresses", "Endereço de rede")
        # Adicione outros tipos de objetos conforme necessário
    ]

    for object_type, description in static_object_types:
        url_base = f"https://{fmc_host}/api/fmc_config/v1/domain/{domain_uuid}/object/{object_type}"
        print(f"Obtendo lista de {description}...")
        try:
            response = requests.get(url_base, headers=headers, verify=verify_ssl)
            response.raise_for_status()
            items = response.json().get('items', [])
            print(f"  Encontrados {len(items)} {description}.")
            for item in items:
                if 'links' in item and 'self' in item['links']:
                    details = fetch_object_details(item['links']['self'], headers)
                    if details and 'literals' in details:
                        item['literals'] = details['literals']
                all_static_objects.append(item)
        except requests.exceptions.HTTPError as e:
            print(f"  Erro ao obter lista de {description}: {e}")
        except requests.exceptions.RequestException as e:
            print(f"  Erro ao conectar ao FMC ao obter lista de {description}: {e}")

    return all_static_objects

def fetch_object_details(url, headers):
    """
    Obtém os detalhes de um objeto estático usando a URL fornecida.
    """
    try:
        response = requests.get(url, headers=headers, verify=verify_ssl)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Erro ao buscar detalhes do objeto {url}: {e}")
        return None

def save_to_json_file(filename, data):
    """
    Salva os dados em um arquivo JSON no diretório do script.
    """
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        filepath = os.path.join(script_dir, 'data', filename)
        with open(filepath, "w") as f:
            json.dump(data, f, indent=4)
        print(f"Informações salvas em {filepath}")
    except Exception as e:
        print(f"Erro ao salvar em {filename}: {e}")

if __name__ == "__main__":
    print("Iniciando a extração de objetos estáticos do Firepower...")
    static_objects = get_static_objects()
    if static_objects:
        save_to_json_file("FP_SO.json", {"items": static_objects}) # Envolver a lista em um dicionário com a chave "items"
        print("Extração de objetos estáticos concluída. Arquivo salvo em: FP_SO.json")
    else:
        print("Falha ao extrair os objetos estáticos.")