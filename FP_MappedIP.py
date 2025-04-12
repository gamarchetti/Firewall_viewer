import requests
import json
import argparse
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

def update_mapped_ips(object_id, ip_addresses, auth_token, action):
    """Updates the mapped IPs of an existing dynamic object."""
    url = f"{BASE_URL}/api/fmc_config/v1/domain/{domain_uuid}/object/dynamicobjects/{object_id}/mappings?action={action}"
    headers = {
        "X-auth-access-token": auth_token,
        "Content-Type": "application/json",
    }
    
    # If action is remove, and no ip_addresses are provided, remove all mappings.
    if action == "remove" and not ip_addresses:
        ip_addresses = get_existing_mappings(object_id, auth_token)
    
    if ip_addresses:
        payload = {"mappings": ip_addresses}
    else:
        payload = {"mappings": []}  # Send empty list to remove all mappings
    
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

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Update mapped IPs for a dynamic object.")
    parser.add_argument("object_id", help="ID of the dynamic object")
    parser.add_argument("action", choices=["add", "remove"], help="Action to perform: add or remove")
    parser.add_argument("ip_addresses", nargs="?", default="", help="Comma-separated list of IP addresses")

    args = parser.parse_args()
    object_id = args.object_id
    action = args.action
    ip_addresses = [ip.strip() for ip in args.ip_addresses.split(",") if ip.strip()]

    auth_token = obtain_auth_token(fmc_username, fmc_password)
    print(ip_addresses)
    if not auth_token:
        print("Failed to obtain authentication token.")
        exit()

    print("Token:", auth_token)

    if action == "remove" and not ip_addresses:
        # Remove all mappings if action is "remove" and no IPs are specified.
        response = update_mapped_ips(object_id, [], auth_token, "remove")
    else:
        response = update_mapped_ips(object_id, ip_addresses, auth_token, action)

    if response:
        print(f"Successfully updated mapped IPs. Action: {action}")
        print("Response:", json.dumps(response, indent=2))
    else:
        print(f"Failed to update mapped IPs. Action: {action}")
