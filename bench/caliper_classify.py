import csv, json, pathlib, re

BASE = str(pathlib.Path(__file__).resolve().parents[1] / "downloads")
meta = json.load(open(BASE + r"\_cal_hf_meta.json", encoding="utf-8"))
rows = list(csv.DictReader(open(BASE + r"\CalibreV3.csv", encoding="utf-8-sig")))
IDRE = re.compile(
    r"(?:Base|Finetune|Merge|Proprietary)(?:Reasoning)?([A-Za-z0-9][\w.\-]*/[\w.\-]+)"
)

# our own measured Russian (from docs)
RU = {
    "Ateron/Gemma-4-Dark-Thoughts-V2-31B": "96-100% (RU ok)",
    "Nimbz/Schattenblume-31B": "100%",
    "Naphula/Goetia-26B-A4B-v1.6": "100% RU-safe / 83% card",
    "Gryphe/Gemma-4-31B-StyleTune": "17-0% FAIL",
    "Gryphe/Gemma-4-26B-A4B-StyleTune-V2": "96-100%",
    "TheDrummer/Artemis-31B-v1.2": "92-96% (но RP-каша)",
    "Blazed-Forge/Split-Untied-31B": "75% -> 96% temp0.4",
    "hiwaifu-research/WaifuGemma4-26b-a4b-v1": "96% (card preset)",
}


def norm_donors(tags):
    ds = []
    for t in tags:
        if not t.startswith("base_model:"):
            continue
        x = t[len("base_model:") :]
        for pre in ("quantized:", "merge:", "finetune:"):
            if x.startswith(pre):
                x = x[len(pre) :]
        ds.append(x)
    seen, out = set(), []
    for d in ds:
        if d not in seen:
            seen.add(d)
            out.append(d)
    return out


def classify(h):
    m = meta.get(h, {})
    tags = m.get("tags", [])
    tl = [t.lower() for t in tags]
    is_merge = any(t in ("merge", "mergekit") for t in tl)
    donors = norm_donors(tags)
    base = any(
        d.lower()
        in (
            "google/gemma-4-31b-it",
            "google/gemma-4-26b-a4b-it",
            "google/gemma-4-12b-it",
        )
        for d in donors
    )
    heretic = any(
        ("heretic" in t) or ("abliterat" in t) or ("uncensored" in t) for t in tl
    )
    lang = m.get("cardData", {}).get("language")
    return is_merge, base, len(donors), heretic, lang, donors


print(
    f"{'model':50} {'RP':>5} {'ERP':>5} {'Cm':>5} {'M':>2} {'B':>2} {'d':>2} {'H':>2} lang"
)
cand = []
for r in rows:
    n = r["display_name"]
    if "Thinking" in n:
        continue
    try:
        pc = float(r.get("parameter_count_b") or 0)
    except ValueError:
        pc = 0
    if pc not in (12, 26, 31):
        continue
    m = IDRE.search(n)
    if not m:
        continue
    h = m.group(1)
    is_m, base, nd, here, lang, donors = classify(h)
    # keep only Gemma-4-ish
    if (
        not (is_m and any("gemma" in d.lower() for d in donors))
        and "gemma" not in h.lower()
        and not any("gemma" in t for t in meta.get(h, {}).get("tags", []))
    ):
        continue
    cand.append(
        (
            h,
            n,
            r["rp_score_v3"],
            r["erp_score_v3"],
            r["combined_v3"],
            is_m,
            base,
            nd,
            here,
            lang,
        )
    )


def nf(x):
    try:
        return float(str(x).replace("*", "").strip())
    except Exception:
        return 0.0


cand.sort(key=lambda x: -nf(x[2]))
for h, n, rp, erp, comb, is_m, base, nd, here, lang in cand:
    print(
        f"{n[:50]:50} {rp:>5} {erp:>5} {comb:>5} {('M' if is_m else 'F'):>2} {('Y' if base else '-'):>2} {nd:>2} {('H' if here else '-'):>2} {lang}"
    )
print()
print(
    "=== RU measured:",
)
for h, v in RU.items():
    print(" ", h, "->", v)
