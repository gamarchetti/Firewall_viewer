import requests
import json
import os
from config import fmc_host, verify_ssl, domain_uuid
from FP_Auth import get_valid_token

def make_api_call(url, headers, method='GET', data=None, retry=False):
    """
    Faz uma chamada à API com tratamento de erro de token.
    """
    try:
        response = requests.request(method, url, headers=headers, verify=verify_ssl, json=data)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401 and not retry:
            print("Erro de autorização. Tentando renovar o token...")
            token = get_valid_token(force_refresh=True)
            if token:
                headers['X-auth-access-token'] = token
                print("Token renovado. Tentando a chamada novamente...")
                return make_api_call(url, headers, method, data, retry=True)
            else:
                print("Falha ao renovar o token.")
                raise
        else:
            raise
    except requests.exceptions.RequestException as e:
        print(f"Erro de conexão: {e}")
        raise

def get_dynamic_objects_with_content():
    """
    Obtém todos os objetos dinâmicos do Firepower e seus conteúdos (IPs).
    """
    if not domain_uuid:
        print("UUID do domínio não encontrado no arquivo config.py. Execute FP_init.py novamente.")
        return None

    token = get_valid_token()
    if not token:
        print("Não foi possível obter um token válido.")
        return None

    headers = {"Content-Type": "application/json", "X-auth-access-token": token}
    all_dynamic_objects = []
    dynamic_object_types = [
        ("dynamicobjects", "Objetos Dinâmicos")
        # Adicione outros tipos de objetos dinâmicos conforme necessário.
    ]

    for object_type, description in dynamic_object_types:
        url_base = f"https://{fmc_host}/api/fmc_config/v1/domain/{domain_uuid}/object/{object_type}"
        print(f"Obtendo lista de {description}...")
        try:
            response_data = make_api_call(url_base, headers)
            items = response_data.get('items', [])
            print(f"  Encontrados {len(items)} {description}. Obtendo detalhes e conteúdo...")
            for item in items:
                object_id = item.get('id')
                object_name = item.get('name')
                item_with_content = item.copy()
                item_with_content['content'] = []

                if item.get('objectType') == 'IP':
                    mappings_url = f"https://{fmc_host}/api/fmc_config/v1/domain/{domain_uuid}/object/dynamicobjects/{object_id}/mappings"
                    print(f"    Obtendo mappings (IPs) para o objeto '{object_name}' (ID: {object_id})...")
                    try:
                        mappings_response_data = make_api_call(mappings_url, headers)
                        mappings_items = mappings_response_data.get('items', [])
                        ips = [mapping.get('mapping') for mapping in mappings_items if mapping.get('mapping')]
                        item_with_content['content'] = ips
                        print(f"      Encontrados {len(ips)} IPs para o objeto '{object_name}'.")
                    except requests.exceptions.HTTPError as e:
                        if e.response.status_code == 404:
                            print(f"      Erro ao obter mappings para o objeto '{object_name}' (ID: {object_id}): Endpoint não encontrado (404).")
                        elif e.response.status_code == 401:
                            print(f"      Erro ao obter mappings para o objeto '{object_name}' (ID: {object_id}): Não autorizado (401).")
                        else:
                            print(f"      Erro ao obter mappings para o objeto '{object_name}' (ID: {object_id}): {e}")
                    except requests.exceptions.RequestException as e:
                        print(f"      Erro de conexão ao obter mappings para o objeto '{object_name}' (ID: {object_id}): {e}")
                else:
                    print(f"    Objeto '{object_name}' (ID: {object_id}) não é do tipo IP. Conteúdo não obtido por este método.")

                all_dynamic_objects.append(item_with_content)

        except requests.exceptions.HTTPError as e:
            print(f"  Erro ao obter lista de {description}: {e}")
        except requests.exceptions.RequestException as e:
            print(f"  Erro ao conectar ao FMC ao obter lista de {description}: {e}")

    return all_dynamic_objects

def save_to_json_file(filename, data):
    """
    Salva os dados em um arquivo JSON no diretório do script.
    """
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        filepath = os.path.join(script_dir, filename)
        with open(filepath, "w") as f:
            json.dump(data, f, indent=4)
        print(f"Informações salvas em {filepath}")
    except Exception as e:
        print(f"Erro ao salvar em {filename}: {e}")

if __name__ == "__main__":
    print("Iniciando a extração de objetos dinâmicos e seus conteúdos do Firepower...")
    dynamic_objects_with_content = get_dynamic_objects_with_content()
    if dynamic_objects_with_content:
        save_to_json_file("FP_DO.json", dynamic_objects_with_content)
        print("Extração de objetos dinâmicos e seus conteúdos concluída.")
    else:
        print("Falha ao extrair os objetos dinâmicos e seus conteúdos.")