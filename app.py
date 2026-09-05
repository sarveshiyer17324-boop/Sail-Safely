import urllib.parse
from flask import Flask, jsonify, render_template_string, request
import requests

import sentry_sdk
from sentry_sdk import metrics

sentry_sdk.init(
    dsn="https://9e7f5833db5ebefa0678401777030d6a@o4512005455937536.ingest.us.sentry.io/4512012502827008",
    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for tracing.
    traces_sample_rate=1.0,
    send_default_pii=True,
    enable_logs=True
)



app = Flask(__name__)

@app.before_request
def set_sentry_user():
    # Captures IP address and incoming user details per request
    sentry_sdk.set_user({
        "ip_address": request.remote_addr,
        
        # If you add user authentication later, pass user details here:
        # "id": session.get("user_id"),
        # "email": session.get("user_email")
    })
# Dictionary for multi-language translations of status alerts and messages
TRANSLATIONS = {
    "en": {
        "safe": " SAFE TO SAIL",
        "caution": "! CAUTION ADVISED",
        "danger": "DANGER: DO NOT SAIL",
        "wave_rough": "Rough waves at {val}m",
        "wave_chop": "Moderate chop at {val}m",
        "wind_gale": "High winds at {val} km/h",
        "wind_breeze": "Moderate winds at {val} km/h",
        "speech_safe": "It is safe to sail at {name}. Wave height is {wave} meters and wind speed is {wind} km per hour.",
        "speech_caution": "Caution advised at {name}. {reasons}.",
        "speech_danger": "Danger! Do not sail at {name}. {reasons}."
    },
    "hi": {
        "safe": "नाव चलाना सुरक्षित है",
        "caution": "सावधान रहें",
        "danger": "खतराः नाव न चलाएं",
        "wave_rough": "{val} मीटर पर ऊंची लहरें",
        "wave_chop": "{val} मीटर पर मध्यम लहरें",
        "wind_gale": "{val} किमी/घंटा तेज हवाएं",
        "wind_breeze": "{val} किमी/घंटा मध्यम हवाएं",
        "speech_safe": "{name} में नाव चलाना सुरक्षित है। लहरों की ऊंचाई {wave} मीटर और हवा की गति {wind} किलोमीटर प्रति घंटा है।",
        "speech_caution": "{name} में सावधानी बरतें। {reasons}",
        "speech_danger": "खतरा! {name} में समुद्र में न जाएं। {reasons}।"
    },
    "mr": {
        "safe": "नौकायन सुरक्षित आहे",
        "caution": "! काळजी घ्या",
        "danger": "धोकाः समुद्रात जाऊ नका",
        "wave_rough": "{val} मीटरवर उंच लाटा",
        "wave_chop": "{val} मीटरवर मध्यम लाटा",
        "wind_gale": "{val} किमी/तास वेगाने वाहणारे वादळी वारे",
        "wind_breeze": "{val} किमी/तास वेगाने वाहणारे मध्यम वारे",
        "speech_safe": "{name} येथे नौकायन सुरक्षित आहे. लाटांची उंची {wave} मीटर आणि वाऱ्याचा वेग {wind} किमी प्रतितास आहे.",
        "speech_caution": "{name} येथे काळजी घ्या. {reasons}.",
        "speech_danger": "धोका! {name} येथे समुद्रात जाऊ नका. {reasons}."
    },
    "ta": {
        "safe": "கடலுக்கு செல்ல பாதுகாப்பானது",
        "caution": "எச்சரிக்கை தேவை",
        "danger": "ஆபத்து: கடலுக்குச் செல்ல வேண்டாம்",
        "wave_rough": "{val} மீட்டரில் கடுமையான அலைகள்",
        "wave_chop": "{val} மீட்டரில் மிதமான அலைகள்",
        "wind_gale": "மணிக்கு {val} கி.மீ வேகத்தில் பலத்த காற்று",
        "wind_breeze": "மணிக்கு {val} கி.மீ வேகத்தில் மிதமான காற்று",
        "speech_safe": "{name}-ல் கடலுக்குச் செல்வது பாதுகாப்பானது. அலை உயரம் {wave} மீட்டர், காற்றின் வேகம் மணிக்கு {wind} கி.மீ.",
        "speech_caution": "{name}-ல் எச்சரிக்கை தேவை. {reasons}.",
        "speech_danger": "ஆபத்து! {name}-ல் கடலுக்குச் செல்ல வேண்டாம். {reasons}."
    },
    "ml": {
        "safe": "കടലിൽ പോകുന്നത് സുരക്ഷിതമാണ്",
        "caution": "! ജാഗ്രത പാലിക്കുക",
        "danger": "അപകദം: കടലിൽ പോകരുത്",
        "wave_rough": "{val} മീറ്ററിൽ ശക്തമായ തിരമാലകൾ",
        "wave_chop": "{val} മീറ്ററിൽ ഇടത്തരം തിരമാലകൾ",
        "wind_gale": "മണിക്കൂറിൽ {val} കി.മീ വേഗതയുള്ള ശക്തമായ കാറ്റ്",
        "wind_breeze": "മണിക്കൂറിൽ {val} കി.മീ വേഗതയുള്ള ഇടത്തരം കാറ്റ്",
        "speech_safe": "{name}-ൽ കടലിൽ പോകുന്നത് സുരക്ഷിതമാണ്. തിരമാലയുടെ ഉയരം {wave} മീറ്ററും കാറ്റിൻ്റെ വേഗത മണിക്കൂറിൽ {wind} കിലോമീറ്ററുമാണ്.",
        "speech_caution": "{name}-ൽ ജാഗ്രത പാലിക്കുക. {reasons}.",
        "speech_danger": "അപകടം! {name}-ൽ കടലിൽ പോകരുത്. {reasons}."
    },
    "gu": {
        "safe": "દરિયામાં જવું સુરક્ષિત છે",
        "caution": "! સાવચેતી રાખો",
        "danger": "ભય: દરિયામાં જશો નહીં",
        "wave_rough": "{val} મીટર પર ઊંચા મોજા",
        "wave_chop": "{val} મીટર પર મધ્યમ મોજા",
        "wind_gale": "{val} કિમી/કલાકની ઝડપે ભારે પવન",
        "wind_breeze": "{val} કિમી/કલાકની ઝડપે મધ્યમ પવન",
        "speech_safe": "{name} ખાતે દરિયામાં જવું સુરક્ષિત છે. મોજાની ઊંચાઈ {wave} મીટર અને પવનની ઝડપ {wind} કિમી પ્રતિ કલાક છે.",
        "speech_caution": "{name} ખાતે સાવચેતી રાખો. {reasons}.",
        "speech_danger": "ભય! {name} ખાતે દરિયામાં જશો નહીં. {reasons}."
    }
}

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
<title>Sagar Saathi | सागर साथी - Marine Safety</title>
<style>
body { font-family: Arial, sans-serif; text-align: center; padding: 20px; background-color: #f0f4f8; }
.app-container { background: white; padding: 25px; border-radius: 12px; display: inline-block; box-shadow: 0 4px 15px rgba(0,0,0,0.1); width: 400px; }
.lang-select { margin-bottom: 15px; padding: 8px; font-size: 14px; border-radius: 6px; border: 1px solid #0076d6; background: #eef7ff; font-weight: bold; width: 100%; }
.geo-btn { background: #28a745; color: white; border: none; padding: 12px 15px; border-radius: 6px; cursor: pointer; font-size: 15px; width: 100%; margin-top: 15px; font-weight: bold; }
.geo-btn:hover { background: #218838; }
.sos-btn { background: #dc3545; color: white; border: none; padding: 12px 15px; border-radius: 6px; cursor: pointer; font-size: 16px; width: 100%; margin-top: 10px; font-weight: bold; }
.sos-btn:hover { background: #c82333; }
input { padding: 10px; width: 55%; border: 1px solid #ccc; border-radius: 4px; font-size: 16px; margin-right: 5px; }
.submit-btn { padding: 10px 15px; background: #0076d6; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 16px; }
.submit-btn:hover { background: #0056b3; }
.status-box { margin-top: 20px; padding: 15px; border-radius: 6px; font-weight: bold; font-size: 18px; white-space: pre-line; }
.safe { background-color: #d4edda; color: #155724; }
.caution { background-color: #fff3cd; color: #856404; }
.danger { background-color: #f8d7da; color: #721c24; }
.data-display { text-align: left; margin-top: 15px; font-size: 15px; line-height: 1.6; }
.sub-title { color: #555; font-size: 14px; margin-top: -10px; margin-bottom: 15px; }
</style>
</head>
<body>
<div class="app-container">
<h1 style="margin-bottom: 5px;">Sagar Saathi</h1>
<div class="sub-title">सागर साथी Marine & Wind Safety App</div>
<select id="lang-picker" class="lang-select">
<option value="en">English</option>
<option value="hi">हिंदी (Hindi)</option>
<option value="mr">मराठी (Marathi)</option>
<option value="ta">தமிழ் (Tamil)</option>
<option value="ml">മലയാളം (Malayalam)</option>
<option value="gu">ગુજરાતી (Gujarati)</option>
</select>
<form id="search-form">
<input type="text" id="city-input" placeholder="e.g., Mumbai, Kochi">
<button type="submit" class="submit-btn">Check</button>
</form>
<button id="gps-btn" class="geo-btn" type="button">Use My Location</button>
<button id="sos-btn" class="sos-btn" type="button">🚨 EMERGENCY SOS</button>

<div id="safety-status" class="status-box" style="display: none;"></div>
<div id="marine-data" class="data-display"></div>
</div>
<script>
document.addEventListener("DOMContentLoaded", () => {
    const gpsBtn = document.getElementById('gps-btn');
    const sosBtn = document.getElementById('sos-btn');
    const searchForm = document.getElementById('search-form');

    sosBtn.addEventListener('click', () => {
        alert("EMERGENCY: Fisher Helpline Number: 040-23895000");
        window.location.href = "tel:04023895000";
    });

    gpsBtn.addEventListener('click', () => {
        if (!navigator.geolocation) return alert("GPS is not supported by your browser.");
        document.getElementById('marine-data').innerHTML = "Detecting location...";
        const lang = document.getElementById('lang-picker').value;
        navigator.geolocation.getCurrentPosition(
            (pos) => fetchMarineSafety(`/get_marine_safety?lat=${pos.coords.latitude}&lon=${pos.coords.longitude}&lang=${lang}`),
            (err) => alert("GPS Error: Please enable location permissions in your browser.")
        );
    });

    searchForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const city = document.getElementById('city-input').value.trim();
        const lang = document.getElementById('lang-picker').value;
        if (city) fetchMarineSafety(`/get_marine_safety?city=${encodeURIComponent(city)}&lang=${lang}`);
    });
});

function speakResult(text, langCode) {
    if ('speechSynthesis' in window) {
        window.speechSynthesis.cancel();
        const utterance = new SpeechSynthesisUtterance(text);
        const langMap = {
            'en': 'en-IN',
            'hi': 'hi-IN',
            'mr': 'mr-IN',
            'ta': 'ta-IN',
            'ml': 'ml-IN',
            'gu': 'gu-IN'
        };
        utterance.lang = langMap[langCode] || 'en-IN';
        window.speechSynthesis.speak(utterance);
    }
}

function fetchMarineSafety(url) {
    const dataDisplay = document.getElementById('marine-data');
    const safetyStatus = document.getElementById('safety-status');
    const currentLang = document.getElementById('lang-picker').value;
    dataDisplay.innerHTML = "Fetching weather & wave telemetry...";
    safetyStatus.style.display = "none";
    
    fetch(url)
    .then(res => res.json())
    .then(data => {
        if (data.error) {
            dataDisplay.innerHTML = "❌ " + data.error;
            speakResult(data.error, currentLang);
            return;
        }
        safetyStatus.style.display = "block";
        safetyStatus.className = "status-box " + data.status_level;
        if (data.reasons.length > 0) {
            safetyStatus.innerText = data.status_title + "\\n(" + data.reasons.join(" & ") + ")";
        } else {
            safetyStatus.innerText = data.status_title;
        }
        dataDisplay.innerHTML = `
        <h3>Conditions for ${data.name}:</h3>
        <ul>
        <li><strong>Coordinates:</strong> ${data.lat}°, ${data.lon}°</li>
        <li><strong>Wave Height:</strong> ${data.wave_height} meters</li>
        <li><strong>Wind Speed:</strong> ${data.wind_speed} km/h (${data.wind_direction}°)</li>
        </ul>`;
        speakResult(data.speech_text, currentLang);
    })
    .catch(() => {
        dataDisplay.innerHTML = "❌ Server connection dropped.";
    });
}
</script>
</body>
</html>
"""
from flask import render_template
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/get_marine_safety")
def get_marine_safety():
    metrics.count("marine_safety.request.count", 1)
    city = request.args.get("city")
    lat_param = request.args.get("lat")
    lon_param = request.args.get("lon")
    lang = request.args.get("lang", "en")

    if lang not in TRANSLATIONS:
        lang = "en"
    t = TRANSLATIONS[lang]

    lat, lon, name = None, None, "Your Location"
    if lat_param and lon_param:
        try:
            lat, lon = float(lat_param), float(lon_param)
        except ValueError:
            return jsonify({"error": "Invalid coordinates provided."}), 400
    elif city:
        try:
            geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={urllib.parse.quote(city.strip())}&count=1&language=en&format=json"
            geo_res = requests.get(geo_url, timeout=5)
            geo_res.raise_for_status()
            data = geo_res.json()
            if not data.get("results"):
                return jsonify({"error": "Location not found."})
            top = data["results"][0]
            lat, lon, name = top["latitude"], top["longitude"], top["name"]
        except Exception:
            return jsonify({"error": "Geocoding service unavailable."}), 502
    else:
        return jsonify({"error": "No location specified."}), 400

    try:
        headers = {"User-Agent": "SagarSaathi/1.0"}
         marine_url = f"https://marine-api.open-meteo.com/v1/marine?latitude={lat}&longitude={lon}&current=wave_height&cell_selection=sea"
        marine_res = requests.get(marine_url, timeout=10)
        marine_res.raise_for_status()
        wave_height = marine_res.json().get("current", {}).get("wave_height")
        if wave_height is None:
            fallback_url = f"https://marine-api.open-meteo.com/v1/marine?latitude={lat}&longitude={lon}&current=wave_height"
            fallback_res = requests.get(fallback_url, headers=headers, timeout=10)
            if fallback_res.status_code == 200:
                wave_height = fallback_res.json().get("current", {}).get("wave_height")

        weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=wind_speed_10m,wind_direction_10m"
        weather_res = requests.get(weather_url, timeout=10)
        weather_res.raise_for_status()
        weather_data = weather_res.json().get("current", {})
        wind_speed = weather_data.get("wind_speed_10m")
        wind_direction = weather_data.get("wind_direction_10m")

        if wave_height is None:
            return jsonify({"error": f"No marine telemetry available for {name}. Ensure target location is on a coastal region."})

        status_level = "safe"
        reasons = []

        if wave_height > 2.0:
            status_level = "danger"
            reasons.append(t["wave_rough"].format(val=round(wave_height, 1)))
        elif wave_height >= 1.2:
            status_level = "caution"
            reasons.append(t["wave_chop"].format(val=round(wave_height, 1)))

        if wind_speed > 35.0:
            status_level = "danger"
            reasons.append(t["wind_gale"].format(val=round(wind_speed, 1)))
        elif wind_speed >= 22.0 and status_level != "danger":
            status_level = "caution"
            reasons.append(t["wind_breeze"].format(val=round(wind_speed, 1)))

        status_title = t[status_level]
        reasons_text = " & ".join(reasons)
       #  metrics.count("marine_safety.status", 1, tags={"level": status_level})

        if status_level == "safe":
            speech_text = t["speech_safe"].format(name=name, wave=round(wave_height, 1), wind=round(wind_speed, 1))
        elif status_level == "caution":
            speech_text = t["speech_caution"].format(name=name, reasons=reasons_text)
        else:
            speech_text = t["speech_danger"].format(name=name, reasons=reasons_text)
          #   metrics.distribution("marine_safety.wave_height_meters", wave_height)
          #   metrics.distribution("marine_safety.wind_speed_kmh", wind_speed)

        return jsonify({
            "name": name,
            "lat": round(lat, 4),
            "lon": round(lon, 4),
            "wave_height": round(wave_height, 2),
            "wind_speed": round(wind_speed, 1),
            "wind_direction": wind_direction,
            "status_level": status_level,
            "status_title": status_title,
            "reasons": reasons,
            "speech_text": speech_text
        })
    except Exception:
        return jsonify({"error": "Failed to fetch marine conditions."}), 502

if __name__ == "__main__":
    app.run(debug=True, port=5000)
