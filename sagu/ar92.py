# Vodoo ARS (VDET Odoo Automated Reports Software)
# By Sary 2023 - sary88vdet@gmail.com
# Special thanks to Gufe - gufe88vdet@gmail.com

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