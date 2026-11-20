import docx
from docx.oxml import parse_xml
import re

doc_path = "manuscript_IPM_v2/IPM_Manuscript.docx"
doc = docx.Document(doc_path)

print(f"Total Paragraphs: {len(doc.paragraphs)}")
print(f"Total Tables: {len(doc.tables)}")

# Check Headings
headings = []
for i, p in enumerate(doc.paragraphs):
    if p.style.name.startswith("Heading"):
        headings.append((p.style.name, p.text.strip()))

print("\n--- Detected Headings ---")
for h_style, h_text in headings:
    print(f"[{h_style}] {h_text}")

# Check for raw math markers or unparsed latex in paragraphs
raw_math_issues = []
for i, p in enumerate(doc.paragraphs):
    text = p.text
    # Search for $ or \tag or math backslashes
    if "$" in text:
        raw_math_issues.append((f"Paragraph {i}", text))
    elif re.search(r'\\[a-zA-Z]+', text):
        # check if it's a latex command like \frac, \sum, \mathcal, etc.
        m = re.findall(r'\\[a-zA-Z]+', text)
        # ignore ordinary backslashes if any (though usually none in manuscript)
        raw_math_issues.append((f"Paragraph {i} (possible latex commands: {m})", text))

# Check tables
table_math_issues = []
for t_idx, table in enumerate(doc.tables):
    for r_idx, row in enumerate(table.rows):
        for c_idx, cell in enumerate(row.cells):
            ctext = cell.text
            if "$" in ctext:
                table_math_issues.append((f"Table {t_idx} [R{r_idx}C{c_idx}]", ctext))
            elif re.search(r'\\[a-zA-Z]+', ctext):
                m = re.findall(r'\\[a-zA-Z]+', ctext)
                table_math_issues.append((f"Table {t_idx} [R{r_idx}C{c_idx}] (commands: {m})", ctext))

print("\n--- Math Issues in Paragraphs ---")
if not raw_math_issues:
    print("Zero raw math markers ($ or LaTeX commands) found in paragraphs!")
else:
    for loc, txt in raw_math_issues[:15]:
        print(f"{loc}: {txt[:100]}...")

print("\n--- Math Issues in Tables ---")
if not table_math_issues:
    print("Zero raw math markers ($ or LaTeX commands) found in tables!")
else:
    for loc, txt in table_math_issues[:15]:
        print(f"{loc}: {txt[:100]}...")

# Check for em dashes and en dashes
dashes_found = []
for i, p in enumerate(doc.paragraphs):
    if "—" in p.text or "–" in p.text:
        dashes_found.append((f"Paragraph {i}", p.text))
for t_idx, table in enumerate(doc.tables):
    for r_idx, row in enumerate(table.rows):
        for c_idx, cell in enumerate(row.cells):
            if "—" in cell.text or "–" in cell.text:
                dashes_found.append((f"Table {t_idx} [R{r_idx}C{c_idx}]", cell.text))

print("\n--- Em/En Dashes Audit ---")
if not dashes_found:
    print("Zero em dashes and zero en dashes found across entire document!")
else:
    print(f"Found {len(dashes_found)} instances of em/en dashes:")
    for loc, txt in dashes_found[:10]:
        print(f"{loc}: {txt[:100]}")

# Check Equation count and tags
# In our convert script, display equations were added as borderless tables (1 row, 2 cols)
eq_tables = []
for t_idx, table in enumerate(doc.tables):
    if len(table.rows) == 1 and len(table.columns) == 2:
        cell_r = table.cell(0, 1).text.strip()
        if cell_r.startswith("(") and cell_r.endswith(")"):
            eq_tables.append((t_idx, cell_r))

print(f"\n--- Display Equation Tables: {len(eq_tables)} found ---")
for t_idx, tag in eq_tables:
    print(f"Table {t_idx} -> Tag: {tag}")
