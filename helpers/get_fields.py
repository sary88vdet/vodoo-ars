import xmlrpc.client
from getpass import getpass

# Odoo server information
url = input('Enter URL: ')
db = input('Enter database: ')
username = input('Username: ')
password = getpass()

# Authenticate and obtain the user's session ID
common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
uid = common.authenticate(db, username, password, {})

# Create a new client object for the authenticated user
models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

# Define the model for which you want to retrieve the fields
model = input('Enter Odoo model: ')

# Retrieve the available fields for the model
fields = models.execute_kw(db, uid, password, model, 'fields_get', [], {})

# Print the available fields
print("Available fields for the model:", model)
for field_name, field_info in fields.items():
    print(f"Field Name: {field_name}")
    print(f"Field Label: {field_info['string']}")

# After listing the available fields, you can choose which fields to use in your code.
# Update the 'fields' list accordingly.

# Search for payments (you can add filters if needed)
#payment_ids = models.execute_kw(db, uid, password, model, 'search', [[]])
#payments = models.execute_kw(db, uid, password, model, 'read', [payment_ids])

# Print payment data using the selected fields
#for payment in payments:
#    print(payment)
#    print(f"Payment Date: {payment.get('date')}")
#    print(f"Payment Amount: {payment.get('amount')}")
#    print(f"Payment Number: {payment.get('check_number')}")

