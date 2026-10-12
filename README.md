<!DOCTYPE html>
<html lang="tr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Binance Spot Tarayıcı</title>
<style>
:root {
  color-scheme: light dark;
  --bg: light-dark(#f4f6fa, #0b1018);
  --panel: light-dark(#ffffff, #131c29);
  --text: light-dark(#172033, #edf2f7);
  --muted: light-dark(#667085, #9ba9bb);
  --border: light-dark(#e0e6ef, #28364a);
  --green: #19b879;
  --red: #ef626c;
  --blue: #5488ff;
}
* { box-sizing: border-box; }
body {
  margin: 0;
  background: var(--bg);
  color: var(--text);
  font-family: system-ui, -apple-system, sans-serif;
}
main { max-width: 1450px; margin: auto; padding: 24px; }
header {
  display: flex; justify-content: space-between;
  align-items: center; flex-wrap: wrap; gap: 16px;
  margin-bottom: 24px;
}
h1 { font-size: 25px; margin: 0 0 6px; }
p { margin: 0; color: var(--muted); font-size: 13px; }
button, input, select {
  border: 1px solid var(--border); border-radius: 9px;
  background: var(--panel); color: var(--text);
  padding: 11px 13px; font: inherit;
}
button { cursor: pointer; font-weight: 650; }
button:hover { border-color: var(--blue); }
.cards {
  display: grid; grid-template-columns: repeat(4, minmax(0,1fr));
  gap: 14px; margin-bottom: 20px;
}
.card, .workspace {
  background: var(--panel); border: 1px solid var(--border);
  border-radius: 14px;
}
.card { padding: 18px; }
.card span { display: block; color: var(--muted); font-size: 13px; }
.card strong { display: block; font-size: 27px; margin-top: 9px; }
.workspace { overflow: hidden; }
.toolbar {
  padding: 16px; display: flex; flex-wrap: wrap;
  gap: 10px; border-bottom: 1px solid var(--border);
}
.toolbar input { flex: 1; min-width: 170px; }
.toolbar select { min-width: 155px; }
.status {
  padding: 12px 16px; color: var(--muted);
  font-size: 13px; border-bottom: 1px solid var(--border);
}
.table-wrap { overflow-x: auto; }
table { width: 100%; border-collapse: collapse; white-space: nowrap; }
th, td {
  text-align: left; padding: 14px 13px;
  border-bottom: 1px solid var(--border); font-size: 13px;
}
th {
  color: var(--muted); font-size: 11px;
  text-transform: uppercase; letter-spacing: .04em;
}
tbody tr:hover { background: var(--bg); }
.coin { font-weight: 750; }
.num { font-variant-numeric: tabular-nums; }
.badge {
  display: inline-block; border-radius: 6px;
  padding: 5px 8px; font-size: 11px; font-weight: 750;
}
.buy { color: var(--green); background: light-dark(#e4f8ef,#123a2d); }
.watch { color: var(--blue); background: light-dark(#eaf0ff,#1d2e52); }
.negative { color: var(--red); }
.empty { padding: 40px 20px; text-align: center; color: var(--muted); }
footer { padding: 16px 2px; color: var(--muted); font-size: 12px; }
@media(max-width:800px) {
  main { padding: 15px; }
  .cards { grid-template-columns: repeat(2,minmax(0,1fr)); gap: 10px; }
  .card { padding: 14px; }
  .card strong { font-size: 23px; }
  h1 { font-size: 21px; }
}
</style>
</head>
<body>
<main>
  <header>
    <div>
      <h1>◈ Binance Spot Tarayıcı</h1>
      <p>1 saatlik analiz · Kırılım ve geri test · Spot piyasa</p>
    </div>
    <button id="refresh">↻ Raporu yenile</button>
  </header>

  <section class="cards">
    <div class="card"><span>Listelenen adaylar</span><strong id="total">—</strong></div>
    <div class="card"><span>AL adayı</span><strong id="buys">—</strong></div>
    <div class="card"><span>Geri test bekleyen</span><strong id="watch">—</strong></div>
    <div class="card"><span>En yüksek puan</span><strong id="top">—</strong></div>
  </section>

  <section class="workspace">
    <div class="toolbar">
      <input id="search" placeholder="Coin ara, ör. BTCUSDT">
      <select id="filter">
        <option value="all">Tüm sonuçlar</option>
        <option value="buy">AL adayları</option>
        <option value="watch">Geri test bekleyenler</option>
      </select>
      <select id="sort">
        <option value="score">Puana göre sırala</option>
        <option value="volume">Hacme göre sırala</option>
        <option value="rsi">RSI'ye göre sırala</option>
        <option value="symbol">Coin adına göre sırala</option>
      </select>
    </div>
    <div class="status" id="status">Rapor yükleniyor…</div>
    <div class="table-wrap">
      <table>
        <thead>
          <tr>
            <th>Coin</th><th>Durum</th><th>Puan</th>
            <th>Fiyat</th><th>Giriş</th><th>STOP</th>
            <th>HEDEF</th><th>RSI</th><th>24s hacim (USDT)</th>
          </tr>
        </thead>
        <tbody id="rows">
          <tr><td colspan="9" class="empty">Rapor bekleniyor…</td></tr>
        </tbody>
      </table>
    </div>
  </section>

  <footer>
    Veriler son başarılı tarama raporundan alınır; canlı fiyat akışı değildir.
    STOP ve HEDEF ATR bazlı hesaplanır. Bu panel emir göndermez.
  </footer>
</main>
<script>
const $ = id => document.getElementById(id);
let data = [];

function parseCSV(text) {
  const lines = text.replace(/^\uFEFF/, "").trim().split(/\r?\n/);
  if (lines.length < 2) return [];
  function splitLine(line) {
    const result = [];
    let value = "", quoted = false;
    for (let i = 0; i < line.length; i++) {
      const c = line[i];
      if (c === '"' && quoted && line[i + 1] === '"') {
        value += '"'; i++;
      } else if (c === '"') {
        quoted = !quoted;
      } else if (c === "," && !quoted) {
        result.push(value); value = "";
      } else value += c;
    }
    result.push(value);
    return result;
  }
  const headers = splitLine(lines[0]);
  return lines.slice(1).filter(line => line.trim()).map(line => {
    const values = splitLine(line);
    const item = {};
    headers.forEach((key, i) => item[key] = values[i] ?? "");
    return item;
  });
}

function number(v) {
  const n = Number(v);
  return Number.isFinite(n) ? n : null;
}
function fmt(v, digits = 6) {
  const n = number(v);
  if (n === null) return "—";
  return n.toLocaleString("tr-TR", {
    maximumFractionDigits: digits
  });
}
function isBuy(row) {
  return (row.signal || "").startsWith("AL");
}
function isWatch(row) {
  return (row.signal || "").startsWith("İZLE");
}

function render() {
  $("total").textContent = data.length;
  $("buys").textContent = data.filter(isBuy).length;
  $("watch").textContent = data.filter(isWatch).length;
  const scores = data.map(x => number(x.score)).filter(x => x !== null);
  $("top").textContent = scores.length ? Math.max(...scores) : "—";

  const query = $("search").value.trim().toUpperCase();
  const filter = $("filter").value;
  const sort = $("sort").value;

  let rows = data.filter(row => {
    if (query && !(row.symbol || "").toUpperCase().includes(query))
      return false;
    if (filter === "buy" && !isBuy(row)) return false;
    if (filter === "watch" && !isWatch(row)) return false;
    return true;
  });

  rows.sort((a, b) => {
    if (sort === "symbol")
      return (a.symbol || "").localeCompare(b.symbol || "");
    const key = sort === "volume" ? "quote_volume_24h" :
                sort === "rsi" ? "rsi" : "score";
    return (number(b[key]) ?? -Infinity) -
           (number(a[key]) ?? -Infinity);
  });

  $("rows").innerHTML = "";
  if (!rows.length) {
    $("rows").innerHTML =
      '<tr><td colspan="9" class="empty">Bu filtrede sonuç bulunamadı. Tarama raporunda uygun aday olmayabilir.</td></tr>';
    return;
  }

  for (const row of rows) {
    const tr = document.createElement("tr");
    const statusClass = isBuy(row) ? "buy" : "watch";
    const statusText = isBuy(row) ? "AL ADAYI" :
                       isWatch(row) ? "GERİ TEST BEKLENİYOR" :
                       (row.signal || "İZLE");

    const values = [
      row.symbol || "—",
      null,
      row.score || "—",
      fmt(row.price),
      fmt(row.entry),
      fmt(row.stop),
      fmt(row.target),
      fmt(row.rsi, 2),
      fmt(row.quote_volume_24h, 0)
    ];

    values.forEach((value, i) => {
      const td = document.createElement("td");
      if (i === 0) {
        td.className = "coin";
        td.textContent = value;
      } else if (i === 1) {
        const badge = document.createElement("span");
        badge.className = "badge " + statusClass;
        badge.textContent = statusText;
        td.appendChild(badge);
      } else {
        td.className = "num";
        td.textContent = value;
        if (i === 5) td.classList.add("negative");
      }
      tr.appendChild(td);
    });
    $("rows").appendChild(tr);
  }
}

async function loadReport() {
  $("status").textContent = "Son tarama raporu yükleniyor…";
  $("refresh").disabled = true;
  try {
    const response = await fetch("reports/latest.csv?t=" + Date.now(), {
      cache: "no-store"
    });
    if (!response.ok) {
      throw new Error("Rapor bulunamadı (HTTP " + response.status + ")");
    }
    data = parseCSV(await response.text());
    render();
    $("status").textContent =
      "Rapor yüklendi · " + data.length +
      " sonuç · " + new Date().toLocaleString("tr-TR");
  } catch (error) {
    $("status").textContent =
      "Rapor yüklenemedi: " + error.message +
      ". GitHub Actions taramasını ve Pages yayınını kontrol et.";
    data = [];
    render();
  } finally {
    $("refresh").disabled = false;
  }
}

$("refresh").addEventListener("click", loadReport);
$("search").addEventListener("input", render);
$("filter").addEventListener("change", render);
$("sort").addEventListener("change", render);
loadReport();
</script>
</body>
</html>
