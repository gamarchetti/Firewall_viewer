import requests
import json
import time
import os
from config import fmc_host, verify_ssl, domain_uuid
from FP_Auth import get_valid_token

def get_access_control_policies(retry=False):
    """
    Obtém todas as Access Control Policies do Firepower usando o domainUUID do config.py.
    Tenta renovar o token em caso de erro 401.
    """
    if not domain_uuid:
        print("UUID do domínio não encontrado no arquivo config.py. Execute FP_init.py novamente.")
        return None

    token = get_valid_token(force_refresh=not retry)  # Força o refresh na primeira tentativa após um 401
    if token:
        url = f"https://{fmc_host}/api/fmc_config/v1/domain/{domain_uuid}/policy/accesspolicies"
        headers = {"Content-Type": "application/json", "X-auth-access-token": token}
        try:
            response = requests.get(url, headers=headers, verify=verify_ssl)
            response.raise_for_status()
            return response.json().get('items', [])
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401 and not retry:
                print("Erro 401 ao obter Access Control Policies. Tentando obter um novo token.")
                return get_access_control_policies(retry=True)
            else:
                print(f"Erro ao obter Access Control Policies: {e}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"Erro ao obter Access Control Policies: {e}")
            return None
    else:
        print("Não foi possível obter um token válido para buscar as Access Control Policies.")
        return None

def get_acp_rules(policy_id, retry=False):
    """
    Obtém os detalhes completos de todas as regras de uma Access Control Policy específica.
    Tenta renovar o token em caso de erro 401.
    """
    token = get_valid_token(force_refresh=not retry) # Força o refresh na primeira tentativa após um 401
    if token:
        url = f"https://{fmc_host}/api/fmc_config/v1/domain/{domain_uuid}/policy/accesspolicies/{policy_id}/accessrules"
        headers = {"Content-Type": "application/json", "X-auth-access-token": token}
        all_rules_details = []
        try:
            response = requests.get(url, headers=headers, verify=verify_ssl)
            response.raise_for_status()
            rules = response.json().get('items', [])
            if rules:
                print(f"Encontradas {len(rules)} regras para a política {policy_id}. Obtendo detalhes...")
                for rule in rules:
                    rule_link = rule.get('links', {}).get('self')
                    if rule_link:
                        detailed_url = f"https://{fmc_host}{rule_link[rule_link.find('/api'):]}"
                        try:
                            detailed_response = requests.get(detailed_url, headers=headers, verify=verify_ssl)
                            detailed_response.raise_for_status()
                            all_rules_details.append(detailed_response.json())
                        except requests.exceptions.HTTPError as e:
                            if e.response.status_code == 401 and not retry:
                                print(f"Erro 401 ao obter detalhes da regra {rule.get('id')}. Tentando obter um novo token.")
                                return get_acp_rules(policy_id, retry=True)
                            else:
                                print(f"Erro ao obter detalhes da regra {rule.get('id')}: {e}")
                        except requests.exceptions.RequestException as e:
                            print(f"Erro ao obter detalhes da regra {rule.get('id')}: {e}")
            return all_rules_details
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401 and not retry:
                print(f"Erro 401 ao obter lista de regras da ACP {policy_id}. Tentando obter um novo token.")
                return get_acp_rules(policy_id, retry=True)
            else:
                print(f"Erro ao obter lista de regras da ACP {policy_id}: {e}")
            return None
        except requests.exceptions.RequestException as e:
            print(f"Erro ao obter lista de regras da ACP {policy_id}: {e}")
            return None
    else:
        print("Não foi possível obter um token válido para buscar as regras da ACP.")
        return None

def save_to_json_file(filename, data):
    """
    Salva os dados em um arquivo JSON.
    """
    try:
        with open(filename, "w") as f:
            json.dump(data, f, indent=4)
        print(f"Informações salvas em {filename}")
    except Exception as e:
        print(f"Erro ao salvar em {filename}: {e}")

if __name__ == "__main__":
    policies = get_access_control_policies()
    if policies:
        # Cria um diretório para as regras das políticas, se não existir
        data_folder = "data" # Assuming 'data' folder is in the same directory
        rules_directory = os.path.join(data_folder, "acp_rules")
        if not os.path.exists(rules_directory):
            os.makedirs(rules_directory)

        # Extrai e salva as regras de cada política
        for policy in policies:
            policy_id = policy.get('id')
            policy_name = policy.get('name')
            if policy_id and policy_name:
                print(f"\nObtendo regras para a política: {policy_name} (ID: {policy_id})")
                rules_details = get_acp_rules(policy_id)
                if rules_details is not None:
                    # Remove caracteres especiais e espaços do nome para criar um nome de arquivo seguro
                    safe_filename = "".join(c if c.isalnum() else "_" for c in policy_name)
                    filename = os.path.join(rules_directory, f"{safe_filename}.json")
                    save_to_json_file(filename, rules_details)