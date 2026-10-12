#!/usr/bin/env python3
"""Pinned Walmart item IDs for grocery list names.

Usage:
  pins.py add <walmart-url-or-id> --key "<list name>" [--alias "<alias>" ...] [--name "<product name>"]
  pins.py lookup "<list item>"        # prints JSON for the pin, exit 1 if no match
  pins.py normalize "<text>"          # prints the normalized form
  pins.py list

Pins live in pins.json next to the project root. Keys and aliases are stored
normalized; lookup normalizes the input the same way and requires an exact match.
"""
import argparse
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

PINS_PATH = Path(__file__).resolve().parent.parent / "pins.json"

QTY_WORDS = {"a", "an", "some", "dozen", "pack", "of", "x"}


def normalize(text: str) -> str:
    s = text.lower().strip()
    s = re.sub(r"[^a-z0-9\s]", " ", s)          # punctuation -> space
    s = re.sub(r"\s+", " ", s).strip()
    words = s.split(" ")
    # drop leading counts/quantity words: "2 dozen eggs", "1x milk", "a loaf of bread"
    while words and (re.fullmatch(r"\d+x?", words[0]) or words[0] in QTY_WORDS):
        words.pop(0)
    if not words:
        return ""
    words[-1] = singularize(words[-1])
    return " ".join(words)


def singularize(w: str) -> str:
    if len(w) <= 3 or w.endswith("ss"):
        return w
    if w.endswith("ies"):
        return w[:-3] + "y"
    if w.endswith("oes"):                       # tomatoes, potatoes
        return w[:-2]
    if w.endswith("es") and re.search(r"(s|x|z|ch|sh)es$", w):
        return w[:-2]
    if w.endswith("s"):
        return w[:-1]
    return w


def parse_item(url_or_id: str) -> tuple[str, str]:
    """Return (item_id, slug). Accepts a full walmart.com/ip URL or a bare numeric ID."""
    if re.fullmatch(r"\d+", url_or_id):
        return url_or_id, ""
    path = urlparse(url_or_id).path
    m = re.search(r"/ip/(?:([^/]+)/)?(\d+)", path)
    if not m:
        sys.exit(f"could not find an item ID in: {url_or_id}")
    slug = (m.group(1) or "").replace("-", " ")
    return m.group(2), slug


def load() -> dict:
    if not PINS_PATH.exists():
        return {}
    return json.loads(PINS_PATH.read_text())


def save(pins: dict) -> None:
    PINS_PATH.write_text(json.dumps(pins, indent=2, sort_keys=True) + "\n")


def cmd_add(a):
    item_id, slug = parse_item(a.target)
    key = normalize(a.key)
    if not key:
        sys.exit("key normalized to empty string")
    aliases = sorted({normalize(x) for x in a.alias if normalize(x) and normalize(x) != key})
    pins = load()
    # refuse to let an alias shadow another pin's key
    for k, v in pins.items():
        if k == key:
            continue
        clash = set(aliases) & ({k} | set(v.get("aliases", [])))
        if clash:
            sys.exit(f"alias {sorted(clash)} already belongs to pin '{k}'")
    pins[key] = {
        "id": item_id,
        "name": a.name or slug or pins.get(key, {}).get("name", ""),
        "url": f"https://www.walmart.com/ip/{item_id}",
        "aliases": aliases,
    }
    save(pins)
    print(json.dumps({key: pins[key]}, indent=2))


def cmd_lookup(a):
    q = normalize(a.item)
    for key, pin in load().items():
        if q == key or q in pin.get("aliases", []):
            print(json.dumps({"key": key, **pin}))
            return
    print(f"no pin for '{a.item}' (normalized: '{q}')", file=sys.stderr)
    sys.exit(1)


def cmd_normalize(a):
    print(normalize(a.text))


def cmd_list(a):
    for key, pin in load().items():
        al = ", ".join(pin.get("aliases", []))
        print(f"{key:20} {pin['id']:12} {pin.get('name','')}" + (f"  [{al}]" if al else ""))


def main():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("add"); s.add_argument("target"); s.add_argument("--key", required=True)
    s.add_argument("--alias", action="append", default=[]); s.add_argument("--name"); s.set_defaults(fn=cmd_add)
    s = sub.add_parser("lookup"); s.add_argument("item"); s.set_defaults(fn=cmd_lookup)
    s = sub.add_parser("normalize"); s.add_argument("text"); s.set_defaults(fn=cmd_normalize)
    s = sub.add_parser("list"); s.set_defaults(fn=cmd_list)
    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
