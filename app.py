from flask import Flask, render_template, redirect, url_for, flash, jsonify, request
import json
import os
import subprocess
import sys  # Import the sys module

app = Flask(__name__)
app.secret_key = "uma_chave_secreta"  # Necessário para o flash()
DATA_FOLDER = os.path.join(app.root_path, 'data')
ACP_RULES_FOLDER = os.path.join(DATA_FOLDER, 'acp_rules')

def get_policy_filenames():
    """
    Retorna uma lista de nomes de arquivos de política no diretório ACP_RULES_FOLDER.
    """
    try:
        return [filename for filename in os.listdir(ACP_RULES_FOLDER) if filename.endswith('.json')]
    except FileNotFoundError:
        print(f"Diretório não encontrado: {ACP_RULES_FOLDER}")
        return []

def load_policy_rules(filename):
    """
    Carrega as regras de política de um arquivo JSON.
    """
    file_path = os.path.join(ACP_RULES_FOLDER, filename)
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Arquivo não encontrado: {file_path}")
        return []
    except json.JSONDecodeError:
        print(f"Erro ao decodificar JSON de: {file_path}")
        return []

def load_json_data(filepath):
    """
    Carrega dados de um arquivo JSON.
    """
    try:
        with open(filepath, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Arquivo não encontrado: {filepath}")
        return None
    except json.JSONDecodeError:
        print(f"Erro ao decodificar JSON de: {filepath}")
        return None

def get_dynamic_objects():
    fp_do_path = os.path.join(DATA_FOLDER, 'FP_DO.json')
    try:
        with open(fp_do_path, 'r') as f:
            data = json.load(f)
            objects = []
            for item in data:  # Itera diretamente sobre a lista 'data'
                object_info = {'name': item['name'], 'ips': []}
                if 'content' in item and isinstance(item['content'], list):
                    object_info['ips'].extend(item['content'])
                objects.append(object_info)
            return objects
    except FileNotFoundError:
        return None

@app.route('/')
def homepage():
    return render_template('homepage.html')

@app.route('/policies')
def policies():
    policy_files = get_policy_filenames()
    return render_template('policies.html', policy_files=policy_files)

@app.route('/policy/<filename>')
def show_policy(filename):
    rules = load_policy_rules(filename)
    fp_do_path = os.path.join(DATA_FOLDER, 'FP_DO.json')
    fp_so_path = os.path.join(DATA_FOLDER, 'FP_SO.json')
    dynamic_objects_data = load_json_data(fp_do_path)
    static_objects_data = load_json_data(fp_so_path)

    dynamic_objects = {}
    if dynamic_objects_data and 'items' in dynamic_objects_data:
        for item in dynamic_objects_data['items']:
            dynamic_objects[item['name']] = item.get('content')

    static_objects_by_id = {}
    if static_objects_data and 'items' in static_objects_data:
        for item in static_objects_data['items']:
            ips = []
            if 'literals' in item:
                for literal in item['literals']:
                    if literal.get('value'):
                        ips.append(literal['value'])
            elif 'value' in item:
                ips.append(item['value'])
            static_objects_by_id[item['id']] = ips

    print("Conteúdo de static_objects_by_id:", static_objects_by_id)
    for rule in rules:
        print(f"Processando regra: {rule.get('name')}")
        rule['source_ips'] = []
        if rule.get('sourceNetworks') and rule['sourceNetworks'].get('objects'):
            print("  Source Networks:", rule.get('sourceNetworks'))
            for source_object in rule['sourceNetworks']['objects']:
                object_id = source_object.get('id')
                print(f"    ID do objeto de origem encontrado: {object_id}")
                if object_id and object_id in static_objects_by_id:
                    print(f"    IPs correspondentes (origem):", static_objects_by_id[object_id])
                    rule['source_ips'].extend(static_objects_by_id[object_id])

        rule['destination_ips'] = []
        if rule.get('destinationNetworks') and rule['destinationNetworks'].get('objects'):
            print("  Destination Networks:", rule.get('destinationNetworks'))
            for destination_object in rule['destinationNetworks']['objects']:
                object_id = destination_object.get('id')
                print(f"    ID do objeto de destino encontrado: {object_id}")
                if object_id and object_id in static_objects_by_id:
                    print(f"    IPs correspondentes (destino):", static_objects_by_id[object_id])
                    rule['destination_ips'].extend(static_objects_by_id[object_id])

    return render_template('policy_details.html', filename=filename, rules=rules)

@app.route('/sync', methods=['POST'])
def sync_data():
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':  # Verifica o cabeçalho AJAX
        try:
            print("Iniciando sincronização...")

            # Construct absolute paths to the scripts
            script_dir = os.path.dirname(os.path.abspath(__file__))  # Get directory of app.py
            fp_acp_path = os.path.join(script_dir, "FP_ACP.py")
            fp_do_path = os.path.join(script_dir, "FP_DynamicObject.py")
            fp_so_path = os.path.join(script_dir, "FP_StaticObject.py")

            # Get the current environment
            current_env = os.environ.copy()

            # Print environment variables from Flask for debugging
            #print("Environment variables from Flask:")
            #for key, value in current_env.items():
            #    print(f"{key}: {value}")

            # Print Python version for debugging
            print(f"Python version from Flask: {sys.version}")

            # Execute FP_ACP.py with explicit environment
            subprocess.run(['python', fp_acp_path], check=True, env=current_env)
            print("FP_ACP.py concluído.")
            #flash("Regras de Access Control Policies sincronizadas com sucesso!", 'success')
            
            # Execute FP_DynamicObjects.py with explicit environment
            subprocess.run(['python', fp_do_path], check=True, env=current_env)
            print("FP_DynamicObject.py concluído.")
            #flash("Objetos dinâmicos sincronizados com sucesso!", 'success')
            
            # Execute FP_StaticObjects.py with explicit environment
            subprocess.run(['python', fp_so_path], check=True, env=current_env)
            print("FP_StaticObject.py concluído.")
            #flash("Objetos estáticos sincronizados com sucesso!", 'success')
            
            return jsonify({'status': 'success', 'message': 'Sincronização concluída com sucesso!'})
        except subprocess.CalledProcessError as e:
            error_message = f"Erro durante a sincronização: {e}"
            print(error_message)
            #flash(error_message, 'error')
            return jsonify({'status': 'error', 'message': error_message})
        except FileNotFoundError:
            error_message = "Erro: Um ou mais scripts de sincronização não foram encontrados."
            print(error_message)
            #flash(error_message, 'error')
            return jsonify({'status': 'error', 'message': error_message})
    else:
        try:
            print("Iniciando sincronização...")

            # Construct absolute paths to the scripts
            script_dir = os.path.dirname(os.path.abspath(__file__))  # Get directory of app.py
            fp_acp_path = os.path.join(script_dir, "FP_ACP.py")
            fp_do_path = os.path.join(script_dir, "FP_DynamicObject.py")
            fp_so_path = os.path.join(script_dir, "FP_StaticObject.py")

            # Get the current environment
            current_env = os.environ.copy()

            # Print environment variables from Flask for debugging
            #print("Environment variables from Flask:")
            #for key, value in current_env.items():
            #    print(f"{key}: {value}")

            # Print Python version for debugging
            print(f"Python version from Flask: {sys.version}")

            # Execute FP_ACP.py with explicit environment
            subprocess.run(['python', fp_acp_path], check=True, env=current_env)
            print("FP_ACP.py concluído.")
            flash("Regras de Access Control Policies sincronizadas com sucesso!", 'success')
            # Execute FP_DynamicObjects.py with explicit environment
            subprocess.run(['python', fp_do_path], check=True, env=current_env)
            print("FP_DynamicObjects.py concluído.")
            flash("Objetos dinâmicos sincronizados com sucesso!", 'success')
            # Execute FP_StaticObjects.py with explicit environment
            subprocess.run(['python', fp_so_path], check=True, env=current_env)
            print("FP_StaticObjects.py concluído.")
            flash("Objetos estáticos sincronizados com sucesso!", 'success')
            return redirect(url_for('homepage'))
        except subprocess.CalledProcessError as e:
            flash(f"Erro durante a sincronização: {e}", 'error')
            return redirect(url_for('homepage'))
        except FileNotFoundError:
            flash("Erro: Um ou mais scripts de sincronização não foram encontrados.", 'error')
            return redirect(url_for('homepage'))

@app.route('/dynamic_objects')
def dynamic_objects():
        dynamic_objects = get_dynamic_objects()
        if dynamic_objects is None:
            flash("Objetos dinâmicos ainda não foram sincronizados. Por favor, sincronize.", 'warning')
            return redirect(url_for('homepage'))
        return render_template('dynamic_objects.html', dynamic_objects=dynamic_objects)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port='443',debug=True)