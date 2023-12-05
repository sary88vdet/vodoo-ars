import xmlrpc.client, sys
from getpass import getpass
from datetime import date, datetime
from vodoo.ars import year_sums, generate_report, save_to_csv

url = input('Enter URL: ')
db = input('Enter database: ')
username = input('Username: ')
password = getpass()

# Authenticate and obtain the user's session ID
try:
    common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
    uid = common.authenticate(db, username, password, {})
except xmlrpc.client.Fault as error:
    print(f'FATAL: Database "{db}" does not exist')
    sys.exit(1)     

# Connect to the database
models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))

def get_objects(model, fields, object_ids=None):
    if not object_ids:
        try:
            object_ids = models.execute_kw(db, uid, password, model, 'search', [[]])
        except xmlrpc.client.Fault as error:
            print(f'Error: {error}')
            sys.exit(1)
    return models.execute_kw(db, uid, password, model, 'read', [object_ids], {'fields': fields})

payments_all = get_objects('account.payment', ['id', 'date', 'amount', 'payment_method_line_id', 'name', 'move_id', 'partner_id', 'state'])

# Search for customers with non-empty 'invoice_ids'
customer_model = 'res.partner'
customers_with_invoices = models.execute_kw(db, uid, password, customer_model, 'search_read', [[['invoice_ids', '!=', False]]], {'fields': ['id', 'name', 'street', 'invoice_ids']})

customers_with_data = []
for customer in customers_with_invoices:
    
    invoice_ids = customer['invoice_ids']
    invoices = get_objects('account.move', ['name', 'invoice_date', 'amount_total'], invoice_ids)
    invoices_with_dates = [invoice for invoice in invoices if invoice['invoice_date']]
   
    payments = []
    for payment in payments_all:
        if payment['partner_id'][0] == customer['id']:
            payments.append(payment)

    yearly_invoice_sums = year_sums(invoices_with_dates, 'invoice_date', 'amount_total')
    yearly_payment_sums = year_sums(payments)

    customer['old_debts'] = generate_report(yearly_invoice_sums, yearly_payment_sums)
    customer['expected'] = yearly_invoice_sums
    customer['real'] = yearly_payment_sums
    
    customers_with_data.append(customer)
    
save_to_csv(customers_with_data) 