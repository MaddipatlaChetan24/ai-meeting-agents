import os
import tempfile
from fpdf import FPDF
from datetime import datetime


def _timestamp() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M")


# ─── TXT Export ───────────────────────────────────────────────────────────────

def export_to_txt(
    title: str,
    summary: str,
    actions: str,
    decisions: str,
    questions: str,
    transcript: str,
) -> str:
    """Export meeting data to a formatted .txt file. Returns the file path."""
    lines = []
    lines.append("=" * 60)
    lines.append(f"  {title}")
    lines.append(f"  Generated on {_timestamp()}")
    lines.append("=" * 60)
    lines.append("")

    sections = [
        ("MEETING SUMMARY", summary),
        ("ACTION ITEMS", actions),
        ("KEY DECISIONS", decisions),
        ("OPEN QUESTIONS", questions),
        ("FULL TRANSCRIPT", transcript),
    ]

    for heading, body in sections:
        lines.append(f"{'─' * 60}")
        lines.append(f"  {heading}")
        lines.append(f"{'─' * 60}")
        lines.append(body.strip() if body else "(none)")
        lines.append("")

    content = "\n".join(lines)

    tmp = tempfile.NamedTemporaryFile(
        delete=False, suffix=".txt", prefix="meeting_", mode="w", encoding="utf-8"
    )
    tmp.write(content)
    tmp.close()
    return tmp.name


# ─── PDF Export ───────────────────────────────────────────────────────────────

class _MeetingPDF(FPDF):
    """Custom PDF with header/footer for a professional look."""

    def __init__(self, title: str):
        super().__init__()
        self._title = title

    def header(self):
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(100, 100, 100)
        self.cell(0, 8, self._title, new_x="LMARGIN", new_y="NEXT", align="L")
        self.set_draw_color(60, 130, 240)
        self.set_line_width(0.5)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(4)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}}", align="C")

    def section_title(self, title: str):
        self.set_font("Helvetica", "B", 13)
        self.set_text_color(30, 80, 180)
        self.cell(0, 10, title, new_x="LMARGIN", new_y="NEXT")
        self.set_draw_color(30, 80, 180)
        self.set_line_width(0.3)
        self.line(10, self.get_y(), 90, self.get_y())
        self.ln(3)

    def section_body(self, text: str):
        self.set_font("Helvetica", "", 10)
        self.set_text_color(40, 40, 40)
        # multi_cell handles long text with automatic line-wrapping
        self.multi_cell(0, 5.5, text.strip() if text else "(none)")
        self.ln(4)


def export_to_pdf(
    title: str,
    summary: str,
    actions: str,
    decisions: str,
    questions: str,
    transcript: str,
) -> str:
    """Export meeting data to a styled PDF. Returns the file path."""
    pdf = _MeetingPDF(title)
    pdf.alias_nb_pages()
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.add_page()

    # ── Cover title ──
    pdf.set_font("Helvetica", "B", 22)
    pdf.set_text_color(25, 25, 25)
    pdf.ln(10)
    pdf.multi_cell(0, 12, title, align="C")
    pdf.ln(2)
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(120, 120, 120)
    pdf.cell(0, 8, f"Generated on {_timestamp()}", align="C",
             new_x="LMARGIN", new_y="NEXT")
    pdf.ln(10)

    # ── Sections ──
    sections = [
        ("Meeting Summary", summary),
        ("Action Items", actions),
        ("Key Decisions", decisions),
        ("Open Questions", questions),
        ("Full Transcript", transcript),
    ]

    for heading, body in sections:
        pdf.section_title(heading)
        pdf.section_body(body)

    tmp = tempfile.NamedTemporaryFile(
        delete=False, suffix=".pdf", prefix="meeting_"
    )
    tmp.close()
    pdf.output(tmp.name)
    return tmp.name
