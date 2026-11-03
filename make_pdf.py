import csv, html
from collections import Counter
rows=list(csv.DictReader(open("trump_clemency.csv",encoding="utf-8")))
hdr=list(rows[0].keys())
bt=Counter((r["Term"],r["Type"]) for r in rows)
bv=Counter(r["Verification_Status"] for r in rows)
def esc(s): return html.escape(s or "")
summ="".join(f"<tr><td>{esc(t)}</td><td>{esc(ty)}</td><td class='n'>{n}</td></tr>" for (t,ty),n in sorted(bt.items()))
body="".join("<tr>"+"".join(f"<td>{esc(r[c])}</td>" for c in hdr)+"</tr>" for r in rows)
html_doc=f"""<html><head><meta charset="utf-8"><style>
@page {{ size: A3 landscape; margin: 10mm 8mm; @bottom-center {{ content: "Trump clemency dataset — page " counter(page) " of " counter(pages); font: 7pt sans-serif; color:#666; }} }}
body {{ font-family: "DejaVu Sans", sans-serif; }}
h1 {{ font-size:16pt; margin:0 0 2mm; }} h2 {{ font-size:11pt; margin:6mm 0 2mm; }}
p.meta {{ font-size:8pt; color:#444; margin:0 0 4mm; }}
table.sum {{ border-collapse:collapse; font-size:9pt; margin-bottom:4mm; }}
table.sum td,table.sum th {{ border:1px solid #999; padding:2px 8px; }}
table.sum th {{ background:#eee; }}
table.data {{ border-collapse:collapse; width:100%; font-size:6.4pt; }}
table.data th {{ background:#222; color:#fff; padding:2px; text-align:left; font-size:6.6pt; }}
table.data td {{ border:0.4pt solid #bbb; padding:1.4px 2px; vertical-align:top; word-wrap:break-word; }}
table.data tr:nth-child(even) td {{ background:#f6f6f6; }}
thead {{ display: table-header-group; }}
tr {{ page-break-inside: avoid; }}
td:nth-child(1) {{ width:8%; }} td:nth-child(2) {{ width:4.5%; }} td:nth-child(3) {{ width:4.5%; }}
td:nth-child(4) {{ width:5.5%; }} td:nth-child(5) {{ width:13%; }} td:nth-child(6) {{ width:10%; }}
td:nth-child(7) {{ width:5%; }} td:nth-child(8) {{ width:4%; }} td:nth-child(9) {{ width:6%; }}
td:nth-child(10) {{ width:14%; }} td:nth-child(11) {{ width:4.5%; }} td:nth-child(12) {{ width:15%; }}
td:nth-child(13) {{ width:4.5%; }}
</style></head><body>
<h1>Pardons, Commutations &amp; Mass Clemency — Donald J. Trump</h1>
<p class="meta">Terms 2017–2021 and 2025–present · {len(rows)} records · Sources: DOJ Office of the Pardon Attorney (primary),
Wikipedia (cross-check), Federal Register Proclamation 10887 (Jan 6, 2025). Generated from trump_clemency.csv.<br>
Verified = present in both DOJ and Wikipedia; Unverified = single source, retained and flagged.</p>
<h2>Counts by term and type</h2>
<table class="sum"><tr><th>Term</th><th>Type</th><th>Records</th></tr>{summ}
<tr><td colspan="2"><b>Total</b></td><td class="n"><b>{len(rows)}</b></td></tr></table>
<p class="meta">Verification: {bv.get('Verified',0)} Verified · {bv.get('Unverified',0)} Unverified</p>
<h2>Records</h2>
<table class="data"><thead><tr>{''.join(f'<th>{esc(c)}</th>' for c in hdr)}</tr></thead><tbody>{body}</tbody></table>
</body></html>"""
open("/tmp/report.html","w",encoding="utf-8").write(html_doc)
from weasyprint import HTML
HTML(string=html_doc).write_pdf("trump_clemency.pdf")
print("ok")
