# Vodoo ARS (VDET Odoo Automated Reports Software)
# By Sary 2023 - sary88vdet@gmail.com

import xmlrpc.client, sys
from getpass import getpass
from datetime import date
from sagu.rexx import save_to_csv, generate_report

# Enter Odoo server information
url = input('Enter URL: ')
db = input('Enter database: ')
username = input('Username: ')
password = getpass()

# CSV reports filename 
date_today = date.today().strftime("%Y.%m.%d") 
re12_csv_filename = f'vdet_re12_{date_today}'

# Authenticate and obtain the user's session ID
try:
    common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
    uid = common.authenticate(db, username, password, {})
except:
    print(f'Wrong password or invalid username.')
    sys.exit(1)        

# Create a new client object for the authenticated user
models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

def get_objects(model, fields):
    try:
        object_ids = models.execute_kw(db, uid, password, model, 'search', [[]])
    except xmlrpc.client.Fault as error:
        print(f'Error: {error}')
        sys.exit(1)
    return models.execute_kw(db, uid, password, model, 'read', [object_ids], {'fields': fields})

payments = get_objects('account.payment', ['id', 'date', 'amount', 'payment_method_line_id', 'name', 'move_id', 'partner_id', 'state'])

invoices = get_objects('account.move', ['id', 'name', 'partner_id', 'invoice_date', 'invoice_date_due',
        'amount_untaxed', 'amount_total', 'payment_state', 'state'])

customers = get_objects('res.partner', ['id', 'street'])

address_map = {}
for customer in customers:
    address_map[customer['id']] = customer['street']

print("Generating report for RE13")
monthly_payment_sums = generate_report(payments)
monthly_invoice_sums = generate_report(invoices, 'invoice_date', 'amount_total')
save_to_csv(monthly_invoice_sums, monthly_payment_sums, address_map)