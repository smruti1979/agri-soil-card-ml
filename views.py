def render_admin_registration_form(username: str, registered_farmers: list) -> str:
    """Renders the administrative dashboard with a space-saving drop-down filter."""
    
    # 1. Build drop-down option elements dynamically
    dropdown_options = "<option value=''>-- Search & Select a Registered Holding --</option>"
    for farmer in registered_farmers:
        dropdown_options += f'<option value="{farmer.land_id}">{farmer.land_id} - {farmer.farmer_name}</option>'

    # 2. Build hidden details display segments that toggle via JavaScript selection
    detail_cards_html = ""
    for farmer in registered_farmers:
        detail_cards_html += f"""
        <div id="card-{farmer.land_id}" class="farmer-detail-card" style="display: none;">
            <div class="holding-summary">
                <p><b>Land Record ID:</b> {farmer.land_id}</p>
                <p><b>Farmer Name:</b> {farmer.farmer_name}</p>
                <p><b>Contact Phone:</b> {farmer.phone_number}</p>
                <p><b>GPS Coordinates:</b> {farmer.latitude}, {farmer.longitude}</p>
            </div>
            
            <div class="metrics-subgrid">
                <div class="metric-mini-box">N: <b>{farmer.nitrogen} mg/kg</b></div>
                <div class="metric-mini-box">P: <b>{farmer.phosphorus} mg/kg</b></div>
                <div class="metric-mini-box">K: <b>{farmer.potassium} mg/kg</b></div>
                <div class="metric-mini-box" style="grid-column: span 3;">Soil pH Baseline: <b>{farmer.ph}</b></div>
            </div>
            
            <a href="/admin/download-card?id={farmer.land_id}" class="btn-download">🖨️ Download Printable Soil Card PDF</a>
        </div>
        """

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Agri Control Hub</title>
        <style>
            body {{ font-family: system-ui, -apple-system, sans-serif; background: #f8fafc; margin: 0; padding: 20px; color: #0f172a; }}
            .navbar {{ background: #1e3a8a; color: white; padding: 15px 25px; border-radius: 12px; display: flex; justify-content: space-between; align-items: center; margin-bottom: 25px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }}
            .navbar h2 {{ margin: 0; font-size: 18px; font-weight: 800; }}
            .session-badge {{ font-size: 12px; background: rgba(255,255,255,0.15); padding: 6px 12px; border-radius: 6px; font-weight: 600; }}
            .dashboard-layout {{ display: grid; grid-template-columns: 1.14fr 1.86fr; gap: 25px; max-width: 1250px; margin: 0 auto; }}
            @media (max-width: 900px) {{ .dashboard-layout {{ grid-template-columns: 1fr; }} }}
            .card {{ background: white; padding: 25px; border-radius: 16px; box-shadow: 0 4px 20px rgba(0,0,0,0.02); border: 1px solid #e2e8f0; height: fit-content; }}
            h3 {{ font-size: 16px; margin-top: 0; margin-bottom: 20px; color: #1e293b; border-bottom: 2px solid #f1f5f9; padding-bottom: 10px; text-transform: uppercase; letter-spacing: 0.5px; }}
            .form-group {{ margin-bottom: 14px; }}
            label {{ display: block; font-size: 11px; font-weight: 700; color: #475569; margin-bottom: 5px; text-transform: uppercase; }}
            input, select {{ width: 100%; padding: 11px; border: 1px solid #cbd5e1; border-radius: 8px; box-sizing: border-box; font-size: 14px; background: #f8fafc; transition: all 0.2s; }}
            input:focus, select:focus {{ outline: none; border-color: #2563eb; background: white; box-shadow: 0 0 0 3px rgba(37,99,235,0.1); }}
            .grid-2 {{ display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }}
            .btn-submit {{ width: 100%; background: #16a34a; color: white; border: none; padding: 12px; font-weight: 700; border-radius: 8px; cursor: pointer; font-size: 14px; transition: background 0.2s; }}
            .btn-submit:hover {{ background: #15803d; }}
            
            .farmer-detail-card {{ background: #f8fafc; border: 1px solid #e2e8f0; padding: 20px; border-radius: 12px; margin-top: 20px; animation: fadeIn 0.3s ease-in-out; }}
            .holding-summary {{ font-size: 14px; line-height: 1.6; color: #334155; margin-bottom: 15px; background: white; padding: 12px; border-radius: 8px; border-left: 4px solid #2563eb; }}
            .holding-summary p {{ margin: 4px 0; }}
            .metrics-subgrid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; margin-bottom: 20px; }}
            .metric-mini-box {{ background: white; border: 1px solid #e2e8f0; padding: 10px; text-align: center; font-size: 13px; border-radius: 6px; }}
            .btn-download {{ display: block; text-align: center; background: #2563eb; color: white; text-decoration: none; padding: 12px; border-radius: 8px; font-size: 14px; font-weight: 700; transition: background 0.2s; }}
            .btn-download:hover {{ background: #1d4ed8; }}
            .placeholder-text {{ text-align: center; color: #94a3b8; padding: 40px 20px; font-size: 14px; border: 2px dashed #e2e8f0; border-radius: 12px; }}
            
            @keyframes fadeIn {{ from {{ opacity: 0; transform: translateY(5px); }} to {{ opacity: 1; transform: translateY(0); }} }}
        </style>
        
        <script>
            function handleFarmerSelection() {{
                var selectBox = document.getElementById("farmerSelect");
                var selectedId = selectBox.value;
                
                var allCards = document.getElementsByClassName("farmer-detail-card");
                for (var i = 0; i < allCards.length; i++) {{
                    allCards[i].style.display = "none";
                }}
                
                var placeholder = document.getElementById("placeholderText");
                
                if (selectedId) {{
                    placeholder.style.display = "none";
                    document.getElementById("card-" + selectedId).style.display = "block";
                }} else {{
                    placeholder.style.display = "block";
                }}
            }}
        </script>
    </head>
    <body>
        <div class="navbar">
            <h2>🏛️ Agricultural Registry Platform</h2>
            <span class="session-badge">Admin Cluster: {username}</span>
        </div>
        
        <div class="dashboard-layout">
            <div class="card">
                <h3>👤 Register New Farmer</h3>
                <form action="/admin/register" method="POST">
                    <div class="form-group"><label>Unique Land ID</label><input type="text" name="land_id" placeholder="e.g., KA-12-105" required></div>
                    <div class="form-group"><label>Farmer Name</label><input type="text" name="farmer_name" placeholder="Full name" required></div>
                    <div class="form-group"><label>Phone Number</label><input type="text" name="phone_number" placeholder="Contact number" required></div>
                    <div class="grid-2">
                        <div class="form-group"><label>Nitrogen (N)</label><input type="number" name="n" min="0" max="300" required></div>
                        <div class="form-group"><label>Phosphorus (P)</label><input type="number" name="p" min="0" max="300" required></div>
                    </div>
                    <div class="grid-2">
                        <div class="form-group"><label>Potassium (K)</label><input type="number" name="k" min="0" max="300" required></div>
                        <div class="form-group"><label>Soil pH</label><input type="number" step="0.1" name="ph" min="3.0" max="10.0" required></div>
                    </div>
                    <div class="grid-2">
                        <div class="form-group"><label>Latitude</label><input type="number" step="0.0001" name="lat" required></div>
                        <div class="form-group"><label>Longitude</label><input type="number" step="0.0001" name="lon" required></div>
                    </div>
                    <button type="submit" class="btn-submit">💾 Save & Add Farmer</button>
                </form>
            </div>
            
            <div class="card">
                <h3>📋 Registry Search & Card Delivery</h3>
                <div class="form-group">
                    <label>Select Profile Target</label>
                    <select id="farmerSelect" onchange="handleFarmerSelection()">
                        {dropdown_options}
                    </select>
                </div>
                
                <div id="placeholderText" class="placeholder-text">
                    🔍 Select a Farmer or Land ID from the drop-down search menu above to review laboratory records and download their custom soil card file.
                </div>
                
                {detail_cards_html.replace('id="card-', 'id="card--')}
            </div>
        </div>
    </body>
    </html>
    """

def render_registration_success(farmer_name: str, land_id: str) -> str:
    return f"""
    <div style="font-family:system-ui; text-align:center; padding: 60px 20px;">
        <h2 style="color:#16a34a;">✅ Record Logged Successfully!</h2>
        <p>Farmer <b>{farmer_name}</b> (<b>{land_id}</b>) added to database repository records.</p><br/>
        <a href="/admin/register" style="background:#1e3a8a; color:white; padding:12px 24px; text-decoration:none; border-radius:8px; font-weight:bold;">← Back to Dashboard</a>
    </div>
    """

def render_inspector_dashboard(username: str, farm, temp, humidity, rainfall, crop, confidence, expected_yield, fertilizer) -> str:
    soil_alert = "✅ Normal Baseline" if 5.5 <= farm.ph <= 8.0 else "⚠️ Soil Anomaly Threat Detected"
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Inspector Hub</title>
        <style>
            body {{ font-family: system-ui, sans-serif; background: #f8fafc; padding: 12px; margin: 0; }}
            .card {{ background: white; max-width: 460px; margin: auto; padding: 20px; border-radius: 16px; box-shadow: 0 4px 20px rgba(0,0,0,0.06); }}
            .info-block {{ background: #f1f5f9; padding: 12px; border-radius: 8px; margin-bottom: 15px; border-left: 4px solid #2563eb; font-size: 14px; }}
            .grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; margin: 10px 0; }}
            .box {{ background: #f8fafc; padding: 8px; border-radius: 6px; text-align: center; font-size: 12px; border: 1px solid #e2e8f0; }}
            .box-bold {{ font-weight: 700; }}
            .recommend-card {{ background: #f0fdf4; border: 2px solid #16a34a; border-radius: 12px; padding: 15px; margin-top: 15px; }}
            .crop-title {{ font-size: 26px; font-weight: 800; color: #166534; text-align: center; margin: 5px 0; }}
        </style>
    </head>
    <body>
        <div class="card">
            <h3 style="text-align:center; margin-top:0;">🌾 FIELD INSPECTOR SYSTEM</h3>
            <div style="font-size:11px; text-align:center; color:#16a34a; background:#f0fdf4; padding:4px; margin-bottom:10px;">Inspector Active: {username}</div>
            
            <div class="info-block">
                <b>👤 Owner Details:</b><br/>
                ID: {farm.land_id} | Name: {farm.farmer_name}<br/>
                GPS: {farm.latitude}, {farm.longitude}
            </div>
            
            <div class="grid">
                <div class="box">N<br/><span class="box-bold">{farm.nitrogen}</span></div>
                <div class="box">P<br/><span class="box-bold">{farm.phosphorus}</span></div>
                <div class="box">K<br/><span class="box-bold">{farm.potassium}</span></div>
            </div>
            
            <div class="box" style="text-align:left; margin-bottom:15px; padding-left: 10px;">Soil pH: <b>{farm.ph}</b> ({soil_alert})</div>
            
            <div style="font-size:12px; font-weight:700; color:#64748b; text-transform: uppercase;">LIVE WEATHER CORE (API)</div>
            <div class="grid">
                <div class="box">Temp<br/><b>{temp}°C</b></div>
                <div class="box">Humidity<br/><b>{humidity}%</b></div>
                <div class="box">Rainfall<br/><b>{int(rainfall)}mm</b></div>
            </div>
            
            <div class="recommend-card">
                <div style="font-size:11px; text-align:center; color:#166534; font-weight:700; text-transform: uppercase;">RECOMMENDED MATCH</div>
                <div class="crop-title">{crop}</div>
                <div style="font-size:12px; text-align:center; margin-bottom:10px;">System Confidence: <b>{confidence}%</b></div>
                
                <div style="border-top:1px solid #bbf7d0; padding-top:8px; font-size:13px;">
                    Est. Yield Tonnage: <b>{expected_yield} Tons/Acre</b><br/><br/>
                    <b>🧪 Fertilizer Guidelines per Acre:</b>
                    <ul style="margin: 5px 0 0 0; padding-left: 20px;">
                        <li>Urea: {int(fertilizer['urea'])} kg</li>
                        <li>DAP: {int(fertilizer['dap'])} kg</li>
                        <li>MOP: {int(fertilizer['mop'])} kg</li>
                    </ul>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
