def formatAmountPaid(data):
    for key, value in data.items():
        amount_paid = value['amountPaid']
        integer_part = int(amount_paid)
        formatted_amount = f"${integer_part}.00"
        value['amountPaid'] = formatted_amount