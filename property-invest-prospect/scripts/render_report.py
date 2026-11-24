#!/usr/bin/env python3
"""Render a sourced property assessment JSON as an A4 PDF."""

import argparse
from html import escape
import json
from pathlib import Path
import subprocess
import sys
from urllib.parse import urlsplit

from reportlab.graphics.shapes import Drawing, Line, Polygon, Rect, String
from reportlab.lib.colors import HexColor, white
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    KeepTogether, LongTable, PageBreak, Paragraph, SimpleDocTemplate,
    Spacer, Table, TableStyle,
)

INK = HexColor("#172C31")
TEAL = HexColor("#18655F")
MUTED = HexColor("#486065")
PALE = HexColor("#EDF4F1")
WARM = HexColor("#FAF0E3")
RULE = HexColor("#D4E2DF")
MARGIN = 47
WIDTH = A4[0] - 2 * MARGIN - 12
FONT_ROOT = Path("/System/Library/Fonts")


def register_fonts(args):
    normal = args.font or FONT_ROOT / "STHeiti Light.ttc"
    bold = args.bold_font or (normal if args.font else FONT_ROOT / "STHeiti Medium.ttc")
    if not normal.is_file() or not bold.is_file():
        raise ValueError("Use --font and optionally --bold-font to supply embedded TrueType CJK fonts.")
    for name, path, default in (("Body", normal, not args.font),
                                ("Heading", bold, not args.font and not args.bold_font)):
        pdfmetrics.registerFont(TTFont(name, str(path), subfontIndex=1 if default else 0))


def paragraph(value, size=11, leading=None, color=INK, bold=False):
    style = ParagraphStyle(
        "report", fontName="Heading" if bold else "Body", fontSize=size,
        leading=leading or size * 1.54, textColor=color, wordWrap="CJK",
    )
    return Paragraph(escape(str(value)).replace("\n", "<br/>"), style)


def grid(headers, rows, weights=None):
    if not headers or any(len(row) != len(headers) for row in rows):
        raise ValueError("Every table row must match the nonempty headers.")
    weights = weights or [1] * len(headers)
    if len(weights) != len(headers) or any(w <= 0 for w in weights):
        raise ValueError("Table weights must be positive and match the number of columns.")
    entries = [[paragraph(text, 9.6, 14, white, True) for text in headers]]
    entries += [[paragraph(cell, 9.7, 14.4) for cell in row] for row in rows]
    table = LongTable(entries, colWidths=[WIDTH * w / sum(weights) for w in weights],
                      repeatRows=1, hAlign="LEFT")
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), INK),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [white, PALE]),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING", (0, 0), (-1, -1), 9),
        ("RIGHTPADDING", (0, 0), (-1, -1), 9),
        ("LINEBELOW", (0, -1), (-1, -1), .65, RULE),
    ]))
    return table


def box(title, body, fill=PALE, color=INK):
    lines = [paragraph(title, 13, 19, color, True), Spacer(1, 4),
             paragraph(body, 11, 17, color)]
    table = Table([[lines]], colWidths=[WIDTH], hAlign="LEFT")
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), fill),
        ("LEFTPADDING", (0, 0), (-1, -1), 14),
        ("RIGHTPADDING", (0, 0), (-1, -1), 14),
        ("TOPPADDING", (0, 0), (-1, -1), 12),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
    ]))
    return table


def source_line(key, sources):
    source = sources[key]
    url = source["url"]
    parts = urlsplit(url)
    if parts.scheme not in ("https", "http") or not parts.netloc:
        raise ValueError(f"Invalid source URL for {key}")
    label = escape(f"[{key}] {source['label']}")
    html = f'<link href="{escape(url, quote=True)}" color="#18655F">{label}</link>'
    style = ParagraphStyle("source", fontName="Body", fontSize=9, leading=14,
                           textColor=TEAL, wordWrap="CJK")
    return Paragraph(html, style)


def scenario_data(block):
    args = [sys.executable, str(Path(__file__).with_name("cashflow.py"))]
    for key in ("price", "weekly-rent", "rates", "deposit-percent", "rented-weeks",
                "management-percent", "annual-fixed-costs"):
        if key in block:
            value = block[key]
            args += ["--" + key, *map(str, value if isinstance(value, list) else [value])]
    return json.loads(subprocess.check_output(args, text=True))


def money(amount, currency, digits=2):
    sign = "-" if amount < 0 else ""
    return f"{sign}{currency}{abs(amount):,.{digits}f}"


def cashflow(block, currency):
    data = scenario_data(block)
    a = data["assumptions"]
    scenarios = data["scenarios"]
    group_keys = ("purchase_price", "weekly_rent", "gross_yield_percent")
    groups = {}
    for result in scenarios:
        group = tuple(result[key] for key in group_keys)
        groups.setdefault(group, []).append(result)
    headers = ["利率", "年利息", "年总支出", "年净现金流", "月均净现金流", "保本周租", "转正周租"]
    elements = [paragraph(
        f"首付 {a['deposit_percent']:g}%，只付利息。每年按 {a['paid_weeks_per_year']:g} 周实收租金，"
        f"管理费 {a['management_percent']:g}%，其他年度持有成本 {money(a['annual_fixed_holding_costs'], currency, 0)}。"
        "现金流为税前，印花税、交割和一次性工程单列。", 10.5, 16),
        Spacer(1, 10),
    ]
    for (price, rent, gross_yield), items in groups.items():
        table_rows = []
        for s in items:
            fields = ("annual_interest", "annual_total_outgoings", "annual_cash_flow",
                      "monthly_cash_flow", "weekly_break_even_rent",
                      "weekly_rent_for_positive_cash_flow_whole_dollars")
            values = [money(s[k], currency, 0 if index == 5 else 2)
                      for index, k in enumerate(fields)]
            table_rows.append([f"{s['interest_rate_percent']:g}%", *values])
        elements += [
            paragraph(f"买入 {money(price, currency, 0)}  /  周租 {money(rent, currency, 0)}"
                      f"  /  毛收益率 {gross_yield:.2f}%", 11.4, 17, TEAL, True),
            Spacer(1, 5),
            grid(headers, table_rows, [.56, 1, 1.06, 1.12, 1.10, .87, .84]),
            Spacer(1, 12),
        ]
    return elements


def parcel_diagram(block):
    points = block["points"]
    if len(points) < 3:
        raise ValueError("A parcel diagram needs at least three distinct points.")
    xs, ys = zip(*points)
    w, h = max(xs) - min(xs), max(ys) - min(ys)
    if not w or not h:
        raise ValueError("Parcel diagram spans must be positive on both axes.")
    scale = min(260 / w, 77 / h)
    transformed = [(72 + (x - min(xs)) * scale, 18 + (y - min(ys)) * scale)
                   for x, y in points]
    diagram = Drawing(WIDTH, 119)
    diagram.add(Rect(0, 0, WIDTH, 119, fillColor=PALE, strokeColor=None))
    diagram.add(Polygon([v for point in transformed for v in point],
                        fillColor=white, strokeColor=TEAL, strokeWidth=1.5))
    first, last = (transformed[index] for index in block["front_edge"])
    diagram.add(Line(*first, *last, strokeColor=TEAL, strokeWidth=3.5))
    diagram.add(Line(349, 34, 367, 34, strokeColor=TEAL, strokeWidth=3.5))
    diagram.add(String(374, 31, "临街边", fontName="Heading", fontSize=10, fillColor=TEAL))
    diagram.add(Line(WIDTH-31, 62, WIDTH-31, 86, strokeColor=TEAL, strokeWidth=1.1))
    diagram.add(Polygon([WIDTH-34, 85, WIDTH-31, 92, WIDTH-28, 85],
                        fillColor=TEAL, strokeColor=TEAL))
    diagram.add(String(WIDTH-36, 99, "N", fontName="Helvetica", fontSize=9, fillColor=TEAL))
    return diagram


def render_blocks(blocks, currency):
    for block in blocks:
        kind = block["type"]
        if kind == "table":
            yield grid(block["headers"], block["rows"], block.get("weights"))
        elif kind == "callout":
            yield box(block["title"], block["text"], WARM)
        elif kind == "cashflow":
            yield from cashflow(block, currency)
        elif kind == "parcel":
            yield parcel_diagram(block)
            yield Spacer(1, 5)
            yield paragraph(block["caption"], 9.4, 14, MUTED)
        elif kind == "text":
            if block.get("title"):
                yield KeepTogether([
                    paragraph(block["title"], 13, 19, INK, True),
                    Spacer(1, 4),
                    paragraph(block["text"]),
                ])
            else:
                yield paragraph(block["text"], color=MUTED if block.get("note") else INK)
        else:
            raise ValueError(f"Unknown report block type: {kind}")
        yield Spacer(1, 10)


def render(report, output):
    doc = SimpleDocTemplate(
        str(output), pagesize=A4, leftMargin=MARGIN, rightMargin=MARGIN,
        topMargin=70, bottomMargin=57, title="房产投资尽调 | " + report["address"],
        author="Property Invest Prospect",
    )

    def chrome(canvas, doc):
        width, height = A4
        canvas.setStrokeColor(RULE)
        for y in (height - 54, 48):
            canvas.line(MARGIN + 6, y, width - MARGIN - 6, y)
        canvas.setFillColor(TEAL)
        canvas.setFont("Heading", 9.2)
        canvas.drawString(MARGIN + 6, height - 43, "PROPERTY INVEST PROSPECT")
        canvas.drawRightString(width - MARGIN - 6, height - 43, "房产投资尽调")
        canvas.setFont("Body", 8.8)
        canvas.setFillColor(MUTED)
        canvas.drawString(MARGIN + 6, 32, report["assessment_date"])
        canvas.drawRightString(width - MARGIN - 6, 32, f"{doc.page:02d}")

    story = [
        Spacer(1, 17),
        paragraph("住宅投资评估", 31, 39, TEAL, True),
        Spacer(1, 10),
        paragraph(report["address"], 28, 35, INK, True),
        Spacer(1, 9),
        paragraph(report["subtitle"], 12, 19, MUTED),
        Spacer(1, 26),
        grid(["核心指标", "本次评估"], report["summary"], [1, 2.15]),
        Spacer(1, 20),
        box(report["verdict"]["title"], report["verdict"]["text"]),
        Spacer(1, 20),
        paragraph("报告内容", 12, 18, TEAL, True),
        Spacer(1, 6),
    ]
    for index, section in enumerate(report["sections"], start=1):
        story.append(paragraph(f"{index:02d}  {section['title']}", 10.4, 16, MUTED))
    for index, section in enumerate(report["sections"], start=1):
        story += [PageBreak(), paragraph(f"{index:02d}  {section['title']}", 25, 33, INK, True),
                  Spacer(1, 13)]
        if section.get("intro"):
            story.extend([paragraph(section["intro"], 11, 17, MUTED), Spacer(1, 12)])
        story.extend(render_blocks(section["blocks"], report.get("currency_symbol", "$")))
        if section.get("sources"):
            story.extend([paragraph("本节来源", 10, 15, TEAL, True), Spacer(1, 2)])
            story.extend(source_line(key, report["sources"]) for key in section["sources"])
    doc.build(story, onFirstPage=chrome, onLaterPages=chrome)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("report_json", type=Path)
    parser.add_argument("output_pdf", type=Path)
    parser.add_argument("--font", type=Path, help="TrueType font with Chinese glyphs.")
    parser.add_argument("--bold-font", type=Path, help="Optional bold TrueType font.")
    args = parser.parse_args()
    register_fonts(args)
    with args.report_json.open(encoding="utf-8") as file:
        report = json.load(file)
    render(report, args.output_pdf)


if __name__ == "__main__":
    main()
