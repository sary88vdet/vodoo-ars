import xmlrpc.client, ssl
from getpass import getpass
from datetime import date, datetime
from vodoo.ars import year_sums, generate_report, save_to_csv

url = input('Enter URL: ')
db = input('Enter database: ')
username = input('Username: ')
password = getpass()

odoo_version = input('Enter Odoo version: ')

if int(odoo_version) == 13:
    payment_fields = ['id', 'payment_date', 'amount', 'payment_method_id', 'name', 'move_name', 'partner_id', 'state']
    payment_date = 'payment_date'
else:
    payment_fields = ['id', 'date', 'amount', 'payment_method_line_id', 'name', 'move_id', 'partner_id', 'state']
    payment_date = 'date'

# Authenticate and obtain the user's session ID
try:
    common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common', context=ssl._create_unverified_context())
    uid = common.authenticate(db, username, password, {})
except xmlrpc.client.Fault as error:
    print(f'FATAL: Database "{db}" does not exist')
    sys.exit(1)     

# Connect to the database
models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url), context=ssl._create_unverified_context())

def get_objects(model, fields, object_ids=None, domain=None):
    if not object_ids:
        if not domain:
            domain = []
        try:
            object_ids = models.execute_kw(db, uid, password, model, 'search', [domain])
        except xmlrpc.client.Fault as error:
            print(f'Error: {error}')
            sys.exit(1)
    return models.execute_kw(db, uid, password, model, 'read', [object_ids], {'fields': fields})

# Add an input for the company name or ID
company = input('Enter company name: ')
company_id = models.execute_kw(db, uid, password, 'res.company', 'search', [[('name', '=', company)]])
domain = [['company_id', '=', company_id]] if company_id else None

payments_all = get_objects('account.payment', ['id', 'payment_date', 'amount', 'payment_method_id', 'name', 'move_name', 'partner_id', 'state'], domain=domain)

# Search for customers with non-empty 'invoice_ids'
customer_model = 'res.partner'
customers_with_invoices = models.execute_kw(db, uid, password, customer_model, 'search_read', [[['invoice_ids', '!=', False]]], {'fields': ['id', 'name', 'street', 'invoice_ids']})

customers_with_data = []
for customer in customers_with_invoices:
    
    invoice_ids = customer['invoice_ids']
    invoices = get_objects('account.move', ['name', 'invoice_date', 'amount_total'], invoice_ids)
    invoices_with_dates = [invoice for invoice in invoices if invoice['invoice_date']]
    print(invoices_with_dates)
   
    payments = []
    for payment in payments_all:
        if payment['partner_id'][0] == customer['id']:
            payments.append(payment)

    yearly_invoice_sums = year_sums(invoices_with_dates, 'invoice_date', 'amount_total')
    yearly_payment_sums = year_sums(payments, payment_date)

    customer['old_debts'] = generate_report(yearly_invoice_sums, yearly_payment_sums)
    customer['expected'] = yearly_invoice_sums
    customer['real'] = yearly_payment_sums
    
    customers_with_data.append(customer)
    
save_to_csv(customers_with_data)