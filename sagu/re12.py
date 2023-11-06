# Vodoo ARS (VDET Odoo Automated Reports Software)
# By Sary 2023 - sary88vdet@gmail.com

import csv
from datetime import datetime
import calendar

def save_to_csv(base_filename, invoice_sums, payment_sums, address_map):
    # First extract key and value from invoice
    for year, customer in invoice_sums.items():
        # invoice_sums and payment_sums are a dictionary within a dictionary
        print(f'Printing customer {customer}!!!')
        first_iteration = True
        for value in customer.values():
            if first_iteration:
                keys = list(reversed(list(value[-1].keys())))
                first_iteration = False
            
        filename = f'{base_filename}_{year}.csv'
        with open(filename, 'w', newline='') as outfile:
            writer = csv.writer(outfile)
            writer.writerow(['Contract', 'Address'] + [key + ' ' + str(year) for key in keys for _ in range(3)])
            writer.writerow(['', ''] + ['Expected', 'Real', 'Old debt'] * 12)
            for key, value in customer.items():
                row = []
                row.append(value[0]) #contract
                print(key)

                row.append(address_map[key]) 

                for month in keys:
                    print(f'{month}/{year}')
                    print(f'Invoice:: {customer[key][-1][month]}')
                    row.append(customer[key][-1][month])
                    try:
                        print(f'Payments:: {payment_sums[year][key][-1][month]}')
                        row.append(payment_sums[year][key][-1][month])
                    except KeyError:
                        print(f'Payments:: Key Error!')
                        row.append(0)
                    row.append('') # Placeholder for old debt                    
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
        #partner_id = record['partner_id'][-1]
        id_number, contract_name = record['partner_id']
        
        if year not in year_sums:
            year_sums[year] = {}
        
        if id_number not in year_sums[year]:
            year_sums[year][id_number] = [contract_name]
            year_sums[year][id_number].append(
             {
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
            )
            print(year_sums[year][id_number])

        if record['partner_id'] and contract_name in downpayment_filter.keys():
            if downpayment_filter[contract_name] == amount:
                print(f'Customer {contract_name} amount {amount} is a downpayment!')
                continue
            else:
                print(f'Adding record {record["name"]} with amount {amount} to report.')
                year_sums[year][id_number][-1][month] += amount
    
    print(f'YEAR SUMS: {year_sums}')
    return year_sums
