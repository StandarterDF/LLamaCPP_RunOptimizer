import csv, json, pathlib, re, time, urllib.request, urllib.error

BASE = str(pathlib.Path(__file__).resolve().parents[1] / "downloads")
rows = list(csv.DictReader(open(BASE + r"\CalibreV3.csv", encoding="utf-8-sig")))

IDRE = re.compile(
    r"(?:Base|Finetune|Merge|Proprietary)(?:Reasoning)?([A-Za-z0-9][\w.\-]*/[\w.\-]+)"
)


def hfid(name):
    m = IDRE.search(name)
    return m.group(1) if m else None


cands = []
for r in rows:
    pc = r.get("parameter_count_b", "")
    try:
        pcv = float(pc)
    except ValueError:
        continue
    if pcv not in (12, 26, 31):
        continue
    h = hfid(r["display_name"])
    if not h:
        continue
    cands.append(
        (
            h,
            r["display_name"],
            r["rp_score_v3"],
            r["erp_score_v3"],
            r["combined_v3"],
            r["parameter_count_b"],
        )
    )

# dedupe by hf_id keeping first (non-thinking first? keep all)
byid = {}
for h, dn, rp, erp, comb, pcb in cands:
    byid.setdefault(h, (dn, rp, erp, comb, pcb))
print("unique hf ids:", len(byid))

out = {}
for i, (h, _) in enumerate(byid.items(), 1):
    url = "https://huggingface.co/api/models/" + h
    try:
        req = urllib.request.Request(
            url, headers={"User-Agent": "gguf-launcher-research"}
        )
        d = json.load(urllib.request.urlopen(req, timeout=25))
        out[h] = {
            "tags": d.get("tags", []),
            "cardData": d.get("cardData", {}),
            "downloads": d.get("downloads"),
            "likes": d.get("likes"),
        }
    except urllib.error.HTTPError as e:
        out[h] = {"error": f"HTTP {e.code}"}
    except Exception as e:
        out[h] = {"error": str(e)}
    if i % 25 == 0:
        print("fetched", i)
    time.sleep(0.05)

json.dump(
    out,
    open(BASE + r"\_cal_hf_meta.json", "w", encoding="utf-8"),
    ensure_ascii=False,
    indent=0,
)
print("saved", len(out))
