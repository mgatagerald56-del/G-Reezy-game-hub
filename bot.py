from flask import Flask, request, jsonify
import os, json, urllib.request
app = Flask(__name__)
GROQ_KEY = os.environ.get("GROQ_API_KEY", "")
MPESA_NUMBER = "0774311399"
PRODUCTS = """
- Xbox Controller - 120000 TZS - for playing games, holding in hands
- Xbox Headset - 85000 TZS - for hearing game sound, talking
- Charging Dock - 45000 TZS - for charging controllers
- Battery Pack - 30000 TZS - for power
- HDMI Cable - 25000 TZS - for connecting Xbox to TV
- Thumb Grips - 15000 TZS - small rubber for controller sticks
"""
HTML = """
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>G Reezy Game Hub</title>
<style>
body{background:#e8f5e9;font-family:Arial;margin:0;padding:15px}
.box{background:white;max-width:500px;margin:auto;border-radius:15px;padding:20px;border:3px solid #107C10}
h1{color:#107C10;text-align:center;margin:0}
.chat{background:#f1f8e9;border-radius:10px;padding:10px;min-height:200px;margin:15px 0}
.user{background:#107C10;color:white;padding:8px;border-radius:8px;margin:5px 0}
.bot{background:#e0e0e0;padding:8px;border-radius:8px;margin:5px 0}
input{width:100%;padding:12px;border:2px solid #107C10;border-radius:8px;box-sizing:border-box}
button.send{width:100%;padding:12px;background:#107C10;color:white;border:none;border-radius:8px;margin-top:10px;font-size:16px;font-weight:bold}
a.wa{display:none;width:100%;padding:12px;background:#25D366;color:white;border-radius:8px;margin-top:10px;font-size:16px;font-weight:bold;text-align:center;text-decoration:none;box-sizing:border-box}
a.share{display:block;width:100%;padding:12px;background:#25D366;color:white;border-radius:8px;margin-top:10px;font-size:16px;font-weight:bold;text-align:center;text-decoration:none;box-sizing:border-box}
</style>
</head>
<body>
<div class="box">
<h1>🎮 G Reezy Game Hub</h1>
<p style="text-align:center">Smart AI is LIVE - Talk like a human</p>
<div class="chat" id="chat"><div class="bot"><b>Bot:</b> Karibu! Niambie unataka nini, hata kwa Kiswahili.</div></div>
<input id="name" placeholder="Your Name e.g. Eric">
<input id="msg" placeholder="Type here..." style="margin-top:10px;">
<button class="send" type="button" onclick="sendMsg()">Send ➤</button>
<a class="wa" id="orderBtn" href="#" target="_blank">Send This Order to G Reezy on WhatsApp ✅</a>
<a class="share" id="shareBtn" href="#" target="_blank">Share hii link kwa WhatsApp 📱</a>
<small style="display:block;text-align:center;margin-top:10px">Pay via M-Pesa to 0774311399</small>
</div>
<script>
var lastOrder = "";
function sendMsg(){
  var n = document.getElementById('name').value || "Gamer";
  var m = document.getElementById('msg').value;
  if(!m){ alert("Type something first"); return; }
  var chat = document.getElementById('chat');
  chat.innerHTML += '<div class="user"><b>' + n + ':</b> ' + m + '</div>';
  document.getElementById('msg').value = "";
  chat.innerHTML += '<div class="bot" id="thinking">Bot is thinking...</div>';
  fetch('/chat', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({name:n, message:m})})
  .then(function(r){ return r.json(); })
  .then(function(d){
    var t = document.getElementById('thinking');
    if(t){ t.remove(); }
    chat.innerHTML += '<div class="bot"><b>Bot:</b> ' + d.reply + '</div>';
    chat.scrollTop = chat.scrollHeight;
    if(d.order){
      lastOrder = d.order;
      var text = "Hi G Reezy! I want to order:\n" + lastOrder + "\nMy Name: " + n + "\nMy Location: ";
      var btn = document.getElementById('orderBtn');
      btn.href = 'https://wa.me/255774311399?text=' + encodeURIComponent(text);
      btn.style.display = "block";
    }
  })
  .catch(function(e){
    var t2 = document.getElementById('thinking');
    if(t2){ t2.remove(); }
    chat.innerHTML += '<div class="bot">Error: ' + e + '</div>';
  });
}
document.getElementById('msg').addEventListener('keydown', function(e){ if(e.key === 'Enter'){ sendMsg(); } });
var link = window.location.href;
document.getElementById('shareBtn').href = 'https://wa.me/?text=' + encodeURIComponent('Check G Reezy Game Hub 🎮 ' + link);
</script>
</body>
</html>
"""
def ask_ai(user_msg, name):
    system = f"""You are G Reezy Game Hub assistant in Dar es Salaam, Tanzania. Speak Swahili + English mix like a local shop owner, friendly, short.
Products and prices:
{PRODUCTS}
Rules:
- Understand typos, Swahili, slang. "kitu cha kucheza" = controller, "sauti" = headset, "kuchaji" = charging dock.
- If user asks price, list prices.
- If user wants to order, calculate TOTAL.
- If user says "nina 200k" suggest what they can afford.
- Always end order with: Pay via M-Pesa to 0774311399 and tap WhatsApp button.
- Return ONLY JSON like: {{"reply": "your reply with <br> for lines", "order": "2 x controller = 240000 TZS\\nTOTAL: 240000 TZS" or "" if no order}}
User name: {name}
"""
    data = {"model": "llama-3.1-8b-instant", "messages": [{"role": "system", "content": system}, {"role": "user", "content": user_msg}], "temperature": 0.3}
    req = urllib.request.Request("https://api.groq.com/openai/v1/chat/completions", data=json.dumps(data).encode(), headers={"Authorization": f"Bearer {GROQ_KEY}", "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=20) as resp:
        out = json.loads(resp.read())
        txt = out["choices"][0]["message"]["content"]
        txt = txt.replace("```json","").replace("```","").strip()
        return json.loads(txt)
@app.route('/')
def home():
    return HTML
@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    name = data.get('name','Gamer')
    msg = data.get('message','')
    if not GROQ_KEY:
        return jsonify({"reply": "AI key missing! Owner: Add GROQ_API_KEY in Render Environment.", "order": ""})
    try:
        result = ask_ai(msg, name)
        return jsonify(result)
    except Exception as e:
        return jsonify({"reply": f"AI amechoka kidogo, jaribu tena. Error: {str(e)[:120]}", "order": ""})
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
