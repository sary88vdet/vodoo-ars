import csv
from datetime import datetime
import calendar

def save_to_csv(filename, month_sums):
    with open(filename, 'w', newline='') as outfile:
        writer = csv.writer(outfile)
        writer.writerow(['Month'] + list(month_sums.keys()))
        writer.writerow(['Total Amount'] + list(month_sums.values()))

# Generate report for monthly payments
def generate_report(records, downpayment_filter=dict()):
    # Reset values of month sums to 0
    month_sums = {
        'January': 0,
        'February': 0,
        'March': 0,
        'April':0,
        'May':0,
        'June': 0,
        'July': 0,
        'August': 0,
        'September': 0,
        'October': 0,
        'November': 0,
        'December': 0,
    }

    for record in records:
        record_date = datetime.strptime(record['date'], '%Y-%m-%d')
        month = calendar.month_name[record_date.month] 
        amount = float(record['amount'])
        
        if record['partner_id'][-1] in filter_downpayment.keys():
            if downpayment_filter[record['partner_id'][-1]] == amount:
                print(f'Customer {record["partner_id"]} amount {amount} is a downpayment!')
                continue
            else:
                print(f'Adding record {record["name"]} with amount {amount} to report.')
                month_sums[month] += amount
     return month_sums
