"""
Generates downloadable reports from a completed scan result, in JSON, CSV,
or PDF. Called by GET /api/scans/<id>/report?format=...
"""
import csv
import io
import json

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_LEFT, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak,
    KeepTogether, HRFlowable,
)


def to_json(result: dict) -> bytes:
    return json.dumps(result, indent=2).encode("utf-8")


def to_csv(result: dict) -> bytes:
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow([
        "Finding", "Endpoint", "Parameter", "Detection",
        "Severity", "Confidence", "Status",
    ])
    for f in result.get("findings", []):
        writer.writerow([
            f.get("title"), f.get("endpoint"), f.get("parameter"),
            f.get("detection"), f.get("severity"),
            f"{f.get('confidence')}%", f.get("status"),
        ])
    return buffer.getvalue().encode("utf-8")


# ---------------------------------------------------------------------------
# PDF colour constants
# ---------------------------------------------------------------------------

_PDF_INK = colors.HexColor("#20272D")        # primary text
_PDF_SECONDARY = colors.HexColor("#53606A")  # secondary text
_PDF_MUTED = colors.HexColor("#737E86")      # muted labels / footer
_PDF_BORDER = colors.HexColor("#D9DEE2")     # light border
_PDF_DIVIDER = colors.HexColor("#E9ECEF")    # very light divider
_PDF_SOFT = colors.HexColor("#F5F7F8")       # soft grey background
_PDF_GREEN = colors.HexColor("#337418")      # primary green
_PDF_PALE_GREEN = colors.HexColor("#EDF5E9") # optional pale green
_PDF_WHITE = colors.white

_SEVERITY_COLORS = {
    "High": colors.HexColor("#A94442"),
    "Medium": colors.HexColor("#A66A12"),
    "Low": colors.HexColor("#337418"),
    "Informational": colors.HexColor("#52738A"),
}

_PRIORITY_COLORS = {
    "High": colors.HexColor("#A94442"),
    "Medium": colors.HexColor("#A66A12"),
    "Low": colors.HexColor("#337418"),
}


# ---------------------------------------------------------------------------
# Styles
# ---------------------------------------------------------------------------

def _build_styles():
    base = getSampleStyleSheet()
    styles = {}

    styles["brand"] = ParagraphStyle(
        "Brand", parent=base["Normal"],
        fontName="Helvetica-Bold", fontSize=13, leading=15,
        textColor=_PDF_GREEN,
    )
    styles["brand_subtitle"] = ParagraphStyle(
        "BrandSubtitle", parent=base["Normal"],
        fontName="Helvetica", fontSize=9, leading=11,
        textColor=_PDF_MUTED, alignment=TA_RIGHT,
    )
    styles["title"] = ParagraphStyle(
        "ReportTitle", parent=base["Normal"],
        fontName="Times-Bold", fontSize=20, leading=23,
        textColor=_PDF_INK, spaceBefore=2, spaceAfter=0,
    )
    styles["meta_label"] = ParagraphStyle(
        "MetaLabel", parent=base["Normal"],
        fontName="Helvetica-Bold", fontSize=7.3, leading=9,
        textColor=_PDF_MUTED,
    )
    styles["meta_value"] = ParagraphStyle(
        "MetaValue", parent=base["Normal"],
        fontName="Helvetica", fontSize=8.2, leading=11,
        textColor=_PDF_INK,
    )
    styles["section_heading"] = ParagraphStyle(
        "SectionHeading", parent=base["Normal"],
        fontName="Helvetica-Bold", fontSize=11, leading=14,
        textColor=_PDF_INK, spaceBefore=10, spaceAfter=6,
    )
    styles["summary_label"] = ParagraphStyle(
        "SummaryLabel", parent=base["Normal"],
        fontName="Helvetica-Bold", fontSize=7.3, leading=9,
        textColor=_PDF_MUTED,
    )
    styles["summary_value"] = ParagraphStyle(
        "SummaryValue", parent=base["Normal"],
        fontName="Helvetica-Bold", fontSize=12, leading=15,
        textColor=_PDF_INK,
    )
    styles["finding_index"] = ParagraphStyle(
        "FindingIndex", parent=base["Normal"],
        fontName="Helvetica-Bold", fontSize=7.5, leading=10,
        textColor=_PDF_MUTED,
    )
    styles["finding_title"] = ParagraphStyle(
        "FindingTitle", parent=base["Normal"],
        fontName="Helvetica-Bold", fontSize=11, leading=14,
        textColor=_PDF_INK,
    )
    styles["finding_subline"] = ParagraphStyle(
        "FindingSubline", parent=base["Normal"],
        fontName="Helvetica", fontSize=8.2, leading=11,
        textColor=_PDF_SECONDARY,
    )
    styles["kv_label"] = ParagraphStyle(
        "KVLabel", parent=base["Normal"],
        fontName="Helvetica-Bold", fontSize=7.5, leading=10,
        textColor=_PDF_MUTED,
    )
    styles["kv_value"] = ParagraphStyle(
        "KVValue", parent=base["Normal"],
        fontName="Helvetica", fontSize=8.2, leading=11,
        textColor=_PDF_INK,
    )
    styles["narrative_label"] = ParagraphStyle(
        "NarrativeLabel", parent=base["Normal"],
        fontName="Helvetica-Bold", fontSize=8, leading=10,
        textColor=_PDF_SECONDARY, spaceBefore=6, spaceAfter=2,
    )
    styles["narrative_body"] = ParagraphStyle(
        "NarrativeBody", parent=base["Normal"],
        fontName="Times-Roman", fontSize=9.5, leading=13.2,
        textColor=_PDF_INK,
    )
    styles["evidence_label"] = ParagraphStyle(
        "EvidenceLabel", parent=base["Normal"],
        fontName="Helvetica-Bold", fontSize=8, leading=10,
        textColor=_PDF_SECONDARY,
    )
    styles["evidence_value"] = ParagraphStyle(
        "EvidenceValue", parent=base["Normal"],
        fontName="Helvetica", fontSize=8.2, leading=11,
        textColor=_PDF_INK,
    )
    styles["evidence_excerpt"] = ParagraphStyle(
        "EvidenceExcerpt", parent=base["Normal"],
        fontName="Times-Italic", fontSize=8.7, leading=12,
        textColor=_PDF_SECONDARY, spaceBefore=4,
    )
    styles["reco_heading"] = ParagraphStyle(
        "RecoHeading", parent=base["Normal"],
        fontName="Helvetica-Bold", fontSize=9.5, leading=12,
        textColor=_PDF_INK, spaceBefore=8, spaceAfter=4,
    )
    styles["reco_title"] = ParagraphStyle(
        "RecoTitle", parent=base["Normal"],
        fontName="Times-Roman", fontSize=9, leading=12.5,
        textColor=_PDF_INK,
    )
    styles["limitations_heading"] = ParagraphStyle(
        "LimitationsHeading", parent=base["Normal"],
        fontName="Helvetica-Bold", fontSize=8.5, leading=11,
        textColor=_PDF_INK, spaceAfter=2,
    )
    styles["limitations_body"] = ParagraphStyle(
        "LimitationsBody", parent=base["Normal"],
        fontName="Times-Italic", fontSize=8.5, leading=11.5,
        textColor=_PDF_SECONDARY,
    )
    styles["footer"] = ParagraphStyle(
        "Footer", parent=base["Normal"],
        fontName="Helvetica", fontSize=7.5, leading=9,
        textColor=_PDF_MUTED, alignment=TA_RIGHT,
    )
    styles["no_findings"] = ParagraphStyle(
        "NoFindings", parent=base["Normal"],
        fontName="Times-Roman", fontSize=9.5, leading=13.2,
        textColor=_PDF_INK,
    )
    return styles


# ---------------------------------------------------------------------------
# Layout helpers
# ---------------------------------------------------------------------------

def _thin_rule(color=_PDF_BORDER, width=0.6):
    return HRFlowable(width="100%", thickness=width, color=color,
                       spaceBefore=2, spaceAfter=2, lineCap="round")


def _header_block(result: dict, styles: dict):
    flow = []
    brand_row = Table(
        [[Paragraph("SQLyse", styles["brand"]),
          Paragraph("SECURITY ASSESSMENT", styles["brand_subtitle"])]],
        colWidths=[9 * cm, 8.1 * cm],
    )
    brand_row.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))
    flow.append(brand_row)
    flow.append(Spacer(1, 0.15 * cm))
    flow.append(Paragraph("Application Security Scan Report", styles["title"]))
    flow.append(Spacer(1, 0.25 * cm))
    flow.append(HRFlowable(width="100%", thickness=1.4, color=_PDF_GREEN,
                            spaceBefore=0, spaceAfter=10, lineCap="round"))

    meta_cells = [
        ("SCAN ID", result.get("scanId", "N/A")),
        ("TARGET URL", result.get("targetUrl", "N/A")),
        ("STARTED", result.get("startedAt") or result.get("started") or "N/A"),
        ("COMPLETED / DURATION", _completed_and_duration(result)),
    ]
    stack = []
    for i, (label, value) in enumerate(meta_cells):
        stack.append([Paragraph(label, styles["meta_label"]),
                      Paragraph(str(value), styles["meta_value"])])
    meta_grid = Table(stack, colWidths=[4.2 * cm, 12.9 * cm])
    meta_grid.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LINEBELOW", (0, 0), (-1, -2), 0.5, _PDF_DIVIDER),
    ]))
    flow.append(meta_grid)
    return flow


def _completed_and_duration(result: dict) -> str:
    completed = result.get("completedAt") or result.get("completed") or "N/A"
    duration = result.get("duration") or result.get("durationSeconds")
    if duration is None:
        return str(completed)
    if isinstance(duration, (int, float)):
        duration = f"{duration} seconds"
    return f"{completed} / {duration}"


def _summary_table(result: dict, styles: dict):
    findings = result.get("findings", [])
    metrics = [
        ("PAGES SCANNED", str(result.get("pagesScanned", 0))),
        ("FORMS DISCOVERED", str(result.get("formsDiscovered", 0))),
        ("PARAMETERS TESTED", str(result.get("parametersTested", 0))),
        ("FINDINGS COUNT", str(len(findings))),
        ("OVERALL RISK", result.get("overallRisk", "Low")),
    ]
    label_row = [Paragraph(m[0], styles["summary_label"]) for m in metrics]

    risk = result.get("overallRisk", "Low")
    risk_color = _SEVERITY_COLORS.get(risk, _PDF_INK)
    value_row = []
    for i, m in enumerate(metrics):
        if i == len(metrics) - 1:
            v_style = ParagraphStyle(
                "RiskValue", parent=styles["summary_value"], textColor=risk_color,
            )
            value_row.append(Paragraph(m[1], v_style))
        else:
            value_row.append(Paragraph(m[1], styles["summary_value"]))

    table = Table([label_row, value_row], colWidths=[3.42 * cm] * 5)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), _PDF_SOFT),
        ("BOX", (0, 0), (-1, -1), 0.6, _PDF_BORDER),
        ("INNERGRID", (0, 0), (-1, -1), 0.4, _PDF_BORDER),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
    ]))
    return table


def _severity_badge(severity: str, styles: dict):
    color = _SEVERITY_COLORS.get(severity, _PDF_SECONDARY)
    style = ParagraphStyle(
        "SeverityBadge", parent=styles["finding_index"],
        fontName="Helvetica-Bold", fontSize=8, textColor=color,
        alignment=TA_RIGHT,
    )
    return Paragraph((severity or "").upper(), style)


def _finding_heading_and_metadata(f: dict, index: int, styles: dict):
    flow = [_thin_rule(color=_PDF_GREEN, width=1.1)]
    flow.append(Spacer(1, 0.15 * cm))

    header_row = Table(
        [[Paragraph(f"FINDING {index}", styles["finding_index"]),
          _severity_badge(f.get("severity"), styles)]],
        colWidths=[13.5 * cm, 3.6 * cm],
    )
    header_row.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))
    flow.append(header_row)
    flow.append(Paragraph(f.get("title", ""), styles["finding_title"]))

    subline = f"Confidence {f.get('confidence', 0)}%  \u2022  Status {f.get('status', 'N/A')}"
    flow.append(Paragraph(subline, styles["finding_subline"]))
    flow.append(Spacer(1, 0.2 * cm))

    meta_rows = [
        ("Endpoint", f.get("endpoint", "N/A")),
        ("HTTP method", f.get("httpMethod") or f.get("method", "N/A")),
        ("Parameter", f.get("parameter", "N/A")),
        ("Detection", f.get("detection", "N/A")),
        ("Response status comparison", f.get("responseStatusComparison", "N/A")),
        ("Response length difference", f.get("responseLengthDifference", "N/A")),
        ("Database error family", f.get("databaseErrorFamily", "N/A")),
    ]
    grid = []
    for label, value in meta_rows:
        grid.append([Paragraph(label, styles["kv_label"]),
                     Paragraph(str(value), styles["kv_value"])])
    meta_table = Table(grid, colWidths=[4.0 * cm, 13.1 * cm])
    meta_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), _PDF_SOFT),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LINEBELOW", (0, 0), (-1, -2), 0.4, _PDF_DIVIDER),
    ]))
    flow.append(meta_table)
    return flow


def _finding_details(f: dict, styles: dict):
    flow = []
    narrative = [
        ("Observed behaviour", f.get("observed", "")),
        ("Risk", f.get("risk", "")),
        ("Potential impact", f.get("impact", "")),
        ("Verification guidance", f.get("verification", "")),
    ]
    for label, text in narrative:
        if not text:
            continue
        flow.append(Paragraph(label, styles["narrative_label"]))
        flow.append(Paragraph(text, styles["narrative_body"]))

    evidence = f.get("evidence", {})
    baseline = evidence.get("baseline", {}) if evidence else {}
    modified = evidence.get("modified", {}) if evidence else {}
    excerpt = (evidence.get("sanitizedExcerpt") if evidence else None) or f.get("sanitizedExcerpt")

    if evidence or excerpt:
        evidence_flow = [Paragraph("Evidence", styles["narrative_label"])]
        rows = []
        if baseline:
            rows.append([Paragraph("Baseline response", styles["evidence_label"]),
                         Paragraph(f"{baseline.get('status', 'N/A')} \u00b7 {baseline.get('length', 'N/A')}",
                                   styles["evidence_value"])])
        if modified:
            rows.append([Paragraph("Modified response", styles["evidence_label"]),
                         Paragraph(f"{modified.get('status', 'N/A')} \u00b7 {modified.get('length', 'N/A')}",
                                   styles["evidence_value"])])
        evidence_inner = []
        if rows:
            ev_table = Table(rows, colWidths=[4.0 * cm, 13.1 * cm])
            ev_table.setStyle(TableStyle([
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("TOPPADDING", (0, 0), (-1, -1), 2),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
            ]))
            evidence_inner.append(ev_table)
        if excerpt:
            evidence_inner.append(Paragraph("Sanitised excerpt", styles["evidence_label"]))
            evidence_inner.append(Paragraph(excerpt, styles["evidence_excerpt"]))

        box = Table([[evidence_inner]], colWidths=[17.1 * cm])
        box.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), _PDF_SOFT),
            ("BOX", (0, 0), (-1, -1), 0.5, _PDF_BORDER),
            ("LINEBEFORE", (0, 0), (0, -1), 1.5, _PDF_GREEN),
            ("LEFTPADDING", (0, 0), (-1, -1), 10),
            ("RIGHTPADDING", (0, 0), (-1, -1), 10),
            ("TOPPADDING", (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ]))
        flow.append(KeepTogether([Spacer(1, 0.1 * cm)] + evidence_flow + [box]))

    recs = f.get("recommendations", [])
    if recs:
        reco_flow = [Paragraph("Recommendations", styles["reco_heading"])]
        first_item = _recommendation_item(recs[0], 1, styles)
        flow.append(KeepTogether(reco_flow + first_item))
        for i, r in enumerate(recs[1:], start=2):
            flow.extend(_recommendation_item(r, i, styles))

    flow.append(Spacer(1, 0.35 * cm))
    return flow


def _recommendation_item(r: dict, number: int, styles: dict):
    priority = r.get("priority", "")
    color = _PRIORITY_COLORS.get(priority, _PDF_SECONDARY)
    priority_style = ParagraphStyle(
        "RecoPriority", parent=styles["kv_label"], fontSize=7.5, textColor=color,
    )
    title_line = (
        f"<b>{number}. {r.get('title', '')}</b>"
        + (f"  <font color='{color.hexval()}'><b>{priority.upper()}</b></font>" if priority else "")
    )
    return [
        Paragraph(title_line, styles["reco_title"]),
        Paragraph(r.get("explanation", ""), styles["reco_title"]),
        Spacer(1, 0.15 * cm),
    ]


def _limitations_block(styles: dict):
    text = Paragraph(
        "Automated findings require manual verification, and the absence of "
        "findings does not guarantee security.",
        styles["limitations_body"],
    )
    inner = [Paragraph("Limitations", styles["limitations_heading"]), text]
    box = Table([[inner]], colWidths=[17.1 * cm])
    box.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), _PDF_SOFT),
        ("BOX", (0, 0), (-1, -1), 0.5, _PDF_BORDER),
        ("LINEBEFORE", (0, 0), (0, -1), 1.5, _PDF_GREEN),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    return KeepTogether([Spacer(1, 0.4 * cm), box])


def _draw_footer(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(_PDF_DIVIDER)
    canvas.setLineWidth(0.5)
    y = 1.15 * cm
    canvas.line(1.7 * cm, y, A4[0] - 1.7 * cm, y)
    canvas.setFont("Helvetica", 7.5)
    canvas.setFillColor(_PDF_MUTED)
    canvas.drawRightString(
        A4[0] - 1.7 * cm, y - 0.35 * cm,
        f"SQLyse Security Report \u2022 Page {doc.page}",
    )
    canvas.restoreState()


def to_pdf(result: dict) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        topMargin=1.45 * cm, bottomMargin=1.55 * cm,
        leftMargin=1.7 * cm, rightMargin=1.7 * cm,
        title="SQLyse Application Security Scan Report",
        author="SQLyse",
    )
    styles = _build_styles()

    story = []
    story.extend(_header_block(result, styles))
    story.append(Spacer(1, 0.35 * cm))
    story.append(Paragraph("Scan summary", styles["section_heading"]))
    story.append(_summary_table(result, styles))
    story.append(Spacer(1, 0.3 * cm))

    findings = result.get("findings", [])
    story.append(Paragraph(f"Findings ({len(findings)})", styles["section_heading"]))

    if not findings:
        story.append(Paragraph(
            "No potential SQL injection issues were detected.", styles["no_findings"],
        ))
    else:
        for i, f in enumerate(findings, start=1):
            heading_flow = _finding_heading_and_metadata(f, i, styles)
            story.append(KeepTogether(heading_flow))
            story.extend(_finding_details(f, styles))

    story.append(_limitations_block(styles))

    doc.build(story, onFirstPage=_draw_footer, onLaterPages=_draw_footer)
    return buffer.getvalue()


def generate(result: dict, fmt: str) -> tuple[bytes, str, str]:
    """Returns (bytes, mimetype, filename)."""
    scan_id = result.get("scanId", "scan")
    if fmt == "json":
        return to_json(result), "application/json", f"{scan_id}.json"
    if fmt == "csv":
        return to_csv(result), "text/csv", f"{scan_id}.csv"
    if fmt == "pdf":
        return to_pdf(result), "application/pdf", f"{scan_id}.pdf"
    raise ValueError(f"Unsupported report format: {fmt}")