from flask import Flask, request, jsonify
import os, json, urllib.request
app = Flask(__name__)
GROQ_KEY = os.environ.get("GROQ_API_KEY", "")

PRODUCTS = """
- Xbox Controller - 120000 TZS
- Xbox Headset - 85000 TZS
- Charging Dock - 45000 TZS
- Battery Pack - 30000 TZS
- HDMI Cable - 25000 TZS
- Thumb Grips - 15000 TZS
"""

HTML = """
<!DOCTYPE html>
<html>
<head><meta name="viewport" content="width=device-width, initial-scale=1"><title>G Reezy Game Hub</title></head>
<body style="font-family:Arial;padding:15px;background:#e8f5e9">
<div style="background:white;max-width:500px;margin:auto;border-radius:15px;padding:20px;border:3px solid #107C10">
<h1 style="color:#107C10;text-align:center">🎮 G Reezy Game Hub</h1>
<div id="chat" style="background:#f1f8e9;padding:10px;min-height:200px;margin:15px 0"><div><b>Bot:</b> Karibu! Niambie unataka nini, hata kwa Kiswahili.</div></div>
<input id="name" placeholder="Your Name e.g. Eric" style="width:100%;padding:12px;box-sizing:border-box">
<input id="msg" placeholder="Type here..." style="width:100%;padding:12px;margin-top:10px;box-sizing:border-box">
<button type="button" onclick="sendMsg()" style="width:100%;padding:12px;background:#107C10;color:white;margin-top:10px;font-size:16px;font-weight:bold">Send ➤</button>
<a id="orderBtn" href="#" target="_blank" style="display:none;width:100%;padding:12px;background:#25D366;color:white;border-radius:8px;margin-top:10px;font-size:16px;font-weight:bold;text-align:center;text-decoration:none;box-sizing:border-box">Send This Order to G Reezy on WhatsApp ✅</a>
<a id="shareBtn" href="#" target="_blank" style="display:block;width:100%;padding:12px;background:#25D366;color:white;border-radius:8px;margin-top:10px;font-size:16px;font-weight:bold;text-align:center;text-decoration:none;box-sizing:border-box">Share hii link kwa WhatsApp 📱</a>
<small style="display:block;text-align:center;margin-top:10px">Pay via M-Pesa to 0774311399</small>
</div>
<script>
function sendMsg(){
  var n = document.getElementById('name').value || "Gamer";
  var m = document.getElementById('msg').value;
  if(!m){ return; }
  var chat = document.getElementById('chat');
  chat.innerHTML += '<div style="background:#107C10;color:white;padding:8px;border-radius:8px;margin:5px 0"><b>' + n + ':</b> ' + m + '</div>';
  document.getElementById('msg').value = "";
  chat.innerHTML += '<div id="thinking">Bot is thinking...</div>';
  fetch('/chat', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({name:n, message:m})})
  .then(function(r){ return r.json(); })
  .then(function(d){
    var t = document.getElementById('thinking'); if(t){ t.remove(); }
    chat.innerHTML += '<div style="background:#e0e0e0;padding:8px;border-radius:8px;margin:5px 0"><b>Bot:</b> ' + d.reply + '</div>';
    if(d.order){
      var text = "Hi G Reezy! I want to order:\\n" + d.order + "\\nMy Name: " + n;
      var btn = document.getElementById('orderBtn');
      btn.href = 'https://wa.me/255774311399?text=' + encodeURIComponent(text);
      btn.style.display = "block";
    }
  })
  .catch(function(e){ var t2 = document.getElementById('thinking'); if(t2){ t2.remove(); } chat.innerHTML += '<div>Error: ' + e + '</div>'; });
}
document.getElementById('shareBtn').href = 'https://wa.me/?text=' + encodeURIComponent('Check G Reezy Game Hub 🎮 ' + window.location.href);
</script>
</body>
</html>
"""
def ask_ai(user_msg, name):
    system = f"""You are G Reezy Game Hub assistant in Dar es Salaam. Speak Swahili + English mix, friendly, short.
Products:
{PRODUCTS}
Rules: Understand typos, Swahili, slang. "kitu cha kucheza"=controller. If user wants to order, calculate TOTAL. Return ONLY JSON: {{"reply": "your reply", "order": "2 x controller = 240000 TZS TOTAL: 240000 TZS" or ""}}"""
    data = {"model": "llama-3.1-8b-instant", "messages": [{"role": "system", "content": system}, {"role": "user", "content": user_msg}], "temperature": 0.3}
    req = urllib.request.Request("https://api.groq.com/openai/v1/chat/completions", data=json.dumps(data).encode(), headers={"Authorization": f"Bearer {GROQ_KEY}", "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=20) as resp:
        out = json.loads(resp.read())
        txt = out["choices"][0]["message"]["content"].replace("```json","").replace("```","").strip()
        return json.loads(txt)
@app.route('/')
def home():
    return HTML
@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    msg = data.get('message','')
    name = data.get('name','Gamer')
    if not GROQ_KEY:
        return jsonify({"reply": "AI key missing! Owner must add GROQ_API_KEY in Render Environment.", "order": ""})
    try:
        return jsonify(ask_ai(msg, name))
    except Exception as e:
        return jsonify({"reply": "AI error: " + str(e)[:150] + ". Try again.", "order": ""})
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
