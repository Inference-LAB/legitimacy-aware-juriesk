import os
import re
from pathlib import Path
import latex2mathml.converter
import lxml.etree as ET
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

ROOT = Path(__file__).resolve().parents[1]
MD_PATH = ROOT / "IPM_Manuscript.md"
DOCX_PATH = ROOT / "IPM_Manuscript.docx"
FIGS_DIR = ROOT / "outputs_v2" / "figures"

# Load XSLT stylesheet for MathML to OMML
XSL_PATH = r"C:\Program Files\Microsoft Office\root\Office16\MML2OMML.XSL"
xslt = ET.parse(XSL_PATH)
transform = ET.XSLT(xslt)

def clean_latex(s):
    s = s.strip()
    s = s.replace(r"\mathbb{I}", r"\mathbf{1}")
    s = s.replace(r"\mathbb{P}", r"\mathbf{P}")
    s = s.replace(r"\mathbb{E}", r"\mathbf{E}")
    s = s.replace(r"\mathbb{R}", r"\mathbf{R}")
    s = s.replace(r"\mathbb{N}", r"\mathbf{N}")
    s = s.replace(r"\mathcal{C}", r"\mathbf{C}")
    s = s.replace(r"\mathcal{H}", r"\mathbf{H}")
    s = s.replace(r"\mathcal{X}", r"\mathbf{X}")
    s = s.replace(r"\mathcal{Y}", r"\mathbf{Y}")
    s = s.replace(r"\mathcal{D}", r"\mathbf{D}")
    s = s.replace(r"\mathcal{L}", r"\mathbf{L}")
    s = s.replace(r"\mathcal{M}", r"\mathbf{M}")
    s = s.replace(r"\mathcal{B}", r"\mathbf{B}")
    s = s.replace(r"\stackrel{\text{iid}}{\sim}", r"\sim")
    s = s.replace(r"\stackrel{\mathrm{iid}}{\sim}", r"\sim")
    s = s.replace(r"\blacksquare", r"\Box")
    s = s.replace(r"\arg\max", r"\mathrm{argmax}")
    s = s.replace(r"\max", r"\mathrm{max}")
    s = s.replace(r"\min", r"\mathrm{min}")
    s = s.replace(r"\inf", r"\mathrm{inf}")
    s = s.replace(r"\sup", r"\mathrm{sup}")
    s = s.replace(r"\binom", r"\choose")
    return s

def latex_to_omml(latex, display=False):
    cleaned = clean_latex(latex)
    try:
        mml = latex2mathml.converter.convert(cleaned, display="block" if display else "inline")
        mml_dom = ET.fromstring(mml)
        omml = transform(mml_dom).getroot()
        # Convert lxml element to docx oxml element
        xml_str = ET.tostring(omml, encoding="utf-8").decode("utf-8")
        return parse_xml(xml_str)
    except Exception as e:
        # Fallback to plain text run if math conversion fails
        return None

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('w:top', top), ('w:bottom', bottom), ('w:left', left), ('w:right', right)]:
        node = OxmlElement(m)
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def set_cell_shading(cell, color_hex="F2F2F2"):
    shading = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{color_hex}"/>')
    cell._tc.get_or_add_tcPr().append(shading)

def set_table_borders(table):
    # Professional academic 3-line booktabs borders: top thin, bottom thin, header bottom thin
    tblPr = table._tbl.tblPr
    borders = parse_xml(
        f'<w:tblBorders {nsdecls("w")}>\n'
        f'  <w:top w:val="single" w:sz="8" w:space="0" w:color="000000"/>\n'
        f'  <w:bottom w:val="single" w:sz="8" w:space="0" w:color="000000"/>\n'
        f'  <w:insideH w:val="single" w:sz="4" w:space="0" w:color="E0E0E0"/>\n'
        f'  <w:insideV w:val="none"/>\n'
        f'  <w:left w:val="none"/>\n'
        f'  <w:right w:val="none"/>\n'
        f'</w:tblBorders>'
    )
    tblPr.append(borders)

def add_formatted_paragraph(doc, text, style='Normal', space_after=6, space_before=0, line_spacing=1.15, align=WD_ALIGN_PARAGRAPH.LEFT):
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.space_before = Pt(space_before)
    p.paragraph_format.line_spacing = line_spacing
    p.alignment = align
    
    # Tokenize inline math $...$ and formatted spans
    # Regex splits by $...$
    tokens = re.split(r'(\$.*?\$)', text)
    for token in tokens:
        if token.startswith('$') and token.endswith('$') and len(token) > 1:
            eq = token[1:-1]
            omml = latex_to_omml(eq, display=False)
            if omml is not None:
                p._p.append(omml)
            else:
                run = p.add_run(token)
                run.font.name = "Cambria Math"
                run.font.size = Pt(11)
                run.italic = True
        else:
            # Process bold **text** and italic *text*
            sub_tokens = re.split(r'(\*\*.*?\*\*|\*.*?\*)', token)
            for st in sub_tokens:
                if st.startswith('**') and st.endswith('**') and len(st) > 4:
                    run = p.add_run(st[2:-2])
                    run.bold = True
                    run.font.name = "Times New Roman"
                    run.font.size = Pt(11)
                elif st.startswith('*') and st.endswith('*') and len(st) > 2:
                    run = p.add_run(st[1:-1])
                    run.italic = True
                    run.font.name = "Times New Roman"
                    run.font.size = Pt(11)
                else:
                    run = p.add_run(st)
                    run.font.name = "Times New Roman"
                    run.font.size = Pt(11)
    return p

def build_word_document():
    print(f"Reading markdown from {MD_PATH}...")
    text = MD_PATH.read_text(encoding="utf-8")
    lines = text.split("\n")
    
    doc = Document()
    
    # Page setup: Standard Letter, 1-inch margins
    sections = doc.sections
    for sec in sections:
        sec.top_margin = Inches(1.0)
        sec.bottom_margin = Inches(1.0)
        sec.left_margin = Inches(1.0)
        sec.right_margin = Inches(1.0)
    
    i = 0
    n = len(lines)
    
    while i < n:
        line = lines[i].strip()
        
        # Empty line
        if not line:
            i += 1
            continue
            
        # Horizontal rule
        if line in ["---", "***", "___"]:
            i += 1
            continue
            
        # Title (# ...)
        if line.startswith("# ") and not line.startswith("## "):
            title_text = line[2:].strip()
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_before = Pt(12)
            p.paragraph_format.space_after = Pt(12)
            run = p.add_run(title_text)
            run.bold = True
            run.font.name = "Times New Roman"
            run.font.size = Pt(16)
            run.font.color.rgb = RGBColor(16, 44, 87) # Classic academic dark navy
            i += 1
            continue
            
        # Heading 1 (## ...)
        if line.startswith("## "):
            h_text = line[3:].strip()
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(16)
            p.paragraph_format.space_after = Pt(6)
            p.paragraph_format.keep_with_next = True
            run = p.add_run(h_text)
            run.bold = True
            run.font.name = "Times New Roman"
            run.font.size = Pt(13)
            run.font.color.rgb = RGBColor(16, 44, 87)
            i += 1
            continue
            
        # Heading 2 (### ...)
        if line.startswith("### "):
            h_text = line[4:].strip()
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(12)
            p.paragraph_format.space_after = Pt(4)
            p.paragraph_format.keep_with_next = True
            run = p.add_run(h_text)
            run.bold = True
            run.font.name = "Times New Roman"
            run.font.size = Pt(12)
            run.font.color.rgb = RGBColor(30, 30, 30)
            i += 1
            continue
            
        # Display Equation ($$...$$)
        if line.startswith("$$"):
            # Check if one-line or multi-line
            if line.endswith("$$") and len(line) > 4:
                eq = line[2:-2].strip()
                i += 1
            else:
                eq_lines = [line[2:].strip()]
                i += 1
                while i < n and not lines[i].strip().endswith("$$"):
                    eq_lines.append(lines[i].strip())
                    i += 1
                if i < n:
                    eq_lines.append(lines[i].strip()[:-2].strip())
                    i += 1
                eq = " ".join(eq_lines)
                
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_before = Pt(8)
            p.paragraph_format.space_after = Pt(8)
            omml = latex_to_omml(eq, display=True)
            if omml is not None:
                p._p.append(omml)
            else:
                run = p.add_run(eq)
                run.italic = True
                run.font.name = "Cambria Math"
                run.font.size = Pt(11)
            continue
            
        # Markdown Table (| ... |)
        if line.startswith("|") and line.endswith("|"):
            tbl_lines = []
            while i < n and lines[i].strip().startswith("|") and lines[i].strip().endswith("|"):
                tbl_lines.append(lines[i].strip())
                i += 1
                
            # Filter out separator line (| :--- |)
            data_rows = []
            for tl in tbl_lines:
                if re.match(r"^\|(\s*:?-+:?\s*\|)+$", tl):
                    continue
                cells = [c.strip() for c in tl.split("|")[1:-1]]
                data_rows.append(cells)
                
            if data_rows:
                num_rows = len(data_rows)
                num_cols = max(len(r) for r in data_rows)
                tbl = doc.add_table(rows=num_rows, cols=num_cols)
                tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
                set_table_borders(tbl)
                
                for r_idx, row_data in enumerate(data_rows):
                    for c_idx in range(num_cols):
                        val = row_data[c_idx] if c_idx < len(row_data) else ""
                        cell = tbl.cell(r_idx, c_idx)
                        cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
                        set_cell_margins(cell, top=80, bottom=80, left=120, right=120)
                        
                        p_cell = cell.paragraphs[0]
                        p_cell.paragraph_format.space_after = Pt(2)
                        p_cell.paragraph_format.space_before = Pt(2)
                        p_cell.paragraph_format.line_spacing = 1.05
                        
                        # Shading and bold for header
                        if r_idx == 0:
                            set_cell_shading(cell, "EAECEE")
                            run = p_cell.add_run(val.replace("**", ""))
                            run.bold = True
                            run.font.name = "Times New Roman"
                            run.font.size = Pt(9.5)
                            p_cell.alignment = WD_ALIGN_PARAGRAPH.CENTER
                        else:
                            # Parse inline bold and math in cell
                            if re.search(r"^[\d\.\-\+\%]+$", val.replace("**", "").replace("$", "").strip()):
                                p_cell.alignment = WD_ALIGN_PARAGRAPH.CENTER
                            else:
                                p_cell.alignment = WD_ALIGN_PARAGRAPH.LEFT
                                
                            tokens = re.split(r'(\$.*?\$|\*\*.*?\*\*)', val)
                            for t in tokens:
                                if t.startswith('$') and t.endswith('$') and len(t) > 1:
                                    omml = latex_to_omml(t[1:-1], display=False)
                                    if omml is not None:
                                        p_cell._p.append(omml)
                                    else:
                                        r = p_cell.add_run(t)
                                        r.font.name = "Cambria Math"
                                        r.font.size = Pt(9.5)
                                elif t.startswith('**') and t.endswith('**') and len(t) > 4:
                                    r = p_cell.add_run(t[2:-2])
                                    r.bold = True
                                    r.font.name = "Times New Roman"
                                    r.font.size = Pt(9.5)
                                else:
                                    r = p_cell.add_run(t)
                                    r.font.name = "Times New Roman"
                                    r.font.size = Pt(9.5)
                                    
                doc.add_paragraph().paragraph_format.space_after = Pt(4)
            continue
            
        # Blockquotes or Callouts (> ...)
        if line.startswith(">"):
            bq_text = line.lstrip(">").strip()
            p = doc.add_paragraph()
            p.paragraph_format.left_indent = Inches(0.4)
            p.paragraph_format.right_indent = Inches(0.4)
            p.paragraph_format.space_before = Pt(4)
            p.paragraph_format.space_after = Pt(4)
            run = p.add_run(bq_text)
            run.italic = True
            run.font.name = "Times New Roman"
            run.font.size = Pt(10.5)
            i += 1
            continue
            
        # Bullet list items (- ...)
        if line.startswith("- "):
            item_text = line[2:].strip()
            # If in references, format with hanging indent
            p = doc.add_paragraph(style='List Bullet')
            p.paragraph_format.space_before = Pt(2)
            p.paragraph_format.space_after = Pt(3)
            p.paragraph_format.line_spacing = 1.15
            
            # Add formatted text
            tokens = re.split(r'(\$.*?\$|\*\*.*?\*\*|\*.*?\*)', item_text)
            for t in tokens:
                if t.startswith('$') and t.endswith('$') and len(t) > 1:
                    omml = latex_to_omml(t[1:-1], display=False)
                    if omml is not None:
                        p._p.append(omml)
                    else:
                        r = p.add_run(t)
                        r.font.name = "Cambria Math"
                        r.font.size = Pt(11)
                elif t.startswith('**') and t.endswith('**') and len(t) > 4:
                    r = p.add_run(t[2:-2])
                    r.bold = True
                    r.font.name = "Times New Roman"
                    r.font.size = Pt(11)
                elif t.startswith('*') and t.endswith('*') and len(t) > 2:
                    r = p.add_run(t[1:-1])
                    r.italic = True
                    r.font.name = "Times New Roman"
                    r.font.size = Pt(11)
                else:
                    r = p.add_run(t)
                    r.font.name = "Times New Roman"
                    r.font.size = Pt(11)
            i += 1
            continue
            
        # Embed Figure 1 after RQ2 intro if referenced
        if "Figure 1 plots the complete Pareto frontiers" in line:
            add_formatted_paragraph(doc, line)
            i += 1
            fig1_path = FIGS_DIR / "fig1_pareto_frontiers_four_benchmarks.png"
            if fig1_path.exists():
                p_img = doc.add_paragraph()
                p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
                p_img.paragraph_format.space_before = Pt(8)
                p_img.paragraph_format.space_after = Pt(4)
                p_img.add_run().add_picture(str(fig1_path), width=Inches(6.2))
                
                p_cap = doc.add_paragraph()
                p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
                p_cap.paragraph_format.space_after = Pt(12)
                r_cap = p_cap.add_run("Figure 1: ")
                r_cap.bold = True
                r_cap.font.name = "Times New Roman"
                r_cap.font.size = Pt(10)
                r_desc = p_cap.add_run("Empirical Pareto Frontiers (Review Budget vs. Held-out Decision Legitimacy) across HateXplain, MD-Agreement, HS-Brexit, and ArMIS. LAJ consistently dominates conventional MSP and fixed 3-tier baselines.")
                r_desc.italic = True
                r_desc.font.name = "Times New Roman"
                r_desc.font.size = Pt(10)
            continue
            
        # Embed Figure 2 after Section 7.1 intro
        if "Table 5 and Figure 2 present the Autonomous Overrule Rate" in line:
            add_formatted_paragraph(doc, line)
            i += 1
            fig2_path = FIGS_DIR / "fig2_demographic_disparity_mitigation.png"
            if fig2_path.exists():
                p_img = doc.add_paragraph()
                p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
                p_img.paragraph_format.space_before = Pt(8)
                p_img.paragraph_format.space_after = Pt(4)
                p_img.add_run().add_picture(str(fig2_path), width=Inches(6.2))
                
                p_cap = doc.add_paragraph()
                p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
                p_cap.paragraph_format.space_after = Pt(12)
                r_cap = p_cap.add_run("Figure 2: ")
                r_cap.bold = True
                r_cap.font.name = "Times New Roman"
                r_cap.font.size = Pt(10)
                r_desc = p_cap.add_run("Sociodemographic Overrule Disparity Mitigation under matched operational review budget (B=0.5). Left: Autonomous overrule of targeted Muslim immigrant annotators on HS-Brexit. Right: Misogyny overrule disparity across gender and political ideology on ArMIS.")
                r_desc.italic = True
                r_desc.font.name = "Times New Roman"
                r_desc.font.size = Pt(10)
            continue

        # Regular Paragraph
        add_formatted_paragraph(doc, line)
        i += 1

    print(f"Saving compiled manuscript to {DOCX_PATH}...")
    doc.save(DOCX_PATH)
    print("Document successfully created and saved!")

if __name__ == "__main__":
    build_word_document()
