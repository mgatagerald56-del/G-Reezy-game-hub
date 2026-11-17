from flask import Flask, request, jsonify
import os
app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html>
<head><meta name="viewport" content="width=device-width, initial-scale=1"><title>Test</title></head>
<body style="font-family:Arial;padding:20px">
<h2>TEST BUTTON</h2>
<div id="chat" style="background:#eee;padding:10px;min-height:100px"></div>
<input id="msg" placeholder="Type here" style="width:100%;padding:12px;margin-top:10px">
<button type="button" onclick="sendMsg()" style="width:100%;padding:12px;background:green;color:white;margin-top:10px">Send ➤</button>
<script>
function sendMsg(){
  alert("BUTTON CLICKED - JS IS WORKING");
  var m = document.getElementById('msg').value;
  var chat = document.getElementById('chat');
  chat.innerHTML += '<div>You said: ' + m + '</div>';
  document.getElementById('msg').value = "";
  fetch('/chat', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({message:m})})
  .then(function(r){ return r.json(); })
  .then(function(d){ chat.innerHTML += '<div>Bot: ' + d.reply + '</div>'; })
  .catch(function(e){ chat.innerHTML += '<div>FETCH ERROR: ' + e + '</div>'; });
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
    msg = data.get('message','')
    return jsonify({"reply": "I got your message: " + msg})
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
