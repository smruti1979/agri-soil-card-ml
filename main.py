import os
import qrcode
from fastapi import FastAPI, Query, HTTPException, Depends, Form, status
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse
from database import SessionLocal, LandRecord, init_db
from analytics import AgriAnalyticsEngine

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Image, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

import auth
import views

app = FastAPI(title="Intelligent Agriculture Gateway")
analytics = AgriAnalyticsEngine()

# ⚠️ CHANGE THIS LINK BELOW EVERY TIME YOU RESTART LOCALTUNNEL!
SERVER_ENDPOINT = "https://smart-agri-p88g.onrender.com/predict"

def get_db():
    db = SessionLocal()
    try: yield db
    finally: db.close()

@app.on_event("startup")
def startup():
    init_db()

@app.get("/", include_in_schema=False)
async def homepage_shortcut():
    """Automatically redirects anyone hitting the bare URL straight to the admin portal."""
    return RedirectResponse(url="/admin/register", status_code=303)

@app.get("/admin/register", response_class=HTMLResponse)
async def get_registration_page(db=Depends(get_db), user: str = Depends(auth.authenticate_admin)):
    all_farmers = db.query(LandRecord).all()
    return HTMLResponse(content=views.render_admin_registration_form(user, all_farmers))

@app.post("/admin/register", response_class=HTMLResponse)
async def register_new_farmer(
    land_id: str = Form(...), farmer_name: str = Form(...), phone_number: str = Form(...),
    n: int = Form(...), p: int = Form(...), k: int = Form(...), ph: float = Form(...),
    lat: float = Form(...), lon: float = Form(...), db=Depends(get_db),
    user: str = Depends(auth.authenticate_admin)
):
    if db.query(LandRecord).filter(LandRecord.land_id == land_id).first():
        raise HTTPException(status_code=400, detail="Land ID already exists.")
    new_farm = LandRecord(land_id=land_id, farmer_name=farmer_name, phone_number=phone_number, nitrogen=n, phosphorus=p, potassium=k, ph=ph, latitude=lat, longitude=lon)
    db.add(new_farm)
    db.commit()
    return RedirectResponse(url="/admin/register", status_code=status.HTTP_303_SEE_OTHER)

@app.get("/admin/download-card")
async def dynamic_card_pdf_download(id: str = Query(...), db=Depends(get_db), user: str = Depends(auth.authenticate_admin)):
    farm = db.query(LandRecord).filter(LandRecord.land_id == id).first()
    if not farm: raise HTTPException(status_code=404, detail="Holdings record not found.")

    temp_dir = "runtime_qrs"
    os.makedirs(temp_dir, exist_ok=True)
    qr_path = f"{temp_dir}/{farm.land_id}.png"
    
    secure_url = f"{SERVER_ENDPOINT}?id={farm.land_id}"
    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_M, box_size=8, border=2)
    qr.add_data(secure_url)
    qr.make(fit=True)
    qr.make_image(fill_color="black", back_color="white").save(qr_path)

    pdf_filename = f"soil_card_{farm.land_id}.pdf"
    doc = SimpleDocTemplate(pdf_filename, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=50, bottomMargin=40)
    story = []
    styles = getSampleStyleSheet()
    
    header_style = ParagraphStyle('HStyle', parent=styles['Heading2'], textColor=colors.HexColor("#16a34a"), spaceAfter=12, alignment=1)
    text_style = ParagraphStyle('TStyle', parent=styles['Normal'], fontSize=11, leading=16, textColor=colors.HexColor("#1e293b"))

    badge_html = f"""
    <font size="14" color="#1e3a8a"><b>OFFICIAL AGRICULTURAL RECORD</b></font><br/><br/>
    <b>Land Record ID :</b> {farm.land_id}<br/>
    <b>Farmer Name   :</b> {farm.farmer_name}<br/>
    <b>Contact Phone :</b> {farm.phone_number}<br/>
    <b>GPS Location  :</b> {farm.latitude}, {farm.longitude}<br/><br/>
    <b>Laboratory Soil Analysis Metrics:</b><br/>
    • Nitrogen (N): {farm.nitrogen} mg/kg<br/>
    • Phosphorus (P): {farm.phosphorus} mg/kg<br/>
    • Potassium (K): {farm.potassium} mg/kg<br/>
    • Soil Base pH: {farm.ph}
    """
    
    card_table = Table([[Paragraph(badge_html, text_style), Image(qr_path, width=140, height=140)]], colWidths=[350, 150])
    card_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'), ('ALIGN', (1,0), (1,0), 'RIGHT'), ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f8fafc")),
        ('BOX', (0,0), (-1,-1), 2, colors.HexColor("#16a34a")), ('TOPPADDING', (0,0), (-1,-1), 20), ('BOTTOMPADDING', (0,0), (-1,-1), 20),
        ('LEFTPADDING', (0,0), (0,0), 20), ('RIGHTPADDING', (1,0), (1,0), 20),
    ]))

    story.append(Paragraph("🏛️ DEPARTMENT OF AGRICULTURE - NATIONAL SOIL REGISTRY", header_style))
    story.append(Spacer(1, 30))
    story.append(card_table)
    story.append(Spacer(1, 20))
    story.append(Paragraph("<font size='9' color='#64748b'><i>Disclaimer: Scan via authenticated mobile devices to query live climate optimization models.</i></font>", text_style))
    
    doc.build(story)
    if os.path.exists(qr_path): os.remove(qr_path)

    return FileResponse(path=pdf_filename, filename=pdf_filename, media_type='application/pdf')

@app.get("/predict", response_class=HTMLResponse)
async def process_qr_scan(id: str = Query(..., alias="id"), db=Depends(get_db), user: str = Depends(auth.authenticate_inspector)):
    farm = db.query(LandRecord).filter(LandRecord.land_id == id).first()
    if not farm: raise HTTPException(status_code=404, detail="Soil card record not found.")

    temp, humidity, rainfall = await analytics.fetch_live_weather(farm.latitude, farm.longitude)
    crop, confidence = analytics.predict_crop(farm.nitrogen, farm.phosphorus, farm.potassium, farm.ph, humidity, temp, rainfall)
    expected_yield, fertilizer = analytics.calculate_optimization(crop, farm.nitrogen, farm.phosphorus, farm.potassium, rainfall)

    html_layout = views.render_inspector_dashboard(user, farm, temp, humidity, rainfall, crop, confidence, expected_yield, fertilizer)
    return HTMLResponse(content=html_layout)
