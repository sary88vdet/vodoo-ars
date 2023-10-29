# Vodoo ARS (VDET Odoo Automated Reports Software)
# By Sary 2023 - sary88vdet@gmail.com

import csv
from datetime import datetime
import calendar

def save_to_csv(base_filename, invoice_sums, payment_sums):
    # First extract key and value from invoice
    for year, customer in invoice_sums.items():
        # invoice_sums and payment_sums are a dictionary within a dictionary
        print(f'Printing customer {customer}')
        first_iteration = True
        for value in customer.values():
            if first_iteration:
                keys = list(reversed(list(value.keys())))
                first_iteration = False
            
        filename = f'{base_filename}_{year}.csv'
        with open(filename, 'w', newline='') as outfile:
            writer = csv.writer(outfile)
            writer.writerow(['Contract', 'Address'] + [key + ' ' + str(year) for key in keys for _ in range(2)])
            writer.writerow(['', ''] + ['Expected', 'Real'] * 12)
            for key, value in customer.items():
                row = []
                row.append(key.split(' ')[0]) #contract
                row.append('') #placeholder for customer address
                for month in keys:
                    print(f'{month}/{year}')
                    print(f'Invoice:: {customer[key][month]}')
                    row.append(customer[key][month])
                    try:
                        print(f'Payments:: {payment_sums[year][key][month]}')
                        row.append(payment_sums[year][key][month])
                    except KeyError:
                        print(f'Payments:: Key Error!')
                        row.append(0)
                    
                print(row)
                writer.writerow(row)

def generate_report(records, downpayment_filter=dict(), date_key='date', amount_key='amount'):
    year_sums = {}

    for record in records:
        try:
            record_date = datetime.strptime(record[date_key], '%Y-%m-%d')
        except TypeError:
            print(f'Warning: record {record["name"]} has no date. Unable to add it to the report!')
            continue
        
        year = record_date.year
        month = calendar.month_name[record_date.month] 
        amount = float(record[amount_key])
        partner_id = record['partner_id'][-1]
        
        if year not in year_sums:
            year_sums[year] = {}
        
        if partner_id not in year_sums[year]:
            year_sums[year][partner_id] = {
                'January': 0,
                'February': 0,
                'March': 0,
                'April': 0,
                'May': 0,
                'June': 0,
                'July': 0,
                'August': 0,
                'September': 0,
                'October': 0,
                'November': 0,
                'December': 0,
            }
        
        if record['partner_id'] and partner_id in downpayment_filter.keys():
            if downpayment_filter[partner_id] == amount:
                print(f'Customer {partner_id} amount {amount} is a downpayment!')
                continue
            else:
                print(f'Adding record {record["name"]} with amount {amount} to report.')
                year_sums[year][partner_id][month] += amount
   
    return year_sums
