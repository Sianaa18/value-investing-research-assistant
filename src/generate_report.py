import os
import json
import yfinance as yf
import google.generativeai as genai
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from src.helper_fmp import get_company_data

# --- Fix: convert Timestamp keys to strings ---
def stringify_keys(obj):
    if isinstance(obj, dict):
        return {str(k): stringify_keys(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [stringify_keys(i) for i in obj]
    else:
        return obj

# --- Setup ---
TICKER = os.getenv("TICKER", "AAPL")
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

print(f"📊 Fetching financial data for {TICKER}...")
data = get_company_data(TICKER)
safe_data = stringify_keys(data)

prompt = f"""
You are a world-class value investor assistant.
Analyze the following company data and write a long-term investment summary
in Warren Buffett’s style (clear, reasoned, and educational).

Company data:
{json.dumps(safe_data, indent=2)}
"""

print("🧠 Using Gemini to analyze the company...")
model = genai.GenerativeModel("gemini-1.5-pro")
response = model.generate_content(prompt)

analysis = response.text if hasattr(response, "text") else str(response)

# --- Generate PDF ---
print("📝 Generating PDF report...")
pdf_path = f"reports/{TICKER}_investment_report.pdf"
os.makedirs("reports", exist_ok=True)

c = canvas.Canvas(pdf_path, pagesize=A4)
c.setFont("Helvetica", 12)
c.drawString(100, 800, f"Value Investment Report for {TICKER}")
text = c.beginText(50, 770)
text.setFont("Helvetica", 10)
for line in analysis.splitlines():
    text.textLine(line)
c.drawText(text)
c.save()

print(f"✅ Report generated: {pdf_path}")
