import os
import json
import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
import google.generativeai as genai
from helper_fmp import get_company_data

# --- Environment Variables ---
FMP_API_KEY = os.getenv("FMP_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
TICKER = os.getenv("TICKER", "AAPL")

# --- Setup Gemini ---
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel(GEMINI_MODEL)

# --- Fetch Financial Data ---
print(f"📊 Fetching financial data for {TICKER}...")
data = get_company_data(TICKER)

# --- Build Summary Prompt ---
prompt = f"""
You are an expert investment analyst like Warren Buffett.
Analyze the company {TICKER} using the data below.

Provide a clear, structured, and easy-to-understand long-term investment summary including:
1. Company overview (industry, main products, management)
2. Financial health (growth, profitability, debt, cash flow)
3. Intrinsic value hints (valuation ratios, margin of safety)
4. Moat and competitive position
5. Risks and opportunities
6. Final investment judgment (Value investor perspective)

Return your output as a well-organized textual report.

Company data (JSON):
{json.dumps(data, indent=2)}
"""

# --- Generate Analysis with Gemini ---
print("🧠 Generating investment analysis with Gemini...")
response = model.generate_content(prompt)
analysis_text = response.text

# --- Create PDF Report ---
print("📄 Creating PDF report...")
timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M")
pdf_filename = f"report_{TICKER}_{timestamp}.pdf"

doc = SimpleDocTemplate(pdf_filename, pagesize=A4)
styles = getSampleStyleSheet()
story = []

story.append(Paragraph(f"<b>Value Investing Report – {TICKER}</b>", styles["Title"]))
story.append(Spacer(1, 20))
story.append(Paragraph(analysis_text.replace("\n", "<br/>"), styles["Normal"]))

doc.build(story)
print(f"✅ Report saved as {pdf_filename}")
