import xmlrpc.client
from getpass import getpass
from sagu.dataex import save_to_csv, generate_report
from datetime import date

# Enter Odoo server information
url = input('Enter URL: ')
db = input('Enter database: ')
#year = input('What year to extract from? ')
username = input('Username: ')
password = getpass()

# Create a dictionary to store Down Payment references
down_payment_references = {}

# CSV reports filename 
date_today = date.today().strftime("%Y.%m.%d")
monthly_payments_csv_filename = f'monthly_payments_{date_today}.csv'
monthly_invoices_csv_filename = f'monthly_invoices_{date_today}.csv' 

# Authenticate and obtain the user's session ID
common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
uid = common.authenticate(db, username, password, {})

# Create a new client object for the authenticated user
models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

# Define the model and fields you want to access (e.g., account.invoice for invoices)
model = 'account.payment' #model name for Customer Payments
fields = ['id', 'date', 'amount', 'payment_method_line_id', 'name', 'move_id', 'partner_id', 'state']

# Search for payments (you can add filters if needed)
payment_ids = models.execute_kw(db, uid, password, model, 'search', [[]])
payments = models.execute_kw(db, uid, password, model, 'read', [payment_ids], {'fields': fields})

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

# Extract data from general ledger
for ledger_row in general_ledger:
    if ledger_row['name'] == 'Down Payment':
        down_payment_references[ledger_row['partner_id'][-1]] = ledger_row['credit']

print('\nGenerating monthly payment sums...')
monthly_payment_sums = generate_report(payments, down_payment_references)
save_to_csv(monthly_payments_csv_filename, monthly_payment_sums)

print('\nGenerating monthly invoice sums...')
monthly_invoice_sums = generate_report(invoices, down_payment_references, 'invoice_date', 'amount_total')
save_to_csv(monthly_invoices_csv_filename, monthly_invoice_sums)