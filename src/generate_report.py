import os
import json
import requests
import google.generativeai as genai

# --- Setup Gemini ---
GENAI_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GENAI_API_KEY:
    raise ValueError("❌ Missing GOOGLE_API_KEY environment variable.")

genai.configure(api_key=GENAI_API_KEY)

# Use the latest stable model
model = genai.GenerativeModel("gemini-1.5-flash-latest")


def fetch_financial_data(ticker: str):
    """Fetch financial data from Yahoo Finance (simple example)."""
    print(f"📊 Fetching financial data for {ticker}...")
    url = f"https://query1.finance.yahoo.com/v10/finance/quoteSummary/{ticker}?modules=financialData"
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch data for {ticker}: HTTP {response.status_code}")
    data = response.json()
    return data


def analyze_with_gemini(ticker: str, data: dict):
    """Ask Gemini to analyze the company's financial data."""
    print("🧠 Using Gemini to analyze the company...")

    prompt = f"""
    You are a financial analyst specializing in value investing.
    Analyze the company {ticker} based on the following financial data:

    {json.dumps(data, indent=2)}

    Write a short, structured investment analysis report.
    Include sections:
    - Company Overview
    - Financial Highlights
    - Investment Risks
    - Conclusion (Buy / Hold / Sell recommendation)
    """

    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print("❌ Gemini API error:", e)
        raise


def save_report(ticker: str, report: str):
    """Save the generated report to a markdown file."""
    output_path = f"reports/{ticker}_report.md"
    os.makedirs("reports", exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"✅ Report saved: {output_path}")


if __name__ == "__main__":
    try:
        TICKER = os.getenv("STOCK_TICKER", "AAPL")
        data = fetch_financial_data(TICKER)
        report = analyze_with_gemini(TICKER, data)
        save_report(TICKER, report)
        print("✨ Report generation completed successfully!")
    except Exception as e:
        print("🚨 Error during report generation:", e)
        exit(1)
