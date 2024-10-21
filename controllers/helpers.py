from babel.numbers import format_currency

def format_to_indian_currency(value):
    return format_currency(value, 'INR', locale='en_IN')
