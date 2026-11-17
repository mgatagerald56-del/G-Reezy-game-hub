from flask import Flask, request, jsonify
import os

app = Flask(__name__)

# --- SHOP SETTINGS - YOU CAN CHANGE THESE ---
SHOP_NAME = "G Reezy Game Hub"
MPESA_NUMBER = "0774311399"
# --- PRICES ---
PRICES = {
    "controller": 120000,
    "headset": 85000,
    "charging dock": 45000,
    "battery pack": 30000,
    "hdmi cable": 25000,
    "thumb grips": 15000,
}

HTML = """
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>G Reezy Game Hub</title>
<style>
body { background:#e8f5e9; font-family: Arial; margin:0; padding:15px; }
.box { background:white; max-width:500px; margin:auto; border-radius:15px; padding:20px; border:3px solid #107C10; }
h1 { color:#107C10; text-align:center; margin:0; }
p.sub { text-align:center; color:#333; }
.chat { background:#f1f8e9; border-radius:10px; padding:10px; min-height:200px; margin:15px 0; }
.user { background:#107C10; color:white; padding:8px; border-radius:8px; margin:5px 0; }
.bot { background:#e0e0e0; padding:8px; border-radius:8px; margin:5px 0; }
input { width:100%; padding:12px; border:2px solid #107C10; border-radius:8px; box-sizing:border-box; }
button.send { width:100%; padding:12px; background:#107C10; color:white; border:none; border-radius:8px; margin-top:10px; font-size:16px; font-weight:bold; }
button.wa { width:100%; padding:12px; background:#25D366; color:white; border:none; border-radius:8px; margin-top:10px; font-size:16px; font-weight:bold; }
small { display:block; text-align:center; margin-top:10px; color:#555; }
</style>
</head>
<body>
<div class="box">
<h1>🎮 G Reezy Game Hub</h1>
<p class="sub">Xbox AI is LIVE - Type quit to stop</p>
<div class="chat" id="chat">
<div class="bot"><b>Bot:</b> Karibu G Reezy Game Hub! Type <b>price</b> to see Xbox accessories.</div>
</div>
<input id="name" placeholder="Your Name e.g. Reezy">
<input id="msg" placeholder="Type here... price / 2 controller / quit" style="margin-top:10px;">
<button class="send" onclick="send()">Send ➤</button>
<button class="wa" onclick="share()">Share hii link kwa WhatsApp 📱</button>
<small>Pay via M-Pesa to 0774311399</small>
</div>
<script>
let name = "";
function send(){
  let n = document.getElementById('name').value || "Gamer";
  let m = document.getElementById('msg').value;
  if(!m) return;
  name = n;
  let chat = document.getElementById('chat');
  chat.innerHTML += `<div class="user"><b>${n}:</b> ${m}</div>`;
  document.getElementById('msg').value = "";
  fetch('/chat', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({name:n, message:m})})
  .then(r=>r.json()).then(d=>{
    chat.innerHTML += `<div class="bot"><b>Bot:</b> ${d.reply}</div>`;
    chat.scrollTop = chat.scrollHeight;
  });
}
function share(){
  let link = window.location.href;
  window.open('https://wa.me/?text=' + encodeURIComponent('Check G Reezy Game Hub 🎮 ' + link));
}
</script>
</body>
</html>
"""

@app.route('/')
def home():
    return HTML

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    name = data.get('name','Gamer')
    msg = data.get('message','').lower().strip()

    if 'price' in msg or 'bei' in msg:
        text = " - ".join([f"{k}: {v} TZS" for k,v in PRICES.items()])
        return jsonify({"reply": text.replace(" - ", "<br>- ")})

    if 'quit' in msg or 'exit' in msg or 'stop' in msg:
        return jsonify({"reply": f"Asante {name}! Karibu tena G Reezy Game Hub! 🎮"})

    # Try to find order like "2 controller"
    for item, price in PRICES.items():
        if item in msg:
            qty = 1
            for word in msg.split():
                if word.isdigit():
                    qty = int(word)
                    break
            total = qty * price
            return jsonify({"reply": f"Sawa {name}, umechagua: {qty} x {item}<br>TOTAL: {total} TZS. Pay via M-Pesa to {MPESA_NUMBER}"})

    return jsonify({"reply": f"Karibu {name}! Type <b>price</b> for Xbox accessories, or e.g. <b>2 controller</b> to order."})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)