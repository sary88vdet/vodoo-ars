import xmlrpc.client
from getpass import getpass

def get_available_models(url, db, username, password):
    # Authenticate and establish a connection
    common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
    uid = common.authenticate(db, username, password, {})

    # Create an XML-RPC object for executing methods
    models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

    try:
        # Fetch all model names from the 'ir.model' object
        model_ids = models.execute_kw(db, uid, password, 'ir.model', 'search', [[]])
        model_data = models.execute_kw(db, uid, password, 'ir.model', 'read', [model_ids], {'fields': ['model']})

        # Extract and return the model names
        model_names = [entry['model'] for entry in model_data]

        return model_names
    except Exception as e:
        raise e

def main():
    url = input('Enter URL: ')
    db = input('Enter database: ')
    username = input('Username: ')
    password = getpass()

    try:
        # Fetch and display the list of available models
        available_models = get_available_models(url, db, username, password)

        print("Available Odoo Models:")
        for model in available_models:
            print(model)

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()

