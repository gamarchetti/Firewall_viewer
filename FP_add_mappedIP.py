import requests
import json
from config import domain_uuid, fmc_username, fmc_password


BASE_URL = "https://fmcrestapisandbox.cisco.com"

def obtain_auth_token(username, password):
    """Obtains an authentication token from the FMC."""
    url = "https://fmcrestapisandbox.cisco.com/api/fmc_platform/v1/auth/generatetoken"
    headers = {"Content-Type": "application/json"}
    try:
        response = requests.post(url, headers=headers, auth=(username, password), verify=False)
        response.raise_for_status()
        return response.headers["X-auth-access-token"]
    except requests.exceptions.RequestException as e:
        print(f"Authentication Error: {e}")
        return None

def get_existing_mappings(object_id, auth_token):
    """Gets the existing IP mappings for a dynamic object."""
    url = f"{BASE_URL}/api/fmc_config/v1/domain/{domain_uuid}/object/dynamicobjects/{object_id}/mappings"
    headers = {"X-auth-access-token": auth_token}
    try:
        response = requests.get(url, headers=headers, verify=False)
        response.raise_for_status()
        return response.json().get("mappings", [])
    except requests.exceptions.RequestException as e:
        print(f"Error getting existing mappings: {e}")
        return []

def update_mapped_ips(object_id, ip_addresses, auth_token):
    """Updates the mapped IPs of an existing dynamic object."""
    url = f"{BASE_URL}/api/fmc_config/v1/domain/{domain_uuid}/object/dynamicobjects/{object_id}/mappings"
    headers = {
        "X-auth-access-token": auth_token,
        "Content-Type": "application/json",
    }
    
    existing_ips = get_existing_mappings(object_id, auth_token)
    updated_mappings = list(set(existing_ips + ip_addresses))

    payload = {
        "mappings": updated_mappings,
        "type": "DynamicObjectMappings",
        "id": object_id,
    }

    try:        
        response = requests.put(url, headers=headers, data=json.dumps(payload), verify=False)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        return response.json()
    except requests.exceptions.ConnectionError as e:
        print(f"Connection Error: {e}")
        return None
    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error: {e} - {response.status_code}")
        try:
            error_json = response.json()
            if "error" in error_json and "messages" in error_json["error"]:
                for message in error_json["error"]["messages"]:
                    print(f"  Error Description: {message.get('description', 'No description available')}")
        except json.JSONDecodeError:
            print(f"  Error Response (non-JSON): {response.text}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None

if __name__ == "__main__":
    object_id = "005056BF-7B88-0ed3-0000-017181086476"
    ip_addresses = ["192.168.1.100/32", "10.0.0.1/24", "172.16.0.1"]
    
    auth_token = obtain_auth_token(fmc_username, fmc_password)
    if not auth_token:
        print("Failed to obtain authentication token.")
        exit()
        
    print("Token obtido:", auth_token)
    response = update_mapped_ips(object_id, ip_addresses, auth_token)

    if response:
        print("Successfully added mapped IP.")
        print("Response:", json.dumps(response, indent=2))
    else:
        print("Failed to add mapped IP.")