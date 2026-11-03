import json,re,csv,difflib
from datetime import datetime
from collections import Counter

DOJ={
 "t1p":("/tmp/doj_T1_pardons.json","pardon","https://www.justice.gov/pardon/pardons-granted-president-donald-j-trump-2017-2021","2017-2021"),
 "t1c":("/tmp/doj_T1_commutations.json","commutation","https://www.justice.gov/pardon/commutations-granted-president-donald-j-trump-2017-2021","2017-2021"),
 "t2":("/tmp/doj_T2_all.json",None,"https://www.justice.gov/pardon/clemency-grants-president-donald-j-trump-2025-present","2025-present")}
WIKI={"2017-2021":"https://en.wikipedia.org/wiki/List_of_people_granted_executive_clemency_in_the_first_Trump_presidency",
      "2025-present":"https://en.wikipedia.org/wiki/List_of_people_granted_executive_clemency_in_the_second_Trump_presidency"}
FR="https://www.federalregister.gov/documents/2025/01/29/2025-01950/granting-pardons-and-commutation-of-sentences-for-certain-offenses-relating-to-the-events-at-or-near"

def norm(s):
    s=re.sub(r'\(.*?\)','',s or '');s=s.lower();s=re.split(r'\baka\b',s)[0]
    s=re.sub(r'[^a-z ]',' ',s);s=re.sub(r'\b(jr|sr|ii|iii|iv)\b',' ',s)
    return re.sub(r'\s+',' ',s).strip()
def iso(s):
    m=re.search(r'([A-Z][a-z]+)\s+(\d{1,2})\s*,\s*(\d{4})',s or '')
    if not m: return ""
    try: return datetime.strptime(f"{m.group(1)} {m.group(2)}, {m.group(3)}","%B %d, %Y").strftime("%Y-%m-%d")
    except: return ""
def restit(s):
    for pat in (r'\$([\d,]+(?:\.\d{2})?)\s*(?:in\s+)?restitution',r'restitution\s+(?:in the amount of\s+)?\$([\d,]+(?:\.\d{2})?)'):
        m=re.search(pat,s or '',re.I)
        if m: return "$"+m.group(1)
    return "Unknown"
def party(n):
    if re.search(r'\bdemocrat',n,re.I): return "Democratic"
    if re.search(r'\brepublican',n,re.I): return "Republican"
    return "Unknown"
def clean(n):
    n=re.sub(r'\[\s*\d+\s*\]','',n); return re.sub(r'\s+',' ',n).strip()

wiki=json.load(open("/tmp/wiki.json"))
wrows=[]
for term,key in (("2017-2021","w1"),("2025-present","w2")):
    for r in wiki[key]:
        if not r["name"] or "1,500" in r["name"]: continue
        wrows.append((term,r))

def find(term,name,kind=None):
    n=norm(name); best=None; bs=0
    for t,r in wrows:
        if t!=term: continue
        m=difflib.SequenceMatcher(None,n,norm(r["name"])).ratio()
        if kind and r["kind"]==kind and m>bs: best,bs=r,m
    if best and bs>=0.88: return best
    # fallback: same last name + first initial
    ln=n.split()[-1] if n.split() else ""
    for t,r in wrows:
        if t!=term: continue
        rn=norm(r["name"]).split()
        if rn and rn[-1]==ln and n and rn[0][:1]==n[0][:1]:
            if kind and r["kind"]!=kind: continue
            return r
    return None

rows=[];seen=set();used=set()
for k,(path,kind,url,term) in DOJ.items():
    for r in json.load(open(path)):
        name=r["name"].strip(); d=iso(r["heading"])
        typ=kind
        if k=="t2":
            h=r["heading"].lower()
            typ=None if ("commutation" in h and "pardon" in h) else ("commutation" if "commutation" in h else "pardon")
        w=find(term,name,typ if typ else None) or find(term,name)
        if typ is None: typ=w["kind"] if w else "Unknown"
        if w: used.add(id(w))
        notes=clean(w["notes"] if w else "")[:400]
        cat="Posthumous" if re.search(r'posthumou|deceased',notes,re.I) else "Individual"
        rec=dict(Name=name,Date=d,Type=typ.capitalize() if typ!="Unknown" else "Unknown",Category=cat,
                 Offense=clean(r["offense"]),Original_Sentence=clean(r["sentenced"]),Restitution_Amount=restit(r["sentenced"]),
                 Political_Party=party(notes),Court=clean(r["district"]),Notes=notes,Term=term,
                 Source_URL=url+((" | "+WIKI[term]) if w else ""),Verification_Status="Verified" if w else "Unverified")
        key=(term,norm(name),rec["Type"],d)
        if key in seen: continue
        seen.add(key); rows.append(rec)

# Wikipedia-only records
for term,r in wrows:
    if id(r) in used: continue
    n=norm(r["name"])
    if any(x[0]==term and norm(x[1]["Name"])==n for x in []): pass
    d=iso(r["date"])
    notes=clean(r["notes"])[:400]
    rec=dict(Name=r["name"],Date=d,Type=r["kind"].capitalize(),
             Category="Posthumous" if re.search(r'posthumou|deceased',notes,re.I) else "Individual",
             Offense=clean(r["offense"]),Original_Sentence=clean(r["sentenced"]),Restitution_Amount=restit(r["sentenced"]),
             Political_Party=party(notes),Court=clean(r["court"]),Notes=notes,Term=term,
             Source_URL=WIKI[term],Verification_Status="Unverified")
    key=(term,n,norm(rec["Type"]),d)
    if key in seen: continue
    seen.add(key); rows.append(rec)

J6=["Stewart Rhodes","Kelly Meggs","Kenneth Harrelson","Thomas Caldwell","Jessica Watkins","Roberto Minuta",
    "Edward Vallejo","David Moerschel","Joseph Hackett","Ethan Nordean","Joseph Biggs","Zachary Rehl",
    "Dominic Pezzola","Jeremy Bertino"]
for n in J6:
    rows.append(dict(Name=n,Date="2025-01-20",Type="Commutation",Category="Individual (named in mass clemency)",
        Offense="Seditious conspiracy and related offenses (Jan 6, 2021 Capitol breach)",
        Original_Sentence="Various (up to 18 years' imprisonment)",Restitution_Amount="Unknown",Political_Party="Unknown",
        Court="District of Columbia",Notes="Commuted to time served; named individually in Proclamation 10887.",
        Term="2025-present",Source_URL=FR+" | "+WIKI["2025-present"],Verification_Status="Verified"))
rows.append(dict(Name="Enrique Tarrio",Date="2025-01-20",Type="Pardon",Category="Individual (named in mass clemency)",
    Offense="Seditious conspiracy (Jan 6, 2021 Capitol breach)",Original_Sentence="22 years' imprisonment",
    Restitution_Amount="Unknown",Political_Party="Unknown",Court="District of Columbia",
    Notes="Proud Boys leader; covered by the full pardon in Proclamation 10887 (b); reported by name.",
    Term="2025-present",Source_URL=FR+" | "+WIKI["2025-present"],Verification_Status="Verified"))
rows.append(dict(Name="January 6 defendants (blanket grant)",Date="2025-01-20",Type="Pardon + Commutation",Category="Mass clemency",
    Offense="Various federal offenses related to the Jan 6, 2021 Capitol breach (sedition, obstruction, assault, etc.)",
    Original_Sentence="Various",Restitution_Amount="Unknown",Political_Party="Unknown",Court="Various (mostly District of Columbia)",
    Notes="Proclamation 10887: 14 named individuals commuted to time served; full pardon to all other Jan 6 defendants (~1,500); pending indictments dismissed with prejudice. Roster of the ~1,500 not published.",
    Term="2025-present",Source_URL=FR+" | "+WIKI["2025-present"],Verification_Status="Verified"))

hdr=["Name","Date","Type","Category","Offense","Original_Sentence","Restitution_Amount","Political_Party","Court","Notes","Term","Source_URL","Verification_Status"]
rows.sort(key=lambda r:(r["Term"],r["Date"],r["Name"]))
with open("trump_clemency.csv","w",newline="",encoding="utf-8") as f:
    w=csv.DictWriter(f,fieldnames=hdr); w.writeheader(); w.writerows(rows)
print("rows:",len(rows))
print("term+type:",dict(Counter((r["Term"],r["Type"]) for r in rows)))
print("verified:",dict(Counter(r["Verification_Status"] for r in rows)))
print("no date:",sum(1 for r in rows if not r["Date"]),"| Unknown type:",sum(1 for r in rows if r["Type"]=="Unknown"))
json.dump(rows,open("rows.json","w"))
