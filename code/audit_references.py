import re
from pathlib import Path

content = Path('manuscript_IPM_v2/IPM_Manuscript.md').read_text(encoding='utf-8')
parts = content.split('## References')
body = parts[0]
refs_text = parts[1]

ref_lines = [l.strip() for l in refs_text.split('\n') if l.strip().startswith('-')]
refs = []
for l in ref_lines:
    m = re.match(r'-\s*(.+?)\s*\((\d{4}[a-z]?)\)\.\s*(.+)', l)
    if m:
        authors_raw = m.group(1).strip()
        first_author_last = authors_raw.split(',')[0].strip().split()[-1]
        year = m.group(2).strip()
        rest = m.group(3).strip()
        refs.append({'first_last': first_author_last, 'year': year, 'raw': l, 'authors': authors_raw, 'rest': rest})
    else:
        print('UNPARSED:', l)

print(f'Total parsed references: {len(refs)}')

# Check citations in body
cites_found = set()
# Match (Author et al., Year) or Author et al. (Year)
for m in re.finditer(r'([A-Z][a-zA-Z\xc0-\xff\-]+)(?:\s+et\s+al\.)?,?\s*\(([12][0-9]{3}[a-z]?)\)', body):
    cites_found.add((m.group(1).strip(), m.group(2).strip()))

for m in re.finditer(r'\(([A-Z][a-zA-Z\xc0-\xff\-]+)(?:\s+et\s+al\.)?,\s*([12][0-9]{3}[a-z]?)\)', body):
    cites_found.add((m.group(1).strip(), m.group(2).strip()))

for m in re.finditer(r'\(([^)]+)\)', body):
    inside = m.group(1)
    for chunk in inside.split(';'):
        chunk = chunk.strip()
        m_chunk = re.match(r'([A-Z][a-zA-Z\xc0-\xff\-]+)(?:\s+et\s+al\.)?,?\s*([12][0-9]{3}[a-z]?)', chunk)
        if m_chunk:
            cites_found.add((m_chunk.group(1).strip(), m_chunk.group(2).strip()))

IGNORE = {'Table', 'Figure', 'Proposition', 'Theorem', 'Definition', 'Section', 'Equation',
          'RQ1', 'RQ2', 'RQ3', 'RQ4', 'HAA', 'MSP', 'CRC', 'RCPS', 'LAJ', 'DCS', 'MT',
          'NLP', 'DSA', 'UK', 'EU', 'AI', 'Train', 'Val', 'Test', 'National', 'Emerson',
          'Singapore', 'Pakistan', 'Department', 'School'}

missing_refs = []
for a, y in sorted(cites_found):
    if a in IGNORE:
        continue
    matched = any(r['first_last'].lower() == a.lower() and r['year'] == y for r in refs)
    if not matched:
        missing_refs.append(f"{a} ({y})")

print(f'\nCitations in body missing from References section ({len(missing_refs)}):')
for m in missing_refs:
    print('  MISSING IN REFS:', m)

# Check references not cited in body
uncited_refs = []
for r in refs:
    a = r['first_last']
    y = r['year']
    pat = rf'\b{a}\b.*?\b{y}\b'
    if not re.search(pat, body, flags=re.IGNORECASE):
        uncited_refs.append(f"{a} ({y})")

print(f'\nReferences in References section never cited in body ({len(uncited_refs)}):')
for u in uncited_refs:
    print('  UNCITED IN BODY:', u)
