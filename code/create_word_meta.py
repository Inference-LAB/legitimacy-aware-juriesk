from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def create_title_page():
    doc = Document()
    for sec in doc.sections:
        sec.top_margin = Inches(1.0)
        sec.bottom_margin = Inches(1.0)
        sec.left_margin = Inches(1.0)
        sec.right_margin = Inches(1.0)
        
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_before = Pt(24)
    p_title.paragraph_format.space_after = Pt(18)
    r = p_title.add_run("How Many Humans Does a Decision Need?\nLegitimacy-Aware Jury Allocation and Conformal Overrule Guarantees for Content Moderation")
    r.bold = True
    r.font.name = "Times New Roman"
    r.font.size = Pt(16)
    r.font.color.rgb = RGBColor(16, 44, 87)
    
    p_auth = doc.add_paragraph()
    p_auth.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_auth.paragraph_format.space_after = Pt(4)
    r = p_auth.add_run("Shixiang Yu")
    r.bold = True
    r.font.name = "Times New Roman"
    r.font.size = Pt(12)
    r_sup = p_auth.add_run("1")
    r_sup.font.superscript = True
    p_auth.add_run(", ")
    r2 = p_auth.add_run("Muhammad Khubaib Ahmad")
    r2.bold = True
    r2.font.name = "Times New Roman"
    r2.font.size = Pt(12)
    r_sup2 = p_auth.add_run("2,3,*")
    r_sup2.font.superscript = True
    
    p_aff = doc.add_paragraph()
    p_aff.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_aff.paragraph_format.space_after = Pt(18)
    r = p_aff.add_run("1 ")
    r.font.superscript = True
    p_aff.add_run("School of Computing, National University of Singapore, Singapore\n")
    r = p_aff.add_run("2 ")
    r.font.superscript = True
    p_aff.add_run("Department of Computer Science, Emerson University Multan, Multan, Pakistan\n")
    r = p_aff.add_run("3 ")
    r.font.superscript = True
    p_aff.add_run("INFERENCE Lab, Multan, Pakistan\n")
    r_star = p_aff.add_run("* ")
    r_star.font.superscript = True
    p_aff.add_run("Corresponding author: Muhammad Khubaib Ahmad (Email: khubaib@eum.edu.pk)")
    for run in p_aff.runs:
        run.font.name = "Times New Roman"
        run.font.size = Pt(10)
        run.font.color.rgb = RGBColor(80, 80, 80)
        
    p_meta = doc.add_paragraph()
    p_meta.paragraph_format.space_before = Pt(12)
    p_meta.paragraph_format.space_after = Pt(12)
    r_h = p_meta.add_run("Manuscript Metadata\n")
    r_h.bold = True
    r_h.font.size = Pt(12)
    p_meta.add_run("• Target Journal: Information Processing & Management (Elsevier)\n• Manuscript Track: Critical Application Manuscript (System Design Research in Social Computing)\n• Word Count: ~9,500 words\n• Target Impact Factor: 8.6 (Q1 SCIE/SSCI, CAS Tier 1)")
    for run in p_meta.runs:
        run.font.name = "Times New Roman"
        
    p_credit = doc.add_paragraph()
    p_credit.paragraph_format.space_before = Pt(12)
    p_credit.paragraph_format.space_after = Pt(6)
    r = p_credit.add_run("CRediT Authorship Contribution Statement\n")
    r.bold = True
    r.font.size = Pt(12)
    p_credit.add_run("• Shixiang Yu: Conceptualization, Methodology, Software, Formal Analysis, Data Curation, Validation, Writing – Original Draft.\n• Muhammad Khubaib Ahmad: Conceptualization, Methodology, Formal Analysis, Supervision, Project Administration, Writing – Review & Editing, Funding Acquisition.")
    for run in p_credit.runs:
        run.font.name = "Times New Roman"
        
    p_dec = doc.add_paragraph()
    p_dec.paragraph_format.space_before = Pt(12)
    p_dec.paragraph_format.space_after = Pt(6)
    r = p_dec.add_run("Declarations\n")
    r.bold = True
    r.font.size = Pt(12)
    p_dec.add_run("• Declaration of Competing Interest: The authors declare that they have no known competing financial interests or personal relationships that could have appeared to influence the work reported in this paper.\n• Funding: This research did not receive any specific grant from funding agencies in the public, commercial, or not-for-profit sectors.\n• Data and Code Availability: All four benchmark datasets (HateXplain, MD-Agreement, HS-Brexit, ArMIS) are publicly accessible. Complete source code, models, and replication notebooks are provided.")
    for run in p_dec.runs:
        run.font.name = "Times New Roman"
        
    doc.save(ROOT / "IPM_Title_Page.docx")
    print("Created IPM_Title_Page.docx")

def create_cover_letter():
    doc = Document()
    for sec in doc.sections:
        sec.top_margin = Inches(1.0)
        sec.bottom_margin = Inches(1.0)
        sec.left_margin = Inches(1.0)
        sec.right_margin = Inches(1.0)
        
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(12)
    r = p.add_run("To:\nProfessor Jiming Liu, PhD, Editor-in-Chief\nInformation Processing & Management (Elsevier)\nDate: November 19, 2026")
    r.font.name = "Times New Roman"
    r.font.size = Pt(11)
    
    p2 = doc.add_paragraph()
    p2.paragraph_format.space_after = Pt(12)
    r = p2.add_run("Subject: Submission of Critical Application Manuscript to Information Processing & Management")
    r.bold = True
    r.font.name = "Times New Roman"
    r.font.size = Pt(11)
    
    body = (
        "Dear Professor Liu and Members of the Editorial Board,\n\n"
        "We are pleased to submit our original research manuscript titled \"How Many Humans Does a Decision Need? "
        "Legitimacy-Aware Jury Allocation and Conformal Overrule Guarantees for Content Moderation\" for consideration "
        "as a Critical Application Manuscript in Information Processing & Management.\n\n"
        "Modern content moderation systems face a fundamental crisis: scalable AI classifiers must arbitrate online speech, "
        "yet hate speech and toxic discourse are inherently subjective and culturally situated. Conventional \"learning-to-defer\" "
        "frameworks operate under a flawed binary assumption—routing each post either entirely to machine autonomy or to a single "
        "human reviewer—while treating inter-annotator disagreement as label noise. Consequently, autonomous systems disproportionately "
        "overrule vulnerable demographic minorities, while single-human review fails to resolve contested interpretations.\n\n"
        "In this manuscript, we present a transformative paradigm: Legitimacy-Aware Jury Allocation (LAJ). Grounded in a generalization "
        "of the Condorcet Jury Theorem over the multi-class probability simplex, we derive a closed-form panel value function f_k(p) "
        "quantifying the exact expected agreement between a k-person human jury and the broader annotator community. By modeling human "
        "disagreement through a second-order bootstrap ensemble, our system dynamically allocates optimal panel sizes k*(x) in {0, 1, ..., M-1} "
        "under operational review budgets. Furthermore, we equip the autonomous tier with distribution-free Conformal Risk Control (CRC), "
        "guaranteeing that the Autonomous Overrule Rate (AOR) cannot exceed a policy-specified safety threshold alpha with finite-sample validity.\n\n"
        "Evaluated across four diverse multi-annotator benchmarks (HateXplain, MD-Agreement, HS-Brexit, ArMIS) using a non-circular Held-out "
        "Annotator Agreement (HAA) protocol, LAJ uniformly dominates conventional Maximum Softmax Probability (MSP) and fixed multi-tier heuristics. "
        "In sociodemographic audits on HS-Brexit and ArMIS, LAJ reduces the autonomous overrule of targeted minorities (Muslim immigrants and female "
        "annotators) by 42.8% to 73.9% relative to standard deployment.\n\n"
        "This work directly aligns with IPM's Critical Application track at the intersection of computing and information science, addressing system design "
        "and societal governance in social computing. We confirm that this manuscript is original, has not been published previously, and is not under "
        "consideration elsewhere. The authors declare no competing interests.\n\n"
        "Thank you for your time and consideration of our work.\n\n"
        "Sincerely,\n\n"
        "Muhammad Khubaib Ahmad, PhD (Corresponding Author)\n"
        "Department of Computer Science, Emerson University Multan\n"
        "INFERENCE Lab, Multan, Pakistan\n"
        "Email: khubaib@eum.edu.pk\n\n"
        "On behalf of co-author:\n"
        "Shixiang Yu\n"
        "School of Computing, National University of Singapore"
    )
    p_body = doc.add_paragraph()
    p_body.paragraph_format.line_spacing = 1.15
    p_body.paragraph_format.space_after = Pt(12)
    r = p_body.add_run(body)
    r.font.name = "Times New Roman"
    r.font.size = Pt(11)
    
    doc.save(ROOT / "IPM_Cover_Letter.docx")
    print("Created IPM_Cover_Letter.docx")

if __name__ == "__main__":
    create_title_page()
    create_cover_letter()
