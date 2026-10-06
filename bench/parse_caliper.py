import csv, json, pathlib, re, sys
from html.parser import HTMLParser

BASE = str(pathlib.Path(__file__).resolve().parents[1] / "downloads")


class TableParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.section = None
        self.headers = []  # list of (field, label)
        self.rows = []  # list of list of (field, text)
        self.cur = None
        self.in_cell = None
        self.cellfield = None
        self.buf = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "thead":
            self.section = "thead"
        elif tag == "tbody":
            self.section = "tbody"
        elif tag == "tr":
            self.cur = []
        elif tag in ("th", "td"):
            self.in_cell = tag
            self.cellfield = a.get("data-field")
            self.buf = []

    def handle_startendtag(self, tag, attrs):
        pass

    def handle_endtag(self, tag):
        if tag in ("th", "td"):
            txt = re.sub(r"\s+", " ", "".join(self.buf)).strip()
            if self.section == "thead" and tag == "th":
                self.headers.append((self.cellfield, txt))
            elif tag == "td" and self.cur is not None:
                self.cur.append((self.cellfield, txt))
            self.in_cell = None
        elif tag == "tr":
            if self.section == "tbody" and self.cur:
                self.rows.append(self.cur)
            self.cur = None
        elif tag in ("thead", "tbody"):
            self.section = None

    def handle_data(self, data):
        if self.in_cell:
            self.buf.append(data)


def parse(path):
    raw = open(path, encoding="utf-8", errors="replace").read()
    p = TableParser()
    p.feed(raw)
    return p


def to_csv(p, out):
    names = [f or lb for (f, lb) in p.headers]
    ncol = len(names)
    with open(out, "w", newline="", encoding="utf-8-sig") as fh:
        w = csv.writer(fh)
        w.writerow(names)
        for r in p.rows:
            vals = [t for (_, t) in r]
            # pad/truncate
            if len(vals) < ncol:
                vals += [""] * (ncol - len(vals))
            w.writerow(vals[:ncol])
    return names


for tag in ("V3", "V2"):
    path = f"{BASE}\\Calibre{tag}.html"
    p = parse(path)
    names = to_csv(p, f"{BASE}\\Calibre{tag}.csv")
    print(f"=== {tag}: rows={len(p.rows)} cols={len(names)}")
    print("columns:", names)
    # sanity: first data row
    print("row0:", [t for (_, t) in p.rows[0]][:14] if p.rows else None)
    print()
