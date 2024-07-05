from datetime import datetime, timedelta
import calendar


def get_pay_period(date_str):
    date = datetime.strptime(date_str, '%d/%m/%Y')  # Parse the date string to a datetime object

    if date.day <= 15:
        start_date = date.replace(day=1)
        end_date = date.replace(day=15)
    else:
        start_date = date.replace(day=16)

        # Handle end of the month
        last_date = calendar.monthrange(date.year, date.month)[1]  # back to the last day of the original month
        end_date = date.replace(day=last_date)

    return {'startDate': start_date.strftime('%Y-%m-%d'), 'endDate': end_date.strftime('%Y-%m-%d')}




# Example usage:
date_str = "21/07/2023"
pay_period = get_pay_period(date_str)
print(pay_period)  # Output: {'startDate': '2023-07-01', 'endDate': '2023-07-15'}
