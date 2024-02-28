import calendar, csv
from datetime import datetime, date

def save_to_csv(customers):
    date_today = date.today().strftime("%Y.%m.%d")
    base_filename = input('Name to save CSV file: ') + f'_{date_today}'

    months = list(calendar.month_name)[1:]
    years = set()

    for customer in customers:
        old_debts = customer['old_debts']
        years.update(old_debts.keys())

    for year in years:    
        months_reversed = list(reversed(months))

        filename = f'{base_filename}_{year}.csv'
        with open(filename, 'w', newline='') as outfile:
            writer = csv.writer(outfile)
            writer.writerow(['Contract', 'Address'] + [f'{i}: {month} {year}' for month in months_reversed for i in range(1, 9)])
            writer.writerow(['', ''] + ['Expected Income', 'Real Income', 'Total Debt', 'Debt Before Payment', 'Current Month Debt', 'Debt After Payment', 'Current Month Income', 'Payment in Advance'] * 12)
            
            for customer in customers:
                row = []
                row.append(customer['name'])
                row.append(customer['street'])
                for month in months_reversed:
                    
                    row.append(customer['expected'].get(year, {}).get(month, '-'))
                    row.append(customer['real'].get(year, {}).get(month, '-'))
                    
                    if year in customer['old_debts']:
                        row.append(customer['old_debts'][year][month]['total_debt']) 
                        row.append(customer['old_debts'][year][month]['debt_before_payment'])
                        row.append(customer['old_debts'][year][month]['current_month_debt'])
                        row.append(customer['old_debts'][year][month]['debt_after_payment'])
                        row.append(customer['old_debts'][year][month]['current_month'])
                        row.append(customer['old_debts'][year][month]['payment_in_adv'])     
                writer.writerow(row)
        
def year_sums(records, date_key='date', amount_key='amount'):
    # Reset values of month sums to 0
    year_sums = {}
    sorted_year_sums = {}
    
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

        year_sums[year][month] += amount
        sorted_keys = sorted(year_sums.keys())
        sorted_year_sums = {key: year_sums[key] for key in sorted_keys}

    return sorted_year_sums

def process_payment(debt_previous_month, invoice, payment, payment_in_adv):
    # Initialize variables
    total_debt = 0
    debt_before_payment = 0
    current_month_debt = 0
    debt_after_payment = 0 
    current_month = 0
    #payment_in_adv = payment_in_adv

    # If without debt
    if debt_previous_month == 0:
        total_debt = debt_previous_month
        debt_before_payment = total_debt + invoice
        current_month_debt = 0

        if (payment + payment_in_adv) <= invoice:
            debt_after_payment = invoice - (payment + payment_in_adv)
            current_month = payment + payment_in_adv
            payment_in_adv = 0
        else:
            payment_in_adv = (payment + payment_in_adv) - invoice
            current_month = invoice
            debt_after_payment = 0

    # If with debt
    else:
        total_debt = debt_previous_month
        debt_before_payment = total_debt + invoice

        if (payment + payment_in_adv) <= total_debt:
            current_month_debt = (payment + payment_in_adv)
            debt_after_payment = invoice + (total_debt - (payment + payment_in_adv))
            current_month = 0
            payment_in_adv = 0
        else: #payment plus payment_in_adv is larger than total_debt
            current_month_debt = total_debt
            current_month = (payment + payment_in_adv) - total_debt
            if invoice >= current_month:
                debt_after_payment = invoice - current_month
                payment_in_adv = 0
            elif invoice < current_month:
                debt_after_payment = 0
                payment_in_adv = current_month - invoice

    # Return relevant values
    return {
        'total_debt': total_debt,
        'debt_before_payment': debt_before_payment,
        'current_month_debt': current_month_debt,
        'debt_after_payment': debt_after_payment,
        'current_month': current_month,
        'payment_in_adv': payment_in_adv
    }

def generate_report(invoice_sums, payment_sums):

    old_debts = {}
    debt_previous_month = 0
    payment_in_adv = 0

    for year, monthly_invoice_sums in invoice_sums.items():
        if year not in old_debts:
            old_debts[year] = {
                'January': {},
                'February': {},
                'March': {},
                'April':{},
                'May': {},
                'June': {},
                'July': {},
                'August': {},
                'September': {},
                'October': {},
                'November': {},
                'December': {},
            }

        for month, month_invoice_sum in monthly_invoice_sums.items():
            if month_invoice_sum == 0:
                # return all vars as 0
                old_debts[year][month]['total_debt'] = 0
                old_debts[year][month]['debt_before_payment'] = 0
                old_debts[year][month]['current_month_debt'] = 0
                old_debts[year][month]['debt_after_payment'] = 0
                old_debts[year][month]['current_month'] = 0
                old_debts[year][month]['payment_in_adv'] = 0
            else:
                old_debts[year][month] = process_payment(
                    debt_previous_month,
                    month_invoice_sum,
                    payment_sums.get(year, {}).get(month, 0),
                    payment_in_adv
                    )
            # Update the debt for previous month        
            debt_previous_month = old_debts[year][month]['debt_after_payment']        
            # Update the payment in advance for the next month
            payment_in_adv = old_debts[year][month]['payment_in_adv']

    return old_debts
