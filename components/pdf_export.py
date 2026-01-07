"""
REI Nationwide LLC - PDF Export
Generate professional underwriting packages as PDF
"""

from typing import Dict, Optional
from datetime import datetime
from io import BytesIO
import base64


def generate_html_report(deal_data: Dict) -> str:
    """
    Generate HTML report for PDF conversion

    Args:
        deal_data: Dictionary with all deal information and calculations

    Returns:
        HTML string ready for PDF conversion
    """
    # Extract data
    address = deal_data.get('address', 'N/A')
    arv = deal_data.get('arv', 0)
    purchase_price = deal_data.get('purchase_price', 0)
    rehab_budget = deal_data.get('rehab_budget', 0)
    estimated_rent = deal_data.get('estimated_rent', 0)
    sqft = deal_data.get('sqft', 0)
    bedrooms = deal_data.get('bedrooms', 'N/A')
    bathrooms = deal_data.get('bathrooms', 'N/A')

    # Calculations
    purchase_pct_arv = deal_data.get('purchase_pct_arv', 0)
    all_in_cost = deal_data.get('all_in_cost', 0)
    holding_costs = deal_data.get('holding_costs', 0)
    closing_costs_buy = deal_data.get('closing_costs_buy', 0)
    dscr = deal_data.get('dscr', 0)
    net_cashflow = deal_data.get('net_cashflow', 0)
    piti = deal_data.get('piti', 0)
    wholesale_fee = deal_data.get('wholesale_fee', 0)
    gross_profit = deal_data.get('gross_profit', 0)

    # Scoring
    deal_score = deal_data.get('deal_score', 'N/A')
    recommended_exit = deal_data.get('recommended_exit', 'N/A')
    score_reason = deal_data.get('score_reason', 'N/A')

    # Score colors
    score_colors = {
        'GREEN': '#10b981',
        'YELLOW': '#f59e0b',
        'RED': '#ef4444'
    }
    score_color = score_colors.get(deal_score, '#6b7280')

    # Generate report date
    report_date = datetime.now().strftime('%B %d, %Y at %I:%M %p')

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Underwriting Package - {address}</title>
        <style>
            @page {{
                size: letter;
                margin: 0.75in;
            }}

            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Helvetica', 'Arial', sans-serif;
                font-size: 11pt;
                line-height: 1.5;
                color: #1f2937;
            }}

            .header {{
                text-align: center;
                margin-bottom: 30px;
                padding-bottom: 20px;
                border-bottom: 3px solid #3b82f6;
            }}

            .company-name {{
                font-size: 24pt;
                font-weight: 700;
                color: #1e3a8a;
                margin: 0;
            }}

            .report-title {{
                font-size: 16pt;
                color: #4b5563;
                margin: 10px 0 5px 0;
            }}

            .report-date {{
                font-size: 9pt;
                color: #6b7280;
                margin: 0;
            }}

            .score-badge {{
                display: inline-block;
                background: {score_color};
                color: white;
                padding: 10px 30px;
                border-radius: 8px;
                font-size: 18pt;
                font-weight: 700;
                margin: 20px 0;
                text-align: center;
            }}

            .section {{
                margin: 25px 0;
            }}

            .section-title {{
                font-size: 14pt;
                font-weight: 600;
                color: #1e3a8a;
                border-bottom: 2px solid #e5e7eb;
                padding-bottom: 5px;
                margin-bottom: 15px;
            }}

            .property-info {{
                background: #f9fafb;
                padding: 15px;
                border-radius: 8px;
                margin-bottom: 15px;
            }}

            .info-row {{
                display: flex;
                justify-content: space-between;
                padding: 5px 0;
                border-bottom: 1px solid #e5e7eb;
            }}

            .info-label {{
                font-weight: 600;
                color: #4b5563;
            }}

            .info-value {{
                color: #1f2937;
            }}

            .metrics-grid {{
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 15px;
                margin: 15px 0;
            }}

            .metric-card {{
                background: #ffffff;
                border: 1px solid #e5e7eb;
                border-radius: 8px;
                padding: 12px;
            }}

            .metric-label {{
                font-size: 9pt;
                color: #6b7280;
                text-transform: uppercase;
                letter-spacing: 0.05em;
                margin-bottom: 5px;
            }}

            .metric-value {{
                font-size: 16pt;
                font-weight: 700;
                color: #1f2937;
            }}

            .metric-good {{
                color: #10b981;
            }}

            .metric-warning {{
                color: #f59e0b;
            }}

            .metric-bad {{
                color: #ef4444;
            }}

            .recommendation-box {{
                background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
                color: white;
                padding: 20px;
                border-radius: 8px;
                margin: 20px 0;
            }}

            .recommendation-title {{
                font-size: 14pt;
                font-weight: 600;
                margin: 0 0 10px 0;
            }}

            .recommendation-text {{
                font-size: 12pt;
                margin: 0;
            }}

            .calculation-table {{
                width: 100%;
                border-collapse: collapse;
                margin: 15px 0;
            }}

            .calculation-table th {{
                background: #f3f4f6;
                text-align: left;
                padding: 10px;
                font-weight: 600;
                border-bottom: 2px solid #d1d5db;
            }}

            .calculation-table td {{
                padding: 8px 10px;
                border-bottom: 1px solid #e5e7eb;
            }}

            .calculation-table tr.total {{
                font-weight: 700;
                background: #f9fafb;
                border-top: 2px solid #3b82f6;
            }}

            .footer {{
                margin-top: 40px;
                padding-top: 20px;
                border-top: 2px solid #e5e7eb;
                text-align: center;
                font-size: 9pt;
                color: #6b7280;
            }}

            .disclaimer {{
                margin-top: 30px;
                padding: 15px;
                background: #fef3c7;
                border-left: 4px solid #f59e0b;
                font-size: 9pt;
                color: #78350f;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1 class="company-name">REI Nationwide LLC</h1>
            <p class="report-title">Property Underwriting Package</p>
            <p class="report-date">Generated: {report_date}</p>
        </div>

        <div class="section">
            <div class="score-badge">{deal_score} DEAL</div>
        </div>

        <div class="section">
            <h2 class="section-title">Property Information</h2>
            <div class="property-info">
                <div class="info-row">
                    <span class="info-label">Address:</span>
                    <span class="info-value">{address}</span>
                </div>
                <div class="info-row">
                    <span class="info-label">Square Footage:</span>
                    <span class="info-value">{sqft:,} sqft</span>
                </div>
                <div class="info-row">
                    <span class="info-label">Bedrooms / Bathrooms:</span>
                    <span class="info-value">{bedrooms} bed / {bathrooms} bath</span>
                </div>
            </div>
        </div>

        <div class="section">
            <h2 class="section-title">Financial Summary</h2>
            <div class="metrics-grid">
                <div class="metric-card">
                    <div class="metric-label">After Repair Value (ARV)</div>
                    <div class="metric-value">${arv:,.0f}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Purchase Price</div>
                    <div class="metric-value">${purchase_price:,.0f}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Purchase % ARV</div>
                    <div class="metric-value {'metric-good' if purchase_pct_arv <= 0.45 else 'metric-warning' if purchase_pct_arv <= 0.60 else 'metric-bad'}">
                        {purchase_pct_arv*100:.1f}%
                    </div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Rehab Budget</div>
                    <div class="metric-value {'metric-good' if rehab_budget <= 20000 else 'metric-warning' if rehab_budget <= 30000 else 'metric-bad'}">
                        ${rehab_budget:,.0f}
                    </div>
                </div>
            </div>
        </div>

        <div class="section">
            <h2 class="section-title">Cost Breakdown</h2>
            <table class="calculation-table">
                <thead>
                    <tr>
                        <th>Item</th>
                        <th style="text-align: right;">Amount</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>Purchase Price</td>
                        <td style="text-align: right;">${purchase_price:,.0f}</td>
                    </tr>
                    <tr>
                        <td>Rehab Budget</td>
                        <td style="text-align: right;">${rehab_budget:,.0f}</td>
                    </tr>
                    <tr>
                        <td>Holding Costs</td>
                        <td style="text-align: right;">${holding_costs:,.0f}</td>
                    </tr>
                    <tr>
                        <td>Closing Costs (Buy)</td>
                        <td style="text-align: right;">${closing_costs_buy:,.0f}</td>
                    </tr>
                    <tr class="total">
                        <td>All-In Cost</td>
                        <td style="text-align: right;">${all_in_cost:,.0f}</td>
                    </tr>
                </tbody>
            </table>
        </div>

        <div class="section">
            <h2 class="section-title">DSCR Analysis (Long-Term Hold)</h2>
            <div class="metrics-grid">
                <div class="metric-card">
                    <div class="metric-label">Monthly Rent</div>
                    <div class="metric-value">${estimated_rent:,.0f}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">PITI (Payment + Tax + Ins)</div>
                    <div class="metric-value">${piti:,.0f}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">DSCR</div>
                    <div class="metric-value {'metric-good' if dscr >= 1.30 else 'metric-warning' if dscr >= 1.20 else 'metric-bad'}">
                        {dscr:.2f}
                    </div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Net Cashflow/Month</div>
                    <div class="metric-value {'metric-good' if net_cashflow >= 175 else 'metric-warning' if net_cashflow >= 100 else 'metric-bad'}">
                        ${net_cashflow:,.0f}
                    </div>
                </div>
            </div>
        </div>

        <div class="section">
            <h2 class="section-title">Wholesale Analysis</h2>
            <div class="metrics-grid">
                <div class="metric-card">
                    <div class="metric-label">Wholesale Price (70% ARV)</div>
                    <div class="metric-value">${arv * 0.70:,.0f}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Potential Assignment Fee</div>
                    <div class="metric-value {'metric-good' if wholesale_fee >= 30000 else 'metric-warning' if wholesale_fee >= 25000 else 'metric-bad'}">
                        ${wholesale_fee:,.0f}
                    </div>
                </div>
            </div>
        </div>

        <div class="recommendation-box">
            <h3 class="recommendation-title">📌 Recommendation</h3>
            <p class="recommendation-text" style="font-size: 14pt; font-weight: 600; margin-bottom: 10px;">
                {recommended_exit}
            </p>
            <p class="recommendation-text">
                {score_reason}
            </p>
        </div>

        <div class="disclaimer">
            <strong>Disclaimer:</strong> This underwriting package is for informational purposes only and does not constitute financial, legal, or investment advice. All estimates are based on assumptions and should be verified independently. REI Nationwide LLC is not responsible for decisions made based on this analysis.
        </div>

        <div class="footer">
            <p><strong>REI Nationwide LLC</strong></p>
            <p>High-Velocity Distressed Property Acquisition</p>
            <p>Contact: www.reinationwide.com | info@reinationwide.com</p>
        </div>
    </body>
    </html>
    """

    return html


def html_to_pdf_weasyprint(html_content: str) -> BytesIO:
    """
    Convert HTML to PDF using WeasyPrint

    Args:
        html_content: HTML string

    Returns:
        BytesIO buffer with PDF content

    Note: Requires 'weasyprint' package
    Installation: pip install weasyprint
    """
    try:
        from weasyprint import HTML
        pdf_buffer = BytesIO()
        HTML(string=html_content).write_pdf(pdf_buffer)
        pdf_buffer.seek(0)
        return pdf_buffer
    except ImportError:
        raise ImportError(
            "WeasyPrint is not installed. Install with: pip install weasyprint\n"
            "Note: WeasyPrint requires system dependencies (cairo, pango). "
            "See https://doc.courtbouillon.org/weasyprint/stable/first_steps.html"
        )


def html_to_pdf_pdfkit(html_content: str) -> BytesIO:
    """
    Convert HTML to PDF using pdfkit (wkhtmltopdf wrapper)

    Args:
        html_content: HTML string

    Returns:
        BytesIO buffer with PDF content

    Note: Requires 'pdfkit' package and wkhtmltopdf binary
    Installation:
    - pip install pdfkit
    - Install wkhtmltopdf: https://wkhtmltopdf.org/downloads.html
    """
    try:
        import pdfkit
        pdf_bytes = pdfkit.from_string(html_content, False)
        pdf_buffer = BytesIO(pdf_bytes)
        pdf_buffer.seek(0)
        return pdf_buffer
    except ImportError:
        raise ImportError(
            "pdfkit is not installed. Install with: pip install pdfkit\n"
            "Also install wkhtmltopdf: https://wkhtmltopdf.org/downloads.html"
        )


def generate_pdf_underwriting_package(deal_data: Dict, method: str = 'html') -> BytesIO:
    """
    Generate PDF underwriting package

    Args:
        deal_data: Dictionary with all deal information
        method: 'html' (returns HTML), 'weasyprint', or 'pdfkit'

    Returns:
        BytesIO buffer with PDF content (or HTML string if method='html')
    """
    html_content = generate_html_report(deal_data)

    if method == 'html':
        # Return HTML as BytesIO for download
        buffer = BytesIO(html_content.encode('utf-8'))
        buffer.seek(0)
        return buffer

    elif method == 'weasyprint':
        return html_to_pdf_weasyprint(html_content)

    elif method == 'pdfkit':
        return html_to_pdf_pdfkit(html_content)

    else:
        raise ValueError(f"Unknown method: {method}. Use 'html', 'weasyprint', or 'pdfkit'")


def get_pdf_download_link(pdf_buffer: BytesIO, filename: str) -> str:
    """
    Generate base64 download link for PDF (for Streamlit)

    Args:
        pdf_buffer: BytesIO with PDF content
        filename: Suggested filename for download

    Returns:
        HTML link for download
    """
    b64 = base64.b64encode(pdf_buffer.read()).decode()
    return f'<a href="data:application/pdf;base64,{b64}" download="{filename}">Download PDF</a>'
