#!/usr/bin/env python3
"""בונה קובץ HTML אחד עצמאי מתוך template.html ותיקיית content/.

מבנה התוכן:
  content/courses/<course-id>/course.json        - פרטי הקורס והסילבוס
  content/courses/<course-id>/lessons/lNN.json   - מפגש אחד לכל קובץ

הוספת קורס חדש: יוצרים תיקייה חדשה תחת content/courses עם אותו מבנה, ומריצים:
  python build.py
התוצאה: dist/course-portal.html
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).parent
COURSES_DIR = ROOT / "content" / "courses"


def load(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def main():
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except Exception:
            pass
    courses = []
    for cdir in sorted(p for p in COURSES_DIR.iterdir() if p.is_dir()):
        course = load(cdir / "course.json")
        lessons = [load(p) for p in sorted((cdir / "lessons").glob("l*.json"))]
        lessons.sort(key=lambda l: l["n"])
        for l in lessons:
            total = sum(t["min"] for t in l["timing"])
            prac = sum(t["min"] for t in l["timing"] if t["type"] == "practice")
            if total != 90:
                print(f"אזהרה: מפגש {l['n']} מסתכם ב-{total} דקות ולא 90", file=sys.stderr)
            if prac * 2 < total:
                print(f"אזהרה: מפגש {l['n']} כולל פחות מ-50% תרגול", file=sys.stderr)
            kinds = [e["kind"] for e in l["exercises"]]
            if "class" not in kinds or "home" not in kinds:
                print(f"אזהרה: במפגש {l['n']} חסר תרגיל כיתה או תרגיל בית", file=sys.stderr)
        course["lessons"] = lessons
        courses.append(course)
    payload = json.dumps({"courses": courses}, ensure_ascii=False).replace("</", "<\\/")
    html = (ROOT / "template.html").read_text(encoding="utf-8").replace("/*__DATA__*/", payload)
    out = ROOT / "dist" / "course-portal.html"
    out.parent.mkdir(exist_ok=True)
    out.write_text(html, encoding="utf-8")
    print(f"נבנה: {out} ({out.stat().st_size // 1024} KB, {len(courses)} קורסים)")


if __name__ == "__main__":
    main()
