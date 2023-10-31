# Vodoo ARS (VDET Odoo Automated Reports Software)
# By Sary 2023 - sary88vdet@gmail.com

import xmlrpc.client
from getpass import getpass
from datetime import date
import sys

# Enter Odoo server information
url = input('Enter URL: ')
db = input('Enter database: ')
username = input('Username: ')
password = getpass()
# Prompt the user for a choice
user_choice = input("Enter 'A' to generate AR92 or 'B' to generate RE11: ")

# Create a dictionary to store Down Payment references
down_payment_references = {}

# CSV reports filename 
date_today = date.today().strftime("%Y.%m.%d")
monthly_payments_csv_filename = f'monthly_payments_{date_today}.csv'
monthly_invoices_csv_filename = f'monthly_invoices_{date_today}.csv' 
re11_csv_filename = f'vdet_re11_{date_today}'

# Authenticate and obtain the user's session ID
try:
    common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
    uid = common.authenticate(db, username, password, {})
except:
    print(f'Exception Error Occurred')
    sys.exit(1)        

# Create a new client object for the authenticated user
models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

# Define the model and fields you want to access (e.g., account.invoice for invoices)
model = 'account.payment' #model name for Customer Payments
fields = ['id', 'date', 'amount', 'payment_method_line_id', 'name', 'move_id', 'partner_id', 'state']

# Search for payments (you can add filters if needed)
try:
    payment_ids = models.execute_kw(db, uid, password, model, 'search', [[]])
except xmlrpc.client.Fault as error:
    print(f'Error: {error}')
    sys.exit(1)

payments = models.execute_kw(db, uid, password, model, 'read', [payment_ids], {'fields': fields})
#print(payments)

model = 'account.move.line' #model name for General Ledger
fields = ['id', 'move_id', 'name', 'debit', 'credit', 'balance',
        'cumulated_balance', 'partner_id']

# Search for payments (you can add filters if needed)
general_ledger_ids = models.execute_kw(db, uid, password, model, 'search', [[]])
general_ledger = models.execute_kw(db, uid, password, model, 'read', [general_ledger_ids], {'fields': fields})

# Define the model and fields you want to access (e.g., account.invoice for invoices)
model = 'account.move' #model name for Customer Invoices
fields = ['id', 'name', 'partner_id', 'invoice_date', 'invoice_date_due',
        'amount_untaxed', 'amount_total', 'payment_state', 'state']

# Search for invoices (you can add filters if needed)
invoice_ids = models.execute_kw(db, uid, password, model, 'search', [[]])
invoices = models.execute_kw(db, uid, password, model, 'read', [invoice_ids], {'fields': fields})
#print(f'PRINTING INVOICE IDS: {invoice_ids}')

model = 'res.partner'
fields = ['id', 'street']

customer_ids = models.execute_kw(db, uid, password, model, 'search', [[]])
customers = models.execute_kw(db, uid, password, model, 'read', [customer_ids], {'fields': fields})

address_map = {}
for customer in customers:
    address_map[customer['id']] = customer['street']

# Extract data from general ledger
for ledger_row in general_ledger:
    if ledger_row['name'] == 'Down Payment':
        down_payment_references[ledger_row['partner_id'][-1]] = ledger_row['credit']

# Check the user's choice
if user_choice == 'A':
    print("Generating report for AR92")
    from sagu.ar92 import save_to_csv, generate_report
elif user_choice == 'B':
    print("Generating report for RE11")
    from sagu.re11 import save_to_csv, generate_report
else:
    print("Invalid input. Please enter 'A' or 'B'.")

print('\nGenerating monthly payment sums...')
monthly_payment_sums = generate_report(payments, down_payment_references)

print('\nGenerating monthly invoice sums...')
monthly_invoice_sums = generate_report(invoices, down_payment_references, 'invoice_date', 'amount_total')

if user_choice == 'A':
    save_to_csv(monthly_payments_csv_filename, monthly_payment_sums, models)
    #save_to_csv(monthly_invoices_csv_filename, monthly_invoice_sums)
elif user_choice == 'B':
    save_to_csv(re11_csv_filename, monthly_invoice_sums, monthly_payment_sums, address_map)