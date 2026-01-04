from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from io import BytesIO
from datetime import datetime


def create_audit_pdf(risks_df, summary_text, total_tx=0, total_risk_val=0):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    # 1. Report Header
    # Custom Title Style
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Title'],
        fontSize=24,
        spaceAfter=10,
        textColor=colors.HexColor("#0E1117")
    )
    story.append(Paragraph("Month-End Audit Exception Report", title_style))
    story.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M')}", styles['Normal']))
    story.append(Spacer(1, 20))

    # --- NEW: Key Metrics Section ---
    # We calculate anomalies from the passed dataframe length
    anomalies_count = len(risks_df)

    # Create a 3-column table for metrics
    metrics_data = [
        ["Total Transactions", "Anomalies Detected", "Risk Value Exposure"],
        [str(total_tx), str(anomalies_count), f"${total_risk_val:,.2f}"]
    ]

    metrics_table = Table(metrics_data, colWidths=[150, 150, 150])
    metrics_table.setStyle(TableStyle([
        # Header Row Styling
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.gray),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),

        # Value Row Styling
        ('FONTNAME', (0, 1), (-1, 1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 1), (-1, 1), 18),
        ('ALIGN', (0, 1), (-1, 1), 'CENTER'),
        ('TEXTCOLOR', (1, 1), (1, 1), colors.red),  # Make Anomalies Count Red
        ('TEXTCOLOR', (2, 1), (2, 1), colors.darkred),  # Make Risk Value Dark Red

        # Spacing
        ('TOPPADDING', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('BOX', (0, 0), (-1, -1), 1, colors.lightgrey),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
    ]))

    story.append(metrics_table)
    story.append(Spacer(1, 25))
    # -------------------------------

    # 3. Executive Summary (from AI)
    story.append(Paragraph("Executive Summary & Recommendations", styles['Heading2']))

    # Handle newlines in AI text cleanly
    if summary_text:
        for line in summary_text.split('\n'):
            if line.strip():
                story.append(Paragraph(line, styles['Normal']))
                story.append(Spacer(1, 6))
    else:
        story.append(Paragraph("No summary available.", styles['Normal']))

    story.append(Spacer(1, 20))

    # 4. Risk Table
    story.append(Paragraph("High Priority Exceptions Detected", styles['Heading2']))

    if not risks_df.empty:
        # Prepare Data for Table
        # Headers
        table_data = [['Severity', 'Vendor', 'GL Code', 'Amount', 'Risk Reason']]

        # Sort by Risk (High first) just in case
        # Note: We expect the DF passed to be filtered for risks already

        for _, row in risks_df.iterrows():
            # Truncate long reasons
            reason = str(row.get('anomaly_reason', ''))
            reason = reason.replace('🤖', '').strip()  # Clean emoji
            if len(reason) > 60:
                reason = reason[:57] + "..."

            severity = row.get('severity', 'Low')

            table_data.append([
                severity,
                row.get('vendor', 'N/A'),
                str(row.get('gl_code', 'N/A')),
                f"${row.get('amount', 0):,.2f}",
                reason
            ])

        # Table Style
        t = Table(table_data, colWidths=[50, 90, 50, 70, 200])

        # Base Style
        style_cmds = [
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#2C3E50")),  # Dark Blue Header
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]

        # Row coloring logic
        for i, row in enumerate(table_data[1:]):  # Skip header
            bg_color = colors.whitesmoke if i % 2 == 0 else colors.white
            severity = row[0]

            # Highlight High severity rows slightly
            if severity == "High":
                bg_color = colors.HexColor("#FFF0F0")  # Light Red tint

            style_cmds.append(('BACKGROUND', (0, i + 1), (-1, i + 1), bg_color))
            style_cmds.append(
                ('TEXTCOLOR', (0, i + 1), (0, i + 1), colors.darkred if severity == "High" else colors.black))

        t.setStyle(TableStyle(style_cmds))
        story.append(t)
    else:
        story.append(Paragraph("No high priority risks found.", styles['Normal']))

    doc.build(story)
    buffer.seek(0)
    return buffer