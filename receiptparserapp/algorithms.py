# algorithms.py

from typing import List, Dict, Any, Callable
from datetime import datetime



# --- Search and Filter Algorithms ---
def filter_receipts(
    receipts: List[Dict[str, Any]],
    vendor_keyword: str = "",
    date_range: tuple = (None, None),
    amount_range: tuple = (None, None)
) -> List[Dict[str, Any]]:
    """
    Applies multiple filters to a list of receipts.
    This simulates search and filtering on the fetched data.
    """
    filtered_data = receipts

    # Keyword search on vendor
    if vendor_keyword:
        filtered_data = [r for r in filtered_data if vendor_keyword.lower() in r['vendor'].lower()]

    # Date filter
    if date_range and date_range[0] and date_range[1]:
        start_date, end_date = date_range
        def parse_date(d):
            if isinstance(d, datetime):
                return d.date()
            elif isinstance(d, str):
                return datetime.strptime(d, "%Y-%m-%d").date()
            elif isinstance(d, (datetime.date, )):
                return d
            else:
                return None

        filtered_data = [
            r for r in filtered_data
            if parse_date(r['transaction_date']) >= start_date and parse_date(r['transaction_date']) <= end_date
        ]

    # Range search for amount
    min_amount, max_amount = amount_range
    if min_amount is not None:
        filtered_data = [r for r in filtered_data if r['amount'] >= min_amount]
    if max_amount is not None:
        filtered_data = [r for r in filtered_data if r['amount'] <= max_amount]
        
    return filtered_data

# --- Aggregation Functions ---
def calculate_aggregates(receipts: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Computes statistical aggregates for a list of receipts."""
    if not receipts:
        return {"total_spend": 0, "mean": 0, "median": 0, "mode": "N/A"}

    amounts = [r['amount'] for r in receipts]
    total_spend = sum(amounts)
    mean = total_spend / len(amounts)

    # Median
    sorted_amounts = sorted(amounts)
    n = len(sorted_amounts)
    mid = n // 2
    if n % 2 == 0:
        median = (sorted_amounts[mid - 1] + sorted_amounts[mid]) / 2
    else:
        median = sorted_amounts[mid]

    # Mode
    frequency: Dict[float, int] = {}
    for amount in amounts:
        frequency[amount] = frequency.get(amount, 0) + 1
    
    if not frequency:
        mode = "N/A"
    else:
        max_freq = max(frequency.values())
        modes = [k for k, v in frequency.items() if v == max_freq]
        mode = modes[0] if len(modes) == 1 else "Multiple"

    return {"total_spend": total_spend, "mean": mean, "median": median, "mode": mode}

def get_monthly_spend(receipts):
    monthly_totals = {}
    for r in receipts:
        # Ensure transaction_date is a datetime object
        date_obj = r['transaction_date']
        if isinstance(date_obj, str):
            date_obj = datetime.strptime(date_obj, "%Y-%m-%d")
        month_key = date_obj.strftime('%Y-%m')
        monthly_totals[month_key] = monthly_totals.get(month_key, 0) + r['amount']
    return monthly_totals

def get_vendor_frequency(receipts: List[Dict[str, Any]]) -> Dict[str, float]:
    """Calculates total spend per vendor for pie chart visualization."""
    vendor_spend: Dict[str, float] = {}
    for r in receipts:
        vendor = r['vendor']
        vendor_spend[vendor] = vendor_spend.get(vendor, 0) + r['amount']
    return vendor_spend