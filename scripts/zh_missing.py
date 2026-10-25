#!/usr/bin/env python3
"""Print, as Markdown, the English strings that have no zh-rCN counterpart.

    python3 scripts/zh_missing.py

Reads app/src/main/res/values/strings*.xml and the same files under
values-zh-rCN/, and lists every translatable key present in English and absent
in Chinese. Prints "OK" when nothing is missing. The Chinese-coverage workflow
uses the output as an issue body; run it by hand to see the same list.
"""
import glob
import os
import xml.etree.ElementTree as ET

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EN = os.path.join(ROOT, "app/src/main/res/values")
ZH = os.path.join(ROOT, "app/src/main/res/values-zh-rCN")


def entries(path):
    """name -> English text, for the translatable strings and plurals only."""
    out = {}
    for e in ET.parse(path).getroot():
        if e.tag not in ("string", "plurals") or e.get("translatable") == "false":
            continue
        if e.tag == "string":
            text = e.text or ""
        else:
            text = " ".join((i.text or "") for i in e.findall("item"))
        out[e.get("name")] = " ".join(text.split()).replace("|", "\\|")
    return out


def main():
    rows = []
    for path in sorted(glob.glob(os.path.join(EN, "strings*.xml"))):
        name = os.path.basename(path)
        en = entries(path)
        zh_path = os.path.join(ZH, name)
        zh = entries(zh_path) if os.path.exists(zh_path) else {}
        for key in sorted(set(en) - set(zh)):
            rows.append((name, key, en[key]))

    if not rows:
        print("OK")
        return

    print(f"`{len(rows)}` English string(s) have no Chinese in `values-zh-rCN/`; those screens fall back to English.")
    print()
    print("| file | key | English |")
    print("|---|---|---|")
    for name, key, text in rows:
        print(f"| `{name}` | `{key}` | {text} |")
    print()
    print("Translate them into `app/src/main/res/values-zh-rCN/<file>`, keeping the same key and placeholders (`%1$s`, `%d`, `\\n`).")


if __name__ == "__main__":
    main()
