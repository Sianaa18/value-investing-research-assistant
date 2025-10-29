import os
import requests

FMP_API_KEY = os.getenv("FMP_API_KEY")

def fmp_get(endpoint, symbol):
    base_url = f"https://financialmodelingprep.com/api/v4/{endpoint}?symbol={symbol}&apikey={FMP_API_KEY}"
    r = requests.get(base_url)
    if r.status_code == 403:
        raise Exception("❌ FMP API: Forbidden. This endpoint is not available on your current FMP plan.")
    r.raise_for_status()
    return r.json()

def get_company_data(symbol):
    """Collect company data using only free FMP endpoints."""
    quote = fmp_get("quote", symbol)
    ratios = fmp_get("ratios", symbol)
    growth = fmp_get("financial-growth", symbol)
    enterprise = fmp_get("enterprise-values", symbol)
    
    return {
        "quote": quote,
        "ratios": ratios,
        "growth": growth,
        "enterprise": enterprise,
    }
