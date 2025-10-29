import os
import requests

FMP_API_KEY = os.getenv("FMP_API_KEY")

def fmp_get(endpoint, symbol):
    """
    Fetch JSON data from FMP v4 API for the given endpoint and stock symbol.
    Example: fmp_get('company-profile', 'AAPL')
    """
    base_url = f"https://financialmodelingprep.com/api/v4/{endpoint}?symbol={symbol}&apikey={FMP_API_KEY}"
    r = requests.get(base_url)
    if r.status_code == 403:
        raise Exception("❌ FMP API: Forbidden. Your plan may not support this endpoint or your key is invalid.")
    r.raise_for_status()
    return r.json()

def get_company_data(symbol):
    """Collect key company data from FMP."""
    profile = fmp_get("company-profile", symbol)
    income = fmp_get("income-statement", symbol)
    balance = fmp_get("balance-sheet-statement", symbol)
    cashflow = fmp_get("cash-flow-statement", symbol)
    metrics = fmp_get("key-metrics", symbol)
    return {
        "profile": profile,
        "income": income,
        "balance": balance,
        "cashflow": cashflow,
        "metrics": metrics,
    }
