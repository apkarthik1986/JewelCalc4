"""Utility functions for JewelCalc"""
import random
import string
import re


def format_currency(amount):
    """Format amount as currency"""
    try:
        return f"₹{float(amount):,.2f}"
    except:
        return f"₹{amount}"


def generate_invoice_number():
    """Generate unique invoice number"""
    letters = ''.join(random.choices(string.ascii_uppercase, k=4))
    numbers = ''.join(random.choices(string.digits, k=6))
    return f"{letters}-{numbers}"


def generate_account_number(existing_accounts):
    """Generate next account number"""
    max_num = 0
    pattern = re.compile(r"CUS-(\d+)")
    
    for account in existing_accounts:
        match = pattern.match(str(account))
        if match:
            try:
                num = int(match.group(1))
                max_num = max(max_num, num)
            except:
                pass
    
    return f"CUS-{(max_num + 1):05d}"


def validate_phone(phone):
    """Validate phone number"""
    return phone.isdigit() and len(phone) == 10


def calculate_item_totals(weight, rate, wastage_percent, making_percent):
    """Calculate item totals"""
    item_value = float(weight) * float(rate)
    wastage_amount = item_value * float(wastage_percent) / 100
    making_amount = item_value * float(making_percent) / 100
    line_total = item_value + wastage_amount + making_amount
    
    return {
        'item_value': item_value,
        'wastage_amount': wastage_amount,
        'making_amount': making_amount,
        'line_total': line_total
    }
