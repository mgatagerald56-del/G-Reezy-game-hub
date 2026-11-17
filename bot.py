from flask import Flask, request, jsonify
import os, json, urllib.request
app = Flask(__name__)
GROQ_KEY = os.environ.get("GROQ_API_KEY", "").strip()
ADMIN_PASSWORD = "greezy123"  # Change this for each business you sell to!

# Products are loaded from file, not from code
def load_products():
    if os.path.exists("products.json"):
        with open("products.json") as f:
            return json.load(f)
    # Default starter products
    return [
        {"id":"1","name":"Xbox Controller","price":120000,"cat":"Controllers","emoji":"🎮","desc":"For playing"},
        {"id":"2","name":"Xbox Headset","price":85000,"cat":"Audio","emoji":"🎧","desc":"Hear + talk"},
        {"id":"3","name":"Charging Dock","price":45000,"cat":"Power","emoji":"🔋","desc":"Charge 2"},
        {"id":"4","name":"Battery Pack","price":30000,"cat":"Power","emoji":"🔋","desc":"Extra power"},
        {"id":"5","name":"HDMI Cable","price":25000,"cat":"Cables","emoji":"🔌","desc":"Xbox to TV"},
        {"id":"6","name":"Thumb Grips","price":15000,"cat":"Controllers","emoji":"👍","desc":"For sticks"},
    ]
def save_products(p):
    with open("products.json","w") as f:
        json.dump(p,f)

HTML = """
<!DOCTYPE html>
<html><head><meta name="viewport" content="width=device-width, initial-scale=1"><title>G Reezy Game Hub</title></head>
<body style="font-family:Arial;padding:15px;background:#e8f5e9;margin:0">
<div style="background:white;max-width:520px;margin:auto;border-radius:15px;padding:15px;border:3px solid #107C10">
<h1 style="color:#107C10;text-align:center">🎮 G Reezy Game Hub</h1>
<input id="search" placeholder="🔍 Search 1000+ products... e.g. controller, headset" oninput="renderShop()" style="width:100%;padding:14px;box-sizing:border-box;border:2px solid #107C10;border-radius:10px;font-size:16px">
<div id="cats" style="margin:10px 0;display:flex;gap:5px;flex-wrap:wrap"></div>
<div id="count" style="color:#666;font-size:13px"></div>
<div id="shop"></div>
<div style="display:flex;justify-content:space-between;margin:10px 0">
<button onclick="prevPage()" style="padding:10px 20px;border-radius:8px;border:1px solid #ccc;background:white">← Prev</button>
<span id="pageInfo" style="padding:10px"></span>
<button onclick="nextPage()" style="padding:10px 20px;border-radius:8px;border:1px solid #ccc;background:white">Next →</button>
</div>
<div style="background:#f1f8e9;border-radius:10px;padding:12px">
<h3 style="margin:0">🛒 Cart</h3>
<div id="cart">Empty</div><div id="total" style="font-weight:bold;font-size:18px;margin-top:8px"></div>
<input id="name" placeholder="Your Name" style="width:100%;padding:12px;box-sizing:border-box;margin-top:10px;border:2px solid #107C10;border-radius:8px">
<input id="location" placeholder="Location e.g. Mikocheni" style="width:100%;padding:12px;box-sizing:border-box;margin-top:10px;border:2px solid #107C10;border-radius:8px">
<a id="orderBtn" href="#" target="_blank" style="display:none;width:100%;padding:14px;background:#25D366;color:white;border-radius:8px;margin-top:10px;font-weight:bold;text-align:center;text-decoration:none;box-sizing:border-box">Send Order on WhatsApp ✅</a>
<small style="display:block;text-align:center;margin-top:8px">Pay via M-Pesa to 0774311399</small>
</div>
<h3 style="text-align:center">💬 Ask AI</h3>
<div id="chat" style="background:#f1f8e9;padding:10px;min-height:80px;border-radius:10px"><div><b>Bot:</b> Uliza chochote</div></div>
<input id="msg" placeholder="Type question..." style="width:100%;padding:12px;margin-top:10px;box-sizing:border-box;border:2px solid #107C10;border-radius:8px">
<button type="button" onclick="sendMsg()" style="width:100%;padding:12px;background:#107C10;color:white;margin-top:10px;font-weight:bold;border:none;border-radius:8px">Ask AI ➤</button>
<a href="/admin" style="display:block;text-align:center;margin-top:15px;color:#888;font-size:12px">Owner? Manage Products →</a>
</div>
<script>
var PRODUCTS = [];
var cart = {}; var currentCat='All'; var page=1; var PER_PAGE=12;
fetch('/api/products').then(r=>r.json()).then(d=>{PRODUCTS=d; renderShop();});
function renderShop(){
  var q = document.getElementById('search').value.toLowerCase();
  var cats = ['All', ...new Set(PRODUCTS.map(p=>p.cat))];
  document.getElementById('cats').innerHTML = cats.map(c=>'<button onclick="setCat(\\''+c+'\\')" style="padding:8px 14px;border-radius:20px;border:1px solid #107C10;background:'+(currentCat===c?'#107C10;color:white':'white')+'">'+c+'</button>').join('');
  var filtered = PRODUCTS.filter(p=> (currentCat==='All'||p.cat===currentCat) && (p.name.toLowerCase().includes(q) || p.cat.toLowerCase().includes(q) || (p.desc||'').toLowerCase().includes(q)) );
  document.getElementById('count').innerHTML = filtered.length + ' products found';
  var totalPages = Math.max(1, Math.ceil(filtered.length/PER_PAGE));
  if(page>totalPages) page=totalPages;
  var start=(page-1)*PER_PAGE; var show=filtered.slice(start, start+PER_PAGE);
  var html='';
  show.forEach(function(p){
    var qty=cart[p.id]||0;
    html+='<div style="display:flex;justify-content:space-between;align-items:center;border:1px solid #ddd;border-radius:10px;padding:10px;margin:8px 0"><div><div style="font-size:28px">'+(p.emoji||'📦')+'</div><b>'+p.name+'</b><br><small>'+(p.desc||'')+' • '+p.cat+'</small><br><b style="color:#107C10">'+p.price.toLocaleString()+' TZS</b></div>';
    if(qty===0){ html+='<button onclick="addItem(\\''+p.id+'\\')" style="background:#107C10;color:white;border:none;padding:10px 15px;border-radius:20px;font-weight:bold">+ Add</button>'; }
    else { html+='<div><button onclick="changeQty(\\''+p.id+'\\',-1)" style="padding:8px 12px;border-radius:50%;border:1px solid #ccc;background:white">-</button> <b>'+qty+'</b> <button onclick="changeQty(\\''+p.id+'\\',1)" style="padding:8px 12px;border-radius:50%;border:1px solid #ccc;background:white">+</button></div>'; }
    html+='</div>';
  });
  if(show.length===0) html='<p style="text-align:center;color:#888">No product found. Try another word.</p>';
  document.getElementById('shop').innerHTML=html;
  document.getElementById('pageInfo').innerHTML='Page '+page+' / '+totalPages;
  renderCart();
}
function setCat(c){ currentCat=c; page=1; renderShop(); }
function nextPage(){ page++; renderShop(); }
function prevPage(){ if(page>1) page--; renderShop(); }
function addItem(id){ cart[id]=1; renderShop(); }
function changeQty(id,d){ cart[id]=(cart[id]||0)+d; if(cart[id]<=0) delete cart[id]; renderShop(); }
function renderCart(){
  var lines=[]; var total=0;
  PRODUCTS.forEach(function(p){ if(cart[p.id]){ var t=p.price*cart[p.id]; total+=t; lines.push(cart[p.id]+' x '+p.name+' = '+t.toLocaleString()+' TZS'); } });
  if(lines.length===0){ document.getElementById('cart').innerHTML='Empty'; document.getElementById('total').innerHTML=''; document.getElementById('orderBtn').style.display='none'; return; }
  document.getElementById('cart').innerHTML=lines.join('<br>');
  document.getElementById('total').innerHTML='TOTAL: '+total.toLocaleString()+' TZS';
  var n=document.getElementById('name').value||''; var loc=document.getElementById('location').value||'';
  var text="Hi G Reezy! Order:\\n"+lines.join("\\n")+"\\nTOTAL: "+total+" TZS\\nName: "+n+"\\nLocation: "+loc;
  var btn=document.getElementById('orderBtn'); btn.href='https://wa.me/255774311399?text='+encodeURIComponent(text); btn.style.display='block';
}
document.getElementById('name').addEventListener('input', renderCart);
document.getElementById('location').addEventListener('input', renderCart);
function sendMsg(){
  var m=document.getElementById('msg').value; if(!m) return;
  var chat=document.getElementById('chat'); chat.innerHTML+='<div style="background:#107C10;color:white;padding:8px;border-radius:8px;margin:5px 0"><b>You:</b> '+m+'</div>'; document.getElementById('msg').value=''; chat.innerHTML+='<div id="thinking">Thinking...</div>';
  fetch('/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:m})}).then(r=>r.json()).then(d=>{var t=document.getElementById('thinking'); if(t)t.remove(); chat.innerHTML+='<div style="background:#e0e0e0;padding:8px;border-radius:8px;margin:5px 0"><b>Bot:</b> '+d.reply+'</div>'; if(d.add){ addItem(d.add); }});
}
</script></body></html>
"""
ADMIN_HTML = """
<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width, initial-scale=1"><title>Admin</title></head>
<body style="font-family:Arial;padding:20px;max-width:500px;margin:auto">
<h2>Owner Admin - Add Product</h2>
<p>No code needed. Add here, customer sees it instantly.</p>
<input id="pass" type="password" placeholder="Admin Password" style="width:100%;padding:12px;margin:5px 0"><br>
<input id="name" placeholder="Product Name e.g. PS5 Controller" style="width:100%;padding:12px;margin:5px 0"><br>
<input id="price" type="number" placeholder="Price e.g. 120000" style="width:100%;padding:12px;margin:5px 0"><br>
<input id="cat" placeholder="Category e.g. Controllers" style="width:100%;padding:12px;margin:5px 0"><br>
<input id="emoji" placeholder="Emoji e.g. 🎮" style="width:100%;padding:12px;margin:5px 0"><br>
<input id="desc" placeholder="Description" style="width:100%;padding:12px;margin:5px 0"><br>
<button onclick="add()" style="width:100%;padding:14px;background:#107C10;color:white;border:none;border-radius:8px;font-weight:bold">Add Product ➤</button>
<div id="msg"></div><h3>Current Products</h3><div id="list"></div>
<script>
function load(){ fetch('/api/products').then(r=>r.json()).then(d=>{ document.getElementById('list').innerHTML = d.map(p=>'<div style="border:1px solid #ddd;padding:10px;margin:5px 0">'+p.name+' - '+p.price+' TZS <button onclick="delProduct(\\''+p.id+'\\')">Delete</button></div>').join(''); }); }
function add(){ var body={password:document.getElementById('pass').value, name:document.getElementById('name').value, price:parseInt(document.getElementById('price').value), cat:document.getElementById('cat').value||'General', emoji:document.getElementById('emoji').value||'📦', desc:document.getElementById('desc').value}; fetch('/api/add',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)}).then(r=>r.json()).then(d=>{ document.getElementById('msg').innerHTML=d.message||d.error; load(); }); }
function delProduct(id){ var pw=prompt('Admin password?'); fetch('/api/delete',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({password:pw, id:id})}).then(r=>r.json()).then(d=>{ alert(d.message||d.error); load(); }); }
load();
</script></body></html>
"""
@app.route('/')
def home(): return HTML
@app.route('/admin')
def admin(): return ADMIN_HTML
@app.route('/api/products')
def api_products(): return jsonify(load_products())
@app.route('/api/add', methods=['POST'])
def api_add():
    d=request.get_json()
    if d.get('password') != ADMIN_PASSWORD: return jsonify({"error":"Wrong password"}),403
    prods=load_products()
    prods.append({"id":str(len(prods)+1)+"_"+os.urandom(3).hex(),"name":d.get('name'),"price":d.get('price',0),"cat":d.get('cat','General'),"emoji":d.get('emoji','📦'),"desc":d.get('desc','')})
    save_products(prods); return jsonify({"message":"Product added! Customer can see it now."})
@app.route('/api/delete', methods=['POST'])
def api_delete():
    d=request.get_json()
    if d.get('password') != ADMIN_PASSWORD: return jsonify({"error":"Wrong password"}),403
    prods=[p for p in load_products() if p['id']!=d.get('id')]; save_products(prods); return jsonify({"message":"Deleted"})
@app.route('/chat', methods=['POST'])
def chat():
    data=request.get_json(); msg=data.get('message',''); prods=load_products()
    # Smart search in products, not just AI
    m=msg.lower()
    found=[p for p in prods if p['name'].lower() in m or any(w in p['name'].lower() for w in m.split() if len(w)>3)]
    if found:
        p=found[0]
        return jsonify({"reply": f"Ndio! Tuna {p['name']} - {p['price']} TZS. Tap + Add hapo juu, ni rahisi!","add":p['id']})
    if not GROQ_KEY:
        return jsonify({"reply":"Tumia Search hapo juu - type jina la product, itatokea instantly.","add":""})
    try:
        system=f"You are shop assistant. Products: {str(prods[:20])}. Answer short Swahili+English. Return JSON {{\"reply\":\"...\", \"add\":\"product id or empty\"}}"
        data2={"model":"llama-3.3-70b-versatile","messages":[{"role":"system","content":system},{"role":"user","content":msg}],"temperature":0.3}
        req=urllib.request.Request("https://api.groq.com/openai/v1/chat/completions", data=json.dumps(data2).encode(), headers={"Authorization": f"Bearer {GROQ_KEY}", "Content-Type":"application/json"})
        with urllib.request.urlopen(req, timeout=20) as resp:
            out=json.loads(resp.read()); txt=out["choices"][0]["message"]["content"].replace("```json","").replace("```","").strip(); return jsonify(json.loads(txt))
    except Exception:
        return jsonify({"reply":"Tumia Search hapo juu - type jina la product, itatokea instantly.","add":""})
if __name__=='__main__':
    port=int(os.environ.get('PORT',5000)); app.run(host='0.0.0.0', port=port)
