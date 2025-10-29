import yfinance as yf
import pandas as pd

def get_company_data(symbol):
    """Fetch stock data using Yahoo Finance (free, no API key needed)."""
    ticker = yf.Ticker(symbol)

    info = ticker.info
    financials = ticker.financials
    balance_sheet = ticker.balance_sheet
    cashflow = ticker.cashflow

    # Convert all to readable strings for the PDF
    data = {
        "company_name": info.get("longName", symbol),
        "sector": info.get("sector", "N/A"),
        "industry": info.get("industry", "N/A"),
        "market_cap": info.get("marketCap", "N/A"),
        "pe_ratio": info.get("trailingPE", "N/A"),
        "dividend_yield": info.get("dividendYield", "N/A"),
        "financials": financials.to_dict(),
        "balance_sheet": balance_sheet.to_dict(),
        "cashflow": cashflow.to_dict(),
    }

    return data
