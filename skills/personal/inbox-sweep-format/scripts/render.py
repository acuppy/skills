#!/usr/bin/env python3
"""Render an Inbox Sweep email from sweep JSON using the fixed templates.

Usage: render.py SWEEP.json --out DIR
Writes DIR/subject.txt, DIR/body.html, DIR/body.txt and prints their paths as JSON.
Exits 2 with every validation error listed if the input does not match the schema.
Stdlib only. Same input always produces byte-identical output.
"""
import argparse
import html
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from string import Template
from urllib.parse import quote_plus

TEMPLATES = Path(__file__).resolve().parent.parent / "templates"
FONT = "-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif"
RED, GREEN, GRAY, LIGHT_GRAY, AMBER, BLUE, INK = (
    "#cf222e", "#1a7f37", "#8c959f", "#afb8c1", "#9a6700", "#0969da", "#1f2328")
MUTED = "#6e7781"
SHORT_HYPHENATED = re.compile(r"\b([A-Za-z]{1,6})-([A-Za-z]{1,6})\b")


class InvalidSweep(Exception):
    def __init__(self, errors):
        super().__init__("\n".join(errors))
        self.errors = errors


# ---------- validation ----------

def validate(data):
    errors = []
    _require(data, "", {"account": str, "generated_at": str, "scanned": int}, errors)
    _optional(data, "", {"timezone_label": str, "errors": int, "subject_prefix": str, "preheader": str}, errors)
    _parse_time(data.get("generated_at"), "generated_at", errors)
    for key in ("todo", "handled", "fyi"):
        if not isinstance(data.get(key), list):
            errors.append(f"{key}: required list (use [] when empty)")
    for i, item in enumerate(_list(data, "todo")):
        path = f"todo[{i}]"
        _require(item, path, {"title": str, "source": str}, errors)
        _optional(item, path, {"detail": str}, errors)
        _target(item, path, errors)
        received = item.get("received_at")
        stamps = received if isinstance(received, list) else [received]
        if not stamps or any(not isinstance(s, str) for s in stamps):
            errors.append(f"{path}.received_at: required ISO timestamp or non-empty list of them")
        else:
            for s in stamps:
                _parse_time(s, f"{path}.received_at", errors)
        if "link" in item:
            _require(item["link"], f"{path}.link", {"label": str}, errors)
            _target(item["link"], f"{path}.link", errors)
    for i, item in enumerate(_list(data, "handled")):
        _require(item, f"handled[{i}]", {"title": str, "reason": str}, errors)
        _target(item, f"handled[{i}]", errors)
    for i, item in enumerate(_list(data, "fyi")):
        _require(item, f"fyi[{i}]", {"title": str}, errors)
        _target(item, f"fyi[{i}]", errors)
    swept = data.get("swept")
    if not isinstance(swept, dict):
        errors.append("swept: required object")
    else:
        if not isinstance(swept.get("by_source"), list):
            errors.append("swept.by_source: required list")
        for i, row in enumerate(_list(swept, "by_source")):
            _require(row, f"swept.by_source[{i}]", {"name": str, "count": int}, errors)
        for key in ("possible_misses", "unsure"):
            for i, item in enumerate(_list(swept, key)):
                _require(item, f"swept.{key}[{i}]", {"title": str}, errors)
                _target(item, f"swept.{key}[{i}]", errors)
    if errors:
        raise InvalidSweep(errors)


def _list(obj, key):
    value = obj.get(key) if isinstance(obj, dict) else None
    return value if isinstance(value, list) else []


def _require(obj, path, fields, errors):
    if not isinstance(obj, dict):
        errors.append(f"{path or 'root'}: must be an object")
        return
    for name, kind in fields.items():
        value = obj.get(name)
        if not isinstance(value, kind) or isinstance(value, bool) or (kind is str and not value.strip()):
            errors.append(f"{_join(path, name)}: required {kind.__name__}")


def _optional(obj, path, fields, errors):
    if not isinstance(obj, dict):
        return
    for name, kind in fields.items():
        if name in obj and (not isinstance(obj[name], kind) or isinstance(obj[name], bool)):
            errors.append(f"{_join(path, name)}: must be {kind.__name__}")


def _target(obj, path, errors):
    if not isinstance(obj, dict):
        return
    has_thread, has_search = bool(obj.get("thread_id")), bool(obj.get("search"))
    if has_thread == has_search:
        errors.append(f"{path}: needs exactly one of thread_id or search")


def _parse_time(value, path, errors):
    try:
        parsed = datetime.fromisoformat(value)
    except (TypeError, ValueError):
        errors.append(f"{path}: not an ISO 8601 timestamp")
        return
    if parsed.tzinfo is None:
        errors.append(f"{path}: needs a UTC offset, e.g. -07:00")


def _join(path, name):
    return f"{path}.{name}" if path else name


# ---------- formatting helpers ----------

def load(name):
    return Template((TEMPLATES / name).read_text().rstrip("\n"))


def fill(name, **values):
    return load(name).substitute(font=FONT, **values)


def esc(text):
    return html.escape(text, quote=True)


def nowrap_title(text):
    """Keep short hyphenated words like add-ons on one line; leave IDs like TKT-1042 alone."""
    return SHORT_HYPHENATED.sub("\\1\u2011\\2", text)


def href(account, item):
    base = f"https://mail.google.com/mail/?authuser={account}"
    if item.get("thread_id"):
        return f"{base}#all/{item['thread_id']}"
    return f"{base}#search/{quote_plus(item['search'])}"


def age(generated, received):
    stamps = received if isinstance(received, list) else [received]
    days = sorted(max(0, (generated - datetime.fromisoformat(s)).days) for s in stamps)
    return f"{days[0]}d" if days[0] == days[-1] else f"{days[0]}–{days[-1]}d"


def run_line(data):
    when = datetime.fromisoformat(data["generated_at"])
    clock = when.strftime("%I:%M %p").lstrip("0")
    tz = data.get("timezone_label", "PT")
    return f"{when:%a %b} {when.day} · {clock} {tz} · {data['scanned']} threads scanned"


def counts(data):
    return {
        "todo": len(data["todo"]),
        "handled": len(data["handled"]),
        "fyi": len(data["fyi"]),
        "swept": sum(row["count"] for row in data["swept"]["by_source"]),
    }


# ---------- HTML ----------

def render_html(data):
    c = counts(data)
    generated = datetime.fromisoformat(data["generated_at"])
    stats = "\n".join(
        fill("stat.html", value=value, label=label, color=color)
        for value, label, color in (
            (c["todo"], "to do", RED if c["todo"] else GREEN),
            (c["handled"], "handled", GREEN),
            (c["fyi"], "FYI", MUTED),
            (c["swept"], "swept", MUTED),
        )
    ).replace("</td>\n    <td", '</td><td width="8"></td>\n    <td')
    sections = [
        section("To do", c["todo"], RED, todo_rows(data, generated)),
    ]
    if data["handled"]:
        sections.append(section("Already handled", c["handled"], GREEN,
                                list_rows(data, data["handled"], "reason"), "no action needed"))
    if data["fyi"]:
        sections.append(section("FYI", c["fyi"], GRAY, list_rows(data, data["fyi"])))
    sections.append(section("Swept", c["swept"], LIGHT_GRAY, swept_body(data), count_color=MUTED,
                            wrap=False))
    return fill(
        "page.html",
        preheader=esc(preheader(data, c)),
        run_line=esc(run_line(data)),
        stats=stats,
        sections="\n".join(sections),
        footer=footer(data),
    ) + "\n"


def section(title, count, accent, body, subtitle="", count_color=None, wrap=True):
    sub = fill("section_subtitle.html", text=esc(subtitle)) if subtitle else ""
    header = fill("section_header.html", accent=accent, title=esc(title), count=count,
                  count_color=count_color or accent, subtitle=sub)
    if wrap:
        body = ('<tr><td><table role="presentation" width="100%" cellpadding="0" cellspacing="0" '
                f'border="0">{body}</table></td></tr>')
    return f"{header}\n{body}"


def todo_rows(data, generated):
    if not data["todo"]:
        return fill("todo_empty.html")
    rows = []
    for n, item in enumerate(data["todo"], 1):
        detail = ""
        if item.get("detail") or item.get("link"):
            link = ""
            if item.get("link"):
                sep = " · " if item.get("detail") else ""
                link = sep + fill("inline_link.html", href=esc(href(data["account"], item["link"])),
                                  color=BLUE, weight=400, label=esc(item["link"]["label"]))
            detail = fill("todo_detail.html", text=esc(item.get("detail", "")), link=link)
            detail = "\n" + detail.lstrip("\n")
        rows.append(fill(
            "todo_item.html",
            divider="border-top:1px solid #e6e8eb;" if n > 1 else "",
            n=n,
            href=esc(href(data["account"], item)),
            title=esc(nowrap_title(item["title"])),
            meta=esc(f"{item['source']} · {age(generated, item['received_at'])}"),
            detail=detail,
        ))
    return "\n".join(rows)


def list_rows(data, items, note_key=None):
    return "".join(
        fill("list_item.html", href=esc(href(data["account"], item)),
             title=esc(nowrap_title(item["title"])),
             note=fill("list_note.html", text=esc(item[note_key])) if note_key else "")
        for item in items
    )


def swept_body(data):
    swept = data["swept"]
    tally = " · ".join(f"{row['name']} {row['count']}" for row in swept["by_source"]) or "Nothing swept"
    extras = []
    for key, label, color in (("possible_misses", "Possible miss", AMBER), ("unsure", "Unsure", INK)):
        items = _list(swept, key)
        if items:
            links = ", ".join(
                fill("inline_link.html", href=esc(href(data["account"], item)), color=color,
                     weight=600, label=esc(item["title"]))
                for item in items)
            pad = "6px" if not extras else "4px"
            extras.append(fill("swept_extra.html", label=label, links=links, pad=pad))
    return fill("swept_body.html", tally=esc(tally), extras="".join(extras))


def footer(data):
    links = " · ".join(
        fill("inline_link.html", href=esc(href(data["account"], {"search": q})), color=BLUE,
             weight=400, label=label)
        for label, q in (("All to-dos", "label:Sweep-Do"), ("All swept", "label:Swept"),
                         ("Prior sweeps", '"Inbox Sweep"')))
    errors = data.get("errors", 0)
    status = fill("error_line.html", count=f"{errors} error{'' if errors == 1 else 's'}") if errors else "0 errors."
    return f"{links} · Ages are from the first message in each thread. {status}"


def preheader(data, c):
    if data.get("preheader"):
        return data["preheader"]
    lead = "; ".join(item["title"] for item in data["todo"][:3])
    head = f"{c['todo']} to do: {lead}." if lead else "Nothing to do."
    return f"{head} {c['handled']} already handled, {c['swept']} swept."


# ---------- subject and plain text ----------

def subject(data):
    c = counts(data)
    when = datetime.fromisoformat(data["generated_at"])
    clock = when.strftime("%I:%M %p").lstrip("0")
    prefix = f"{data['subject_prefix']} " if data.get("subject_prefix") else ""
    return (f"{prefix}Inbox Sweep · {c['todo']} to do · {c['handled']} handled · "
            f"{c['swept']} swept · {when:%a %b} {when.day}, {clock}")


def render_text(data):
    c = counts(data)
    generated = datetime.fromisoformat(data["generated_at"])
    todo = []
    for n, item in enumerate(data["todo"], 1):
        todo.append(f"{n}. {item['title']} ({item['source']}, {age(generated, item['received_at'])})")
        if item.get("detail"):
            todo.append(f"   {item['detail']}")
        todo.append(f"   {href(data['account'], item)}")
    swept = data["swept"]
    extras = [f"Possible miss: {i['title']}" for i in _list(swept, "possible_misses")]
    extras += [f"Unsure: {i['title']}" for i in _list(swept, "unsure")]
    tally = ", ".join(f"{row['name']} {row['count']}" for row in swept["by_source"]) or "nothing"
    return load("text.txt").substitute(
        run_line=run_line(data),
        stats_line=f"{c['todo']} to do · {c['handled']} handled · {c['fyi']} FYI · {c['swept']} swept",
        todo="\n".join(todo) or "Nothing needs you right now.",
        handled="\n".join(f"- {i['title']} · {i['reason']}" for i in data["handled"]) or "None.",
        fyi="\n".join(f"- {i['title']}" for i in data["fyi"]) or "None.",
        swept_total=c["swept"],
        tally=tally,
        swept_extras="\n".join(extras),
    ).rstrip() + "\n"


# ---------- entry point ----------

def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("sweep_json")
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    try:
        data = json.loads(Path(args.sweep_json).read_text())
        validate(data)
    except json.JSONDecodeError as err:
        sys.exit(f"invalid JSON: {err}")
    except InvalidSweep as err:
        print("sweep JSON failed validation:", file=sys.stderr)
        for line in err.errors:
            print(f"  - {line}", file=sys.stderr)
        sys.exit(2)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    files = {"subject": subject(data) + "\n", "html": render_html(data), "text": render_text(data)}
    paths = {"subject": out / "subject.txt", "html": out / "body.html", "text": out / "body.txt"}
    for key, path in paths.items():
        path.write_text(files[key])
    print(json.dumps({key: str(path) for key, path in paths.items()}, indent=2))


if __name__ == "__main__":
    main()
