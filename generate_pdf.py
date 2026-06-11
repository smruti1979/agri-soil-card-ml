import os
import qrcode
from database import SessionLocal, LandRecord

# ReportLab core page structure components
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Image, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

# Change this URL payload string to match your active LocalTunnel link extension
SERVER_ENDPOINT = "https://new-llamas-itch.loca.lt/predict"

def build_single_page_soil_cards():
    db = SessionLocal()
    records = db.query(LandRecord).all()
    
    if not records:
        print("❌ Database registry records missing. Please execute main.py first.")
        db.close()
        return

    print("🛠️ Generating clean 1-Card-Per-Page PDF configuration layout sheets...")
    
    # 1. Initialize Document Canvas (Letter page size with balanced outer margins)
    pdf_filename = "printable_soil_cards.pdf"
    doc = SimpleDocTemplate(
        pdf_filename, 
        pagesize=letter, 
        rightMargin=40, 
        leftMargin=40, 
        topMargin=40, 
        bottomMargin=40
    )
    story = []
    
    # 2. Configure Typography Styles
    styles = getSampleStyleSheet()
    header_style = ParagraphStyle(
        'HeaderStyle', 
        parent=styles['Heading2'], 
        textColor=colors.HexColor("#16a34a"), 
        spaceAfter=12,
        alignment=1 # Center aligned header
    )
    text_style = ParagraphStyle(
        'TextStyle', 
        parent=styles['Normal'], 
        fontSize=11, 
        leading=16, 
        textColor=colors.HexColor("#1e293b")
    )

    os.makedirs("temp_qrs", exist_ok=True)
    
    total_records = len(records)
    for idx, rec in enumerate(records):
        # 3. Create Compact Secure URL payload barcode
        secure_url = f"{SERVER_ENDPOINT}?id={rec.land_id}"
        qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_M, box_size=8, border=2)
        qr.add_data(secure_url)
        qr.make(fit=True)
        
        qr_path = f"temp_qrs/{rec.land_id}.png"
        qr.make_image(fill_color="black", back_color="white").save(qr_path)
        
        # 4. Format Official Government Badge Display Data
        badge_html = f"""
        <font size="14" color="#1e3a8a"><b>OFFICIAL AGRICULTURAL RECORD</b></font><br/><br/>
        <b>Land Record ID :</b> {rec.land_id}<br/>
        <b>Farmer Name   :</b> {rec.farmer_name}<br/>
        <b>Contact Phone :</b> {rec.phone_number}<br/>
        <b>GPS Location  :</b> {rec.latitude}, {rec.longitude}<br/><br/>
        <b>Laboratory Soil Analysis Metrics:</b><br/>
        • Nitrogen (N): {rec.nitrogen} mg/kg<br/>
        • Phosphorus (P): {rec.phosphorus} mg/kg<br/>
        • Potassium (K): {rec.potassium} mg/kg<br/>
        • Soil Base pH: {rec.ph}
        """
        
        # 5. Arrange Content in a High-Contrast Table Block Matrix (Left: Text, Right: QR Barcode)
        card_content = [
            [Paragraph(badge_html, text_style), Image(qr_path, width=140, height=140)]
        ]
        
        # Width distribution perfectly fills the page layout canvas boundary metrics
        card_table = Table(card_content, colWidths=[340, 160])
        card_table.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('ALIGN', (1,0), (1,0), 'RIGHT'),
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f8fafc")),
            ('BOX', (0,0), (-1,-1), 2, colors.HexColor("#16a34a")), # Heavy Green Outer Boundary Grid Box Border lines
            ('TOPPADDING', (0,0), (-1,-1), 20),
            ('BOTTOMPADDING', (0,0), (-1,-1), 20),
            ('LEFTPADDING', (0,0), (0,0), 20),
            ('RIGHTPADDING', (1,0), (1,0), 20),
        ]))
        
        # 6. Append structural elements to the page story flow
        story.append(Paragraph("🏛️ DEPARTMENT OF AGRICULTURE - NATIONAL SOIL REGISTRY", header_style))
        story.append(Spacer(1, 30))
        story.append(card_table)
        story.append(Spacer(1, 20))
        story.append(Paragraph("<font size='9' color='#64748b'><i>Disclaimer: This card contains static baseline soil profile matrix attributes. Scan via authenticated mobile devices to query live micro-climate optimization models.</i></font>", text_style))
        
        # 7. Force an immediate new page break unless it's the absolute final row record 
        if idx < total_records - 1:
            story.append(PageBreak())

    # Build the cumulative compiled file
    doc.build(story)

    # Post-execution file tree clean up loops
    for file in os.listdir("temp_qrs"): 
        os.remove(f"temp_qrs/{file}")
    os.rmdir("temp_qrs")
    print(f"🎉 Document Compiled Successfully: 1-Card-Per-Page structure appended into '{pdf_filename}' ({total_records} Total Pages).")

if __name__ == "__main__":
    build_single_page_soil_cards()
