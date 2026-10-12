<!DOCTYPE html>
<html lang="tr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Binance Spot Tarayıcı v2</title>
<style>
:root {
  color-scheme: light dark;
  --bg: light-dark(#f4f6fa,#0b1018);
  --panel: light-dark(#fff,#131c29);
  --text: light-dark(#172033,#edf2f7);
  --muted: light-dark(#667085,#9ba9bb);
  --border: light-dark(#e0e6ef,#28364a);
  --green:#19b879; --red:#ef626c; --blue:#5488ff;
  --amber:#d99a22;
}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--text);
font-family:system-ui,-apple-system,sans-serif}
main{max-width:1500px;margin:auto;padding:22px}
header{display:flex;justify-content:space-between;align-items:center;
flex-wrap:wrap;gap:14px;margin-bottom:20px}
h1{font-size:24px;margin:0 0 6px}
p,.muted{color:var(--muted);font-size:13px}
button,input,select{border:1px solid var(--border);border-radius:9px;
background:var(--panel);color:var(--text);padding:10px 12px;font:inherit}
button{cursor:pointer;font-weight:650}
button:hover{border-color:var(--blue)}
.cards{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));
gap:12px;margin-bottom:16px}
.card,.workspace{background:var(--panel);border:1px solid var(--border);
border-radius:13px}
.card{padding:16px}
.card span{display:block;color:var(--muted);font-size:12px}
.card strong{display:block;font-size:25px;margin-top:8px}
.workspace{overflow:hidden}
.toolbar{padding:14px;display:flex;gap:10px;flex-wrap:wrap;
border-bottom:1px solid var(--border)}
.toolbar input{flex:1;min-width:160px}
.status{padding:12px 14px;border-bottom:1px solid var(--border);
font-size:12px;color:var(--muted)}
.table-wrap{overflow-x:auto}
table{width:100%;border-collapse:collapse;white-space:nowrap}
th,td{text-align:left;padding:12px 10px;border-bottom:1px solid var(--border);
font-size:12px}
th{color:var(--muted);font-size:10px;text-transform:uppercase}
tbody tr:hover{background:var(--bg)}
.coin{font-weight:750}
.num{font-variant-numeric:tabular-nums}
.badge{display:inline-block;border-radius:6px;padding:5px 7px;
font-size:10px;font-weight:750}
.buy{color:var(--green);background:light-dark(#e4f8ef,#123a2d)}
.watch{color:var(--blue);background:light-dark(#eaf0ff,#1d2e52)}
.warn{color:var(--amber);background:light-dark(#fff4d7,#40351b)}
.bad{color:var(--red);background:light-dark(#ffe8e8,#402126)}
.empty{padding:35px;text-align:center;color:var(--muted)}
.note{margin:14px 2px;color:var(--muted);font-size:12px;line-height:1.6}
@media(max-width:800px){
 main{padding:12px}.cards{grid-template-columns:repeat(2,minmax(0,1fr))}
 .card{padding:12px}.card strong{font-size:22px}h1{font-size:20px}
}
</style>
</head>
<body>
<main>
<header>
 <div>
  <h1>◈ Binance Spot Tarayıcı v2</h1>
  <p>1 saatlik sinyaller · Hacim filtresi · Giriş kalitesi</p>
 </div>
 <button id="refresh">↻ Raporu yenile</button>
</header>

<section class="cards">
 <div class="card"><span>Raporlanan coin</span><strong id="total">—</strong></div>
 <div class="card"><span>AL sinyali</span><strong id="buys">—</strong></div>
 <div class="card"><span>Girişe uygun aday</span><strong id="ready">—</strong></div>
 <div class="card"><span>2M USD üstü hacim</span><strong id="liquid">—</strong></div>
</section>

<section class="workspace">
 <div class="toolbar">
  <input id="search" placeholder="Coin ara, ör. BTCUSDT">
  <select id="filter">
   <option value="all">Tüm coinler</option>
   <option value="buy">AL sinyalleri</option>
   <option value="ready">Girişe uygun</option>
   <option value="wait">Bekle / riskli</option>
   <option value="volume">2M USD üzeri hacim</option>
  </select>
  <select id="sort">
   <option value="score">Puana göre</option>
   <option value="volume">Hacme göre</option>
   <option value="rsi">RSI'ye göre</option>
   <option value="symbol">Coin adına göre</option>
  </select>
 </div>
 <div class="status" id="status">Rapor yükleniyor…</div>
 <div class="table-wrap">
 <table>
 <thead><tr>
  <th>Coin</th><th>Sinyal</th><th>Giriş değerlendirmesi</th>
  <th>Puan</th><th>Fiyat</th><th>Giriş</th><th>Stop</th>
  <th>Hedef</th><th>RSI</th><th>24s hacim (USDT)</th>
 </tr></thead>
 <tbody id="rows"><tr><td colspan="10" class="empty">Rapor bekleniyor…</td></tr></tbody>
 </table>
 </div>
</section>

<div class="note">
 Hacim eşiği: 2.000.000 USDT. Rapor dosyasındaki quote_volume_24h alanı kullanılır.
 Giriş değerlendirmesi mevcut CSV alanlarından yaklaşık olarak üretilir; EMA,
 MACD, mum kapanışı ve gerçek piyasa rejimi CSV'de yoksa doğrulanamaz.
 Bu panel emir göndermez ve canlı fiyat akışı sağlamaz.
</div>
</main>
<script>
const $ = id => document.getElementById(id);
const MIN_VOLUME = 2000000;
let data = [];

function parseCSV(text) {
 const lines = text.replace(/^\uFEFF/,"").trim().split(/\r?\n/);
 if(lines.length<2) return [];
 function splitLine(line) {
  const out=[]; let v="",q=false;
  for(let i=0;i<line.length;i++){
   const c=line[i];
   if(c==='"' && q && line[i+1]==='"'){v+='"';i++}
   else if(c==='"') q=!q;
   else if(c===","&&!q){out.push(v);v=""}
   else v+=c;
  }
  out.push(v);return out;
 }
 const headers=splitLine(lines[0]);
 return lines.slice(1).filter(x=>x.trim()).map(line=>{
  const vals=splitLine(line),o={};
  headers.forEach((h,i)=>o[h]=vals[i]??"");
  return o;
 });
}
function n(v){
 if(v===null||v===undefined||String(v).trim()==="")return null;
 const x=Number(v);return Number.isFinite(x)?x:null;
}
function fmt(v,d=6){
 const x=n(v);return x===null?"—":x.toLocaleString("tr-TR",{maximumFractionDigits:d});
}
function isBuy(r){return (r.signal||"").toUpperCase().startsWith("AL")}
function isWatch(r){return (r.signal||"").toUpperCase().startsWith("İZLE")}
function volume(r){return n(r.quote_volume_24h)??0}
function quality(r){
 const price=n(r.price),entry=n(r.entry),rsi=n(r.rsi);
 if(!isBuy(r))return {text:isWatch(r)?"GERİ TEST BEKLE":"AL SİNYALİ YOK",kind:"watch"};
 if(volume(r)<MIN_VOLUME)return {text:"HACİM YETERSİZ",kind:"bad"};
 if(price===null||entry===null||price<=0||entry<=0)
  return {text:"VERİ EKSİK",kind:"warn"};
 const distance=(price-entry)/entry*100;
 if(distance>2)return {text:"YÜKSELİŞİ KOVALAMA",kind:"bad"};
 if(rsi!==null&&rsi>=70)return {text:"AŞIRI ISINMIŞ",kind:"bad"};
 if(rsi!==null&&rsi<50)return {text:"MOMENTUM ZAYIF",kind:"warn"};
 if(distance>0.8)return {text:"GERİ ÇEKİLME BEKLE",kind:"warn"};
 return {text:"ADAY — DOĞRULAMA GEREKLİ",kind:"buy"};
}
function render(){
 $("total").textContent=data.length;
 $("buys").textContent=data.filter(isBuy).length;
 $("liquid").textContent=data.filter(r=>volume(r)>=MIN_VOLUME).length;
 $("ready").textContent=data.filter(r=>{
  const q=quality(r);return q.kind==="buy";
 }).length;

 const query=$("search").value.trim().toUpperCase();
 const filter=$("filter").value,sort=$("sort").value;
 let rows=data.filter(r=>{
  if(query&&!(r.symbol||"").toUpperCase().includes(query))return false;
  const q=quality(r);
  if(filter==="buy"&&!isBuy(r))return false;
  if(filter==="ready"&&q.kind!=="buy")return false;
  if(filter==="wait"&&(q.kind==="buy"))return false;
  if(filter==="volume"&&volume(r)<MIN_VOLUME)return false;
  return true;
 });
 rows.sort((a,b)=>{
  if(sort==="symbol")return (a.symbol||"").localeCompare(b.symbol||"");
  const k=sort==="volume"?"quote_volume_24h":sort==="rsi"?"rsi":"score";
  return (n(b[k])??-Infinity)-(n(a[k])??-Infinity);
 });
 $("rows").innerHTML="";
 if(!rows.length){
  $("rows").innerHTML='<tr><td colspan="10" class="empty">Bu filtrede sonuç yok.</td></tr>';return;
 }
 for(const r of rows){
  const q=quality(r),tr=document.createElement("tr");
  const vals=[
   r.symbol||"—",r.signal||"—",q.text,r.score||"—",
   fmt(r.price),fmt(r.entry),fmt(r.stop),fmt(r.target),
   fmt(r.rsi,2),fmt(r.quote_volume_24h,0)
  ];
  vals.forEach((v,i)=>{
   const td=document.createElement("td");
   if(i===0)td.className="coin";
   if(i===3||i>=4)td.classList.add("num");
   if(i===1||i===2){
    const b=document.createElement("span");b.className="badge ";
    if(i===2)b.className+=""+q.kind;
    else b.className+=(isBuy(r)?"buy":isWatch(r)?"watch":"warn");
    b.textContent=v;td.appendChild(b);
   }else td.textContent=v;
   if(i===6)td.classList.add("negative");
   tr.appendChild(td);
  });
  $("rows").appendChild(tr);
 }
}
async function loadReport(){
 $("status").textContent="Son tarama raporu yükleniyor…";
 $("refresh").disabled=true;
 try{
  const res=await fetch("reports/latest.csv?t="+Date.now(),{cache:"no-store"});
  if(!res.ok)throw new Error("HTTP "+res.status);
  const csv=await res.text();data=parseCSV(csv);render();
  $("status").textContent="CSV yüklendi · "+data.length+
   " satır · Sayfa yenilenme: "+new Date().toLocaleString("tr-TR")+
   " · Raporun gerçek üretim zamanı CSV'de ayrıca bulunmalıdır.";
 }catch(e){
  data=[];render();
  $("status").textContent="Rapor yüklenemedi: "+e.message+
   " · GitHub Actions ve Pages yayınını kontrol et.";
 }finally{$("refresh").disabled=false}
}
$("refresh").addEventListener("click",loadReport);
$("search").addEventListener("input",render);
$("filter").addEventListener("change",render);
$("sort").addEventListener("change",render);
loadReport();
</script>
</body>
</html>
