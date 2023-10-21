import csv
from datetime import datetime
import calendar

def save_to_csv(base_filename, year_sums):
    for year, month_sums in year_sums.items():
        filename = f'{base_filename}_{year}.csv'
        with open(filename, 'w', newline='') as outfile:
            writer = csv.writer(outfile)
            writer.writerow(['Month'] + list(month_sums.keys()))
            writer.writerow(['Total Amount'] + list(month_sums.values()))
        print(f'Finished writing AR92 CSV report for {year} to {filename}.')

def save_to_csv_ar93(base_filename, invoice_sums, payment_sums):
    # First extract key and value from invoice
    for year, customer in invoice_sums.items():
        # It's a dictionary within a dictionary
        print(f'Printing customer {customer}')
        first_iteration = True
        for value in customer.values():
            if first_iteration:
                keys = list(reversed(list(value.keys())))
                first_iteration = False
            
        filename = f'{base_filename}_{year}.csv'
        with open(filename, 'w', newline='') as outfile:
            writer = csv.writer(outfile)
            writer.writerow(['Contract', 'Address'] + [key for key in keys for _ in range(2)])
            
            for key, value in customer.items():
                row = []
                row.append(key)
                row.append('placeholder')
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

# Generate report for monthly payments
def generate_report(records, downpayment_filter=dict(), date_key='date', amount_key='amount'):
    # Reset values of month sums to 0
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
        
        if year not in year_sums:
            year_sums[year] = {
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
        
        if record['partner_id'] and record['partner_id'][-1] in downpayment_filter.keys():
            if downpayment_filter[record['partner_id'][-1]] == amount:
                print(f'\"{record["partner_id"][-1]}\" amount {amount} is a downpayment! Not adding in the report.')
                continue
            else:
                print(f'Adding \"{record["partner_id"][-1]}\" amount {amount} to the report.')
                year_sums[year][month] += amount
        elif record['partner_id']:
            print(f'Adding \"{record["partner_id"][-1]}\" amount {amount} to the report.')
            year_sums[year][month] += amount

    return year_sums

def generate_ar93(records, downpayment_filter=dict(), date_key='date', amount_key='amount'):
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
    #print(year_sums)

    for k, v in year_sums.items():
        print(k)
        if k == 2023:
            print('\n')
            print(year_sums[k])
    return year_sums
