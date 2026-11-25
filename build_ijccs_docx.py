"""Build the IJCCS Word manuscript from MANUSCRIPT_MASTER.md."""
from __future__ import annotations

import re
from pathlib import Path

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "paper" / "MANUSCRIPT_MASTER.md"
OUTPUT = ROOT / "paper" / "MANUSCRIPT_MASTER.docx"


def set_cell_shading(cell, fill: str) -> None:
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:fill"), fill)
    tc_pr.append(shd)


def set_repeat_table_header(row) -> None:
    tr_pr = row._tr.get_or_add_trPr()
    repeat = OxmlElement("w:tblHeader")
    repeat.set(qn("w:val"), "true")
    tr_pr.append(repeat)


def set_run_font(run, size: float = 11, bold: bool | None = None, italic: bool | None = None) -> None:
    run.font.name = "Times New Roman"
    run._element.rPr.rFonts.set(qn("w:eastAsia"), "Times New Roman")
    run.font.size = Pt(size)
    if bold is not None:
        run.bold = bold
    if italic is not None:
        run.italic = italic


def add_inline(paragraph, text: str) -> None:
    token = re.compile(r"(\*\*.+?\*\*|(?<!\*)\*[^*]+\*|`[^`]+`|\[[^\]]+\]\([^)]+\))")
    cursor = 0
    for match in token.finditer(text):
        if match.start() > cursor:
            paragraph.add_run(text[cursor:match.start()])
        value = match.group(0)
        if value.startswith("**"):
            run = paragraph.add_run(value[2:-2])
            run.bold = True
        elif value.startswith("*"):
            run = paragraph.add_run(value[1:-1])
            run.italic = True
        elif value.startswith("`"):
            paragraph.add_run(value[1:-1])
        else:
            link = re.fullmatch(r"\[([^\]]+)\]\(([^)]+)\)", value)
            paragraph.add_run(f"{link.group(1)} ({link.group(2)})")
        cursor = match.end()
    if cursor < len(text):
        paragraph.add_run(text[cursor:])


def add_table(document: Document, rows: list[list[str]]) -> None:
    if len(rows) < 2:
        return
    table = document.add_table(rows=1, cols=len(rows[0]))
    table.style = "Table Grid"
    table.autofit = True
    for index, value in enumerate(rows[0]):
        cell = table.rows[0].cells[index]
        cell.text = value
        cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
        set_cell_shading(cell, "D9E2F3")
        for paragraph in cell.paragraphs:
            paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
            for run in paragraph.runs:
                set_run_font(run, 8.5, bold=True)
    set_repeat_table_header(table.rows[0])
    for row_values in rows[1:]:
        cells = table.add_row().cells
        for index, value in enumerate(row_values):
            cells[index].text = value
            cells[index].vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
            for paragraph in cells[index].paragraphs:
                for run in paragraph.runs:
                    set_run_font(run, 8.5)
    document.add_paragraph().paragraph_format.space_after = Pt(1)


def configure(document: Document) -> None:
    section = document.sections[0]
    section.page_width = Inches(8.5)
    section.page_height = Inches(11)
    section.top_margin = Inches(1.1811)
    section.bottom_margin = Inches(1.1811)
    section.left_margin = Inches(1.1811)
    section.right_margin = Inches(1.1811)

    normal = document.styles["Normal"]
    normal.font.name = "Times New Roman"
    normal._element.rPr.rFonts.set(qn("w:eastAsia"), "Times New Roman")
    normal.font.size = Pt(11)
    normal.paragraph_format.line_spacing = 1
    normal.paragraph_format.space_after = Pt(5)
    normal.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

    for name, size in (("Heading 1", 12), ("Heading 2", 11), ("Heading 3", 11)):
        style = document.styles[name]
        style.font.name = "Times New Roman"
        style._element.rPr.rFonts.set(qn("w:eastAsia"), "Times New Roman")
        style.font.size = Pt(size)
        style.font.bold = True
        style.paragraph_format.keep_with_next = True
        style.paragraph_format.space_before = Pt(9)
        style.paragraph_format.space_after = Pt(4)

    header = section.header.paragraphs[0]
    header.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    run = header.add_run("IJCCS manuscript draft")
    set_run_font(run, 8, italic=True)
    footer = section.footer.paragraphs[0]
    footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
    field = OxmlElement("w:fldSimple")
    field.set(qn("w:instr"), "PAGE")
    footer._p.append(field)


def main() -> None:
    source = SOURCE.read_text(encoding="utf-8-sig")
    document = Document()
    configure(document)
    lines = source.splitlines()
    index = 0
    abstract_body = False
    while index < len(lines):
        line = lines[index].strip()
        if not line or line == "---":
            index += 1
            continue
        if line.startswith("|"):
            parsed = []
            while index < len(lines) and lines[index].strip().startswith("|"):
                cells = [cell.strip() for cell in lines[index].strip().strip("|").split("|")]
                if not all(re.fullmatch(r"[:\- ]+", cell or "-") for cell in cells):
                    parsed.append(cells)
                index += 1
            if parsed:
                width = len(parsed[0])
                add_table(document, [row[:width] + [""] * max(0, width-len(row)) for row in parsed])
            continue
        image_match = re.fullmatch(r"!\[[^\]]*\]\(([^)]+)\)", line)
        if image_match:
            image_path = (SOURCE.parent / image_match.group(1)).resolve()
            if image_path.exists():
                paragraph = document.add_paragraph()
                paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
                paragraph.add_run().add_picture(str(image_path), width=Inches(6.05))
            else:
                paragraph = document.add_paragraph(f"[Figure file missing: {image_path.name}]")
                paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
            index += 1
            continue
        if line.startswith("# "):
            paragraph = document.add_paragraph()
            paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
            paragraph.paragraph_format.space_after = Pt(14)
            run = paragraph.add_run(line[2:])
            set_run_font(run, 18, bold=True)
            index += 1
            continue
        if line.startswith("## "):
            heading = line[3:]
            paragraph = document.add_paragraph(style="Heading 1")
            add_inline(paragraph, heading)
            abstract_body = heading.strip().lower() in {"abstract", "abstrak"}
            index += 1
            continue
        if line.startswith("### "):
            paragraph = document.add_paragraph(style="Heading 2")
            add_inline(paragraph, line[4:])
            index += 1
            continue
        if line.startswith("#### "):
            paragraph = document.add_paragraph(style="Heading 3")
            add_inline(paragraph, line[5:])
            index += 1
            continue
        if line.startswith("- "):
            paragraph = document.add_paragraph(style="List Bullet")
            add_inline(paragraph, line[2:])
            index += 1
            continue
        if re.match(r"^\d+\.\s", line):
            paragraph = document.add_paragraph(style="List Number")
            add_inline(paragraph, re.sub(r"^\d+\.\s", "", line))
            index += 1
            continue
        if line.startswith("*") and line.endswith("*") and not line.startswith("**"):
            paragraph = document.add_paragraph()
            paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
            paragraph.paragraph_format.keep_together = True
            run = paragraph.add_run(line.strip("*"))
            run.italic = True
            index += 1
            continue
        paragraph = document.add_paragraph()
        paragraph.paragraph_format.keep_together = False
        if abstract_body:
            paragraph.paragraph_format.first_line_indent = Inches(0)
        if line.startswith("\\[") or line.startswith("\\]"):
            paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
        if line.startswith("[1]") or re.match(r"^\[\d+\]", line):
            paragraph.paragraph_format.left_indent = Inches(0.25)
            paragraph.paragraph_format.first_line_indent = Inches(-0.25)
            paragraph.paragraph_format.space_after = Pt(2)
        add_inline(paragraph, line)
        if abstract_body:
            for run in paragraph.runs:
                run.italic = True
            abstract_body = False
        index += 1

    document.core_properties.title = "Threshold Transfer and Category-Specific Performance in Classical Foreground Segmentation Across CDnet2014"
    document.core_properties.subject = "IJCCS submission manuscript"
    document.core_properties.keywords = "CDnet2014, foreground segmentation, threshold transfer, background subtraction"
    document.save(OUTPUT)
    print(OUTPUT)


if __name__ == "__main__":
    main()
