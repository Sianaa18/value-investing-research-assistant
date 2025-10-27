# src/generate_report.py
import os
import requests
import pandas as pd
from datetime import datetime
from fpdf import FPDF
import textwrap

# Read env vars
FMP_API_KEY = os.environ.get('FMP_API_KEY')
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
GEMINI_MODEL = os.environ.get('GEMINI_MODEL', 'gemini-2.5-flash')
TICKER = os.environ.get('TICKER', 'AAPL').upper()

if not FMP_API_KEY or not GEMINI_API_KEY:
    raise SystemExit("Set FMP_API_KEY and GEMINI_API_KEY as environment variables.")

BASE_FMP = 'https://financialmodelingprep.com/api/v3'

def fmp_get(endpoint, params=None):
    p = {'apikey': FMP_API_KEY}
    if params:
        p.update(params)
    r = requests.get(f"{BASE_FMP}/{endpoint}", params=p, timeout=30)
    r.raise_for_status()
    return r.json()

# Fetch data
profile = fmp_get(f'profile/{TICKER}')
if isinstance(profile, list):
    profile = profile[0] if profile else {}
income = fmp_get(f'income-statement/{TICKER}', params={'limit': 5})
balance = fmp_get(f'balance-sheet-statement/{TICKER}', params={'limit': 5})
cash = fmp_get(f'cash-flow-statement/{TICKER}', params={'limit': 5})

# Build simple metrics
df_income = pd.DataFrame(income)
df_balance = pd.DataFrame(balance)
df_cash = pd.DataFrame(cash)

def latest(df, col):
    try:
        return float(df[col].dropna().astype(float).iloc[-1])
    except Exception:
        return None

metrics = {}
metrics['company'] = profile.get('companyName', TICKER)
metrics['revenue'] = latest(df_income, 'revenue')
metrics['netIncome'] = latest(df_income, 'netIncome')
metrics['freeCashFlow'] = latest(df_cash, 'freeCashFlow')
metrics['totalAssets'] = latest(df_balance, 'totalAssets')
metrics['totalLiabilities'] = latest(df_balance, 'totalLiabilities')
metrics['shareholderEquity'] = latest(df_balance, 'totalStockholdersEquity')

# Simple ratio
try:
    metrics['ROE'] = metrics['netIncome'] / metrics['shareholderEquity'] if metrics['shareholderEquity'] else None
except:
    metrics['ROE'] = None

# Build prompt text for Gemini
prompt = f"""
Act as a world-class value investor. Analyze {metrics['company']} ({TICKER}) for long-term value investing.
Include: Business Overview, Financial Performance (last 3-5 years) with metrics, Competitive Advantage, Management & Capital Allocation, Valuation & Intrinsic Value (reasoned range), Risks & Weaknesses, Long-Term Outlook, Investor Summary & Verdict.
Key metrics: {metrics}
"""

# Call Gemini REST API (REST example)
gl_url = f"https://generativelanguage.googleapis.com/v1beta2/models/{GEMINI_MODEL}:generateContent"
headers = {
    "Authorization": f"Bearer {GEMINI_API_KEY}",
    "Content-Type": "application/json; charset=utf-8",
}
payload = {
    "prompt": {"text": prompt},
    "temperature": 0.2,
    "maxOutputTokens": 1400
}
resp = requests.post(gl_url, headers=headers, json=payload, timeout=60)
resp.raise_for_status()
j = resp.json()

# Extract text (schema may differ; adapt if needed)
analysis_text = ""
if 'candidates' in j and j['candidates']:
    analysis_text = j['candidates'][0].get('content', '') or str(j['candidates'][0])
else:
    # fallback: stringify whole response
    analysis_text = str(j)

# Make a simple PDF
class PDFReport:
    def __init__(self, title, subtitle):
        self.pdf = FPDF()
        self.pdf.set_auto_page_break(auto=True, margin=15)
        self.title = title
        self.subtitle = subtitle

    def build(self, text):
        self.pdf.add_page()
        self.pdf.set_font("Arial", "B", 14)
        self.pdf.cell(0, 10, self.title, ln=True, align='C')
        self.pdf.set_font("Arial", "", 10)
        self.pdf.cell(0, 8, self.subtitle, ln=True, align='C')
        self.pdf.ln(6)
        self.pdf.set_font("Arial", "", 11)
        self.pdf.multi_cell(0, 6, text)

    def save(self, fname):
        self.pdf.output(fname)

title = f"Value Investing Report: {metrics['company']} ({TICKER})"
subtitle = f"Generated: {datetime.utcnow().isoformat()} UTC"
pdf = PDFReport(title, subtitle)
pdf.build(analysis_text)
out_fname = f"report_{TICKER}_{datetime.utcnow().strftime('%Y%m%d_%H%M')}.pdf"
pdf.save(out_fname)
print("Saved:", out_fname)
