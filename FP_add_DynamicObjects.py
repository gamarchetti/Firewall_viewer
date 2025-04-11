import requests
import json
from config import domain_uuid, fmc_username, fmc_password  # Import domain_uuid, fmc_username, fmc_password
import os

def obtain_auth_token(username, password):
    """Obtains an authentication token from the FMC."""
    url = "https://fmcrestapisandbox.cisco.com/api/fmc_platform/v1/auth/generatetoken"
    headers = {"Content-Type": "application/json"}
    response = requests.post(url, headers=headers, auth=(username, password), verify=False)
    response.raise_for_status()
    return response.headers["X-auth-access-token"]


def create_dynamic_object(name, object_type, description, auth_token):
    """
    Creates a new dynamic object on the FMC.

    Args:
        name (str): The name of the dynamic object.
        object_type (str): The type of the object (e.g., "Network", "Host").
        description (str): A description for the object.
        auth_token (str): The authentication token for the FMC API.

    Returns:
        dict: The JSON response from the API if successful, None otherwise.
    """
    headers = {
        "Content-Type": "application/json",
        "X-auth-access-token": auth_token,
    }

    payload = {
        "name": name,
        "objectType": object_type,
        "description": description,
    }

    base_url = "https://fmcrestapisandbox.cisco.com"
    api_path = f"/api/fmc_config/v1/domain/{domain_uuid}/object/dynamicobjects"
    url = f"{base_url}{api_path}"
    
    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload), verify=False)
        response.raise_for_status() 
        return response.json()
    except requests.exceptions.ConnectionError as e:
        print(f"Connection Error: {e}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Status Code: {e.response.status_code}")
            print(f"Response Text: {e.response.text}")
        return None

if __name__ == "__main__":

    file_path = 'data/FP_DO.json'

    New_Dynamic_Object = input("Digite o nome do objeto dinâmico: ")

    dynamic_object_type = "IP"
    dynamic_object_name = New_Dynamic_Object
    dynamic_object_description = "Test with IP Type"

    # Check if data file exists
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r') as f:
                dynamic_objects = json.load(f)  # Load the list of dynamic objects

            # Check if object name exists
            name_exists = any(obj['name'] == dynamic_object_name for obj in dynamic_objects)
            if name_exists:
                print(f"Object name '{dynamic_object_name}' already exists.")
                exit()
        except (FileNotFoundError, json.JSONDecodeError):
            print("Error reading or decoding JSON file.")
            exit()

    try:
        auth_token = obtain_auth_token(fmc_username, fmc_password)       
    except requests.exceptions.RequestException as e:
        print(f"Authentication Error: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Status Code: {e.response.status_code}")
            print(f"Response Text: {e.response.text}")
        exit()

    # Call the function with sample values
    response_data = create_dynamic_object(
        name=dynamic_object_name,
        object_type=dynamic_object_type,
        description=dynamic_object_description,
        auth_token=auth_token
    )
    
    if response_data:
        print("Dynamic object created successfully:")
        print(json.dumps(response_data, indent=4)) 