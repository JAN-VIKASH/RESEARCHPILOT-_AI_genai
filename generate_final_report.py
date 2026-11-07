"""
generate_final_report.py
Generates the complete, submission-ready 27-page academic project report PDF:
'ResearchPilot_AI_Final_Report.pdf'
"""

import os
import sys
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import registerFontFamily

# Register Unicode TrueType font (Arial) to ensure characters like 'ğ' in Oğuz render accurately
try:
    arial_path = r"C:\Windows\Fonts\arial.ttf"
    arial_bd_path = r"C:\Windows\Fonts\arialbd.ttf"
    arial_it_path = r"C:\Windows\Fonts\ariali.ttf"
    arial_bi_path = r"C:\Windows\Fonts\arialbi.ttf"
    if os.path.exists(arial_path) and os.path.exists(arial_bd_path):
        pdfmetrics.registerFont(TTFont('Helvetica', arial_path))
        pdfmetrics.registerFont(TTFont('Helvetica-Bold', arial_bd_path))
        pdfmetrics.registerFont(TTFont('Helvetica-Oblique', arial_it_path if os.path.exists(arial_it_path) else arial_path))
        pdfmetrics.registerFont(TTFont('Helvetica-BoldOblique', arial_bi_path if os.path.exists(arial_bi_path) else arial_bd_path))
        registerFontFamily('Helvetica', normal='Helvetica', bold='Helvetica-Bold', italic='Helvetica-Oblique', boldItalic='Helvetica-BoldOblique')
except Exception:
    pass

import build_diagrams

PAGE_WIDTH, PAGE_HEIGHT = A4
LEFT_MARGIN = 48
RIGHT_MARGIN = 48
TOP_MARGIN = 44
BOTTOM_MARGIN = 44
USABLE_WIDTH = PAGE_WIDTH - LEFT_MARGIN - RIGHT_MARGIN

class NumberedCanvas(canvas.Canvas):
    """Two-pass canvas to dynamically compute and draw running headers and footers with page numbers."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        
        # Cover page (Page 1)
        if self._pageNumber == 1:
            self.setFont("Helvetica-Bold", 7.5)
            self.setFillColor(colors.HexColor("#0F172A"))
            self.drawCentredString(PAGE_WIDTH / 2.0, PAGE_HEIGHT - 28, "PRASAD V POTLURI SIDDHARTHA INSTITUTE OF TECHNOLOGY | CSE")
            self.setFont("Helvetica", 7.5)
            self.setFillColor(colors.HexColor("#475569"))
            self.drawCentredString(PAGE_WIDTH / 2.0, 20, f"ResearchPilot AI – Academic Project Report | {self._pageNumber}")
            self.restoreState()
            return

        # Running Header on pages 2-27 (CORRECTION I: SIDDHARTHA with 'h')
        self.setFont("Helvetica-Bold", 7.5)
        self.setFillColor(colors.HexColor("#0F172A"))
        self.drawString(LEFT_MARGIN, PAGE_HEIGHT - 28, "PRASAD V POTLURI SIDDHARTHA INSTITUTE OF TECHNOLOGY")
        self.setFont("Helvetica", 7.5)
        self.setFillColor(colors.HexColor("#475569"))
        self.drawRightString(PAGE_WIDTH - RIGHT_MARGIN, PAGE_HEIGHT - 28, "CSE")

        # Running Footer
        self.setFont("Helvetica", 7.5)
        self.setFillColor(colors.HexColor("#475569"))
        self.drawCentredString(PAGE_WIDTH / 2.0, 20, f"ResearchPilot AI – Academic Project Report | {self._pageNumber}")
        self.restoreState()


def get_styles():
    base = getSampleStyleSheet()
    
    styles = {
        'DocTitle': ParagraphStyle('DocTitle', parent=base['Normal'], fontName='Helvetica-Bold', fontSize=18, leading=22, alignment=1, textColor=colors.HexColor('#0F172A')),
        'DocSubtitle': ParagraphStyle('DocSubtitle', parent=base['Normal'], fontName='Helvetica-Oblique', fontSize=10.5, leading=14, alignment=1, textColor=colors.HexColor('#334155')),
        'CoverInstitution': ParagraphStyle('CoverInstitution', parent=base['Normal'], fontName='Helvetica-Bold', fontSize=12, leading=15, alignment=1, textColor=colors.HexColor('#0F172A')),
        'CoverDept': ParagraphStyle('CoverDept', parent=base['Normal'], fontName='Helvetica-Bold', fontSize=9.5, leading=13, alignment=1, textColor=colors.HexColor('#1E293B')),
        'CoverYear': ParagraphStyle('CoverYear', parent=base['Normal'], fontName='Helvetica-Bold', fontSize=9, leading=12, alignment=1, textColor=colors.HexColor('#334155')),
        'CoverCourse': ParagraphStyle('CoverCourse', parent=base['Normal'], fontName='Helvetica-Bold', fontSize=11, leading=15, alignment=1, textColor=colors.HexColor('#0F172A')),
        
        'ChapterHeader': ParagraphStyle('ChapterHeader', parent=base['Normal'], fontName='Helvetica-Bold', fontSize=13.5, leading=17, textColor=colors.HexColor('#0F172A'), spaceAfter=5),
        'SectionHeader': ParagraphStyle('SectionHeader', parent=base['Normal'], fontName='Helvetica-Bold', fontSize=9.2, leading=12, textColor=colors.HexColor('#0F172A'), spaceBefore=4, spaceAfter=2.5),
        'SubSectionHeader': ParagraphStyle('SubSectionHeader', parent=base['Normal'], fontName='Helvetica-Bold', fontSize=8.2, leading=10.5, textColor=colors.HexColor('#1E293B'), spaceBefore=2.5, spaceAfter=1.5),
        
        'Body': ParagraphStyle('Body', parent=base['Normal'], fontName='Helvetica', fontSize=7.6, leading=10.4, textColor=colors.HexColor('#0F172A'), spaceAfter=3.5, alignment=4),
        'BodyCompact': ParagraphStyle('BodyCompact', parent=base['Normal'], fontName='Helvetica', fontSize=7.2, leading=9.6, textColor=colors.HexColor('#0F172A'), spaceAfter=2.0, alignment=4),
        'Bullet': ParagraphStyle('Bullet', parent=base['Normal'], fontName='Helvetica', fontSize=7.5, leading=10.0, textColor=colors.HexColor('#0F172A'), leftIndent=12, firstLineIndent=-8, spaceAfter=1.8),
        
        'Caption': ParagraphStyle('Caption', parent=base['Normal'], fontName='Helvetica-Oblique', fontSize=7.0, leading=9.0, alignment=1, textColor=colors.HexColor('#475569'), spaceBefore=2, spaceAfter=3),
        'TableText': ParagraphStyle('TableText', parent=base['Normal'], fontName='Helvetica', fontSize=6.8, leading=8.6, textColor=colors.HexColor('#0F172A')),
        'TableHeader': ParagraphStyle('TableHeader', parent=base['Normal'], fontName='Helvetica-Bold', fontSize=7.0, leading=9.0, textColor=colors.HexColor('#0F172A')),
        'TOCItem': ParagraphStyle('TOCItem', parent=base['Normal'], fontName='Helvetica-Bold', fontSize=7.6, leading=11.2, textColor=colors.HexColor('#0F172A')),
        'TOCSub': ParagraphStyle('TOCSub', parent=base['Normal'], fontName='Helvetica', fontSize=7.0, leading=9.8, textColor=colors.HexColor('#475569'), leftIndent=10),
    }
    return styles

def generate_report():
    output_pdf_path = os.path.join(os.path.dirname(__file__), "ResearchPilot_AI_Final_Report.pdf")
    doc = SimpleDocTemplate(
        output_pdf_path,
        pagesize=A4,
        leftMargin=LEFT_MARGIN,
        rightMargin=RIGHT_MARGIN,
        topMargin=TOP_MARGIN,
        bottomMargin=BOTTOM_MARGIN,
    )
    
    styles = get_styles()
    story = []

    # =========================================================================
    # PAGE 1: COVER PAGE
    # =========================================================================
    story.append(Spacer(1, 15))
    story.append(Paragraph("PRASAD V POTLURI SIDDHARTHA INSTITUTE OF TECHNOLOGY", styles['CoverInstitution']))
    story.append(Spacer(1, 3))
    story.append(Paragraph("DEPARTMENT OF COMPUTER SCIENCE & ENGINEERING", styles['CoverDept']))
    story.append(Spacer(1, 2))
    story.append(Paragraph("ACADEMIC YEAR: 2026–27", styles['CoverYear']))
    story.append(Spacer(1, 40))
    story.append(Paragraph("GENERATIVE AI COURSE PROJECT REPORT", styles['CoverCourse']))
    story.append(Spacer(1, 18))
    story.append(Paragraph("RESEARCHPILOT AI", styles['DocTitle']))
    story.append(Spacer(1, 6))
    story.append(Paragraph("An Intelligent Research Assistant with Supervisor Agent Architecture", styles['DocSubtitle']))
    story.append(Spacer(1, 45))
    story.append(Paragraph("<b>Faculty Name:</b> [FACULTY NAME]", styles['Body']))
    story.append(Spacer(1, 6))
    story.append(Paragraph("<b>Team Members</b>", styles['SubSectionHeader']))
    
    team_data = [
        [Paragraph("1. K. Jan Vikash", styles['TableText']), Paragraph("23501A0571", styles['TableText'])],
        [Paragraph("2. K. Harsha Vardhan", styles['TableText']), Paragraph("23501A0584", styles['TableText'])],
        [Paragraph("3. K. Sruthi", styles['TableText']), Paragraph("23501A0573", styles['TableText'])],
        [Paragraph("4. K. Yoshita Navya", styles['TableText']), Paragraph("23501A0581", styles['TableText'])],
    ]
    team_table = Table(team_data, colWidths=[280, 200])
    team_table.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#0F172A')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(team_table)
    story.append(Spacer(1, 30))
    
    story.append(Paragraph("<b>GitHub Repository Link:</b> [INSERT REPOSITORY URL]", styles['Body']))
    story.append(Paragraph("<b>Project Deployment Link:</b> [INSERT DEPLOYMENT URL OR WRITE NOT DEPLOYED]", styles['Body']))
    story.append(Paragraph("<b>Deployment Platform:</b> [INSERT PLATFORM / NOT APPLICABLE]", styles['Body']))
    story.append(Spacer(1, 45))
    
    sig_data = [
        [Paragraph("<b>Signature of Faculty</b>", styles['Body']), Paragraph("<b>Signature of HOD</b>", styles['Body'])]
    ]
    sig_table = Table(sig_data, colWidths=[240, 240])
    sig_table.setStyle(TableStyle([
        ('ALIGN', (0,0), (0,0), 'LEFT'),
        ('ALIGN', (1,0), (1,0), 'RIGHT'),
    ]))
    story.append(sig_table)
    story.append(PageBreak())

    # =========================================================================
    # PAGE 2: CONTENTS
    # =========================================================================
    story.append(Paragraph("CONTENTS", styles['ChapterHeader']))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#0F172A"), spaceBefore=2, spaceAfter=10))
    
    toc_data = [
        [Paragraph("CHAPTER 1: INTRODUCTION", styles['TOCItem']), Paragraph("3", styles['TOCItem'])],
        [Paragraph("&nbsp;&nbsp;1.1 Background &nbsp;&bull;&nbsp; 1.2 Problem Statement &nbsp;&bull;&nbsp; 1.3 Motivation &nbsp;&bull;&nbsp; 1.4 Objectives &nbsp;&bull;&nbsp; 1.5 Scope", styles['TOCSub']), Paragraph("", styles['TOCSub'])],
        [Paragraph("CHAPTER 2: LITERATURE SURVEY", styles['TOCItem']), Paragraph("5", styles['TOCItem'])],
        [Paragraph("&nbsp;&nbsp;2.1 Introduction &nbsp;&bull;&nbsp; 2.2 Review of Research &nbsp;&bull;&nbsp; 2.3 Comparison Table &nbsp;&bull;&nbsp; 2.4 Research Gap", styles['TOCSub']), Paragraph("", styles['TOCSub'])],
        [Paragraph("CHAPTER 3: PROBLEM DEFINITION AND REQUIREMENTS", styles['TOCItem']), Paragraph("8", styles['TOCItem'])],
        [Paragraph("&nbsp;&nbsp;3.1 Existing System &nbsp;&bull;&nbsp; 3.2 Limitations &nbsp;&bull;&nbsp; 3.3 Proposed System &nbsp;&bull;&nbsp; 3.4 Functional Reqs &nbsp;&bull;&nbsp; 3.7 Software", styles['TOCSub']), Paragraph("", styles['TOCSub'])],
        [Paragraph("CHAPTER 4: SYSTEM DESIGN", styles['TOCItem']), Paragraph("10", styles['TOCItem'])],
        [Paragraph("&nbsp;&nbsp;4.1 Overall Architecture &nbsp;&bull;&nbsp; 4.2 Supervisor Agent &nbsp;&bull;&nbsp; 4.4 Intent Hierarchy &nbsp;&bull;&nbsp; 4.6 RAG &nbsp;&bull;&nbsp; 4.10 Sequence", styles['TOCSub']), Paragraph("", styles['TOCSub'])],
        [Paragraph("CHAPTER 5: IMPLEMENTATION", styles['TOCItem']), Paragraph("17", styles['TOCItem'])],
        [Paragraph("&nbsp;&nbsp;5.1 Frontend &nbsp;&bull;&nbsp; 5.2 Backend &nbsp;&bull;&nbsp; 5.4 Search &nbsp;&bull;&nbsp; 5.8 Intent Routing &nbsp;&bull;&nbsp; 5.9 Tools &nbsp;&bull;&nbsp; 5.10 Firewall", styles['TOCSub']), Paragraph("", styles['TOCSub'])],
        [Paragraph("CHAPTER 6: TESTING AND RESULTS", styles['TOCItem']), Paragraph("20", styles['TOCItem'])],
        [Paragraph("&nbsp;&nbsp;6.1 Introduction &nbsp;&bull;&nbsp; 6.2 Test Cases (TC01-TC18) &nbsp;&bull;&nbsp; 6.3 Results &nbsp;&bull;&nbsp; 6.7 Limitations", styles['TOCSub']), Paragraph("", styles['TOCSub'])],
        [Paragraph("CHAPTER 7: CONCLUSION AND FUTURE SCOPE", styles['TOCItem']), Paragraph("22", styles['TOCItem'])],
        [Paragraph("&nbsp;&nbsp;7.1 Conclusion &nbsp;&bull;&nbsp; 7.2 Limitations &nbsp;&bull;&nbsp; 7.3 Future Scope", styles['TOCSub']), Paragraph("", styles['TOCSub'])],
        [Paragraph("CHAPTER 8: REFERENCES", styles['TOCItem']), Paragraph("23", styles['TOCItem'])],
        [Paragraph("APPENDIX A: IMPLEMENTATION WORKFLOW AND API RESPONSIBILITIES", styles['TOCItem']), Paragraph("24", styles['TOCItem'])],
        [Paragraph("APPENDIX B: APPLICATION SCREENSHOT PLACEHOLDERS", styles['TOCItem']), Paragraph("25", styles['TOCItem'])],
    ]
    toc_table = Table(toc_data, colWidths=[430, 50])
    toc_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('ALIGN', (1,0), (1,-1), 'RIGHT'),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(toc_table)
    story.append(Spacer(1, 20))
    story.append(Paragraph("<i>Note: Page numbers reflect the complete 27-page academic report structure. All technical corrections (supervisor routing priorities, diagram alignments, grounded summarization, and firewall specifications) have been fully integrated.</i>", styles['Caption']))
    story.append(PageBreak())

    # =========================================================================
    # PAGE 3: CHAPTER 1: INTRODUCTION
    # =========================================================================
    story.append(Paragraph("CHAPTER 1: INTRODUCTION", styles['ChapterHeader']))
    story.append(Paragraph("1.1 Background", styles['SectionHeader']))
    story.append(Paragraph(
        "Academic research requires students and researchers to discover relevant publications, understand technical contributions, "
        "compare methodologies, and identify unanswered questions. These activities often involve searching several scholarly repositories, "
        "downloading papers, reading long PDF documents, recording notes, and preparing literature reviews. When these tasks are performed "
        "manually across separate websites and documents, the process can become time-consuming and difficult to organise.", styles['Body']
    ))
    story.append(Paragraph(
        "Recent advances in large language models (LLMs), information retrieval, document parsing, and vector databases provide opportunities "
        "to support this workflow. Retrieval-Augmented Generation (RAG) combines a retrieval component with language-model generation so that "
        "responses can be informed by selected source material. Tool-using language-model systems can also route a request to a suitable "
        "operation, such as search, summarisation, or document question answering.", styles['Body']
    ))
    story.append(Paragraph(
        "ResearchPilot AI is a web-based academic research assistant. The supplied implementation combines a React and TypeScript frontend "
        "with a Python FastAPI backend, relational storage through SQLite and SQLAlchemy, and a persistent ChromaDB collection for document "
        "retrieval. The application supports academic paper discovery, workspace organisation, PDF upload and extraction, workspace-aware "
        "question answering, and structured research analysis.", styles['Body']
    ))
    story.append(Paragraph(
        "The project uses a Supervisor Agent to classify a research request and invoke one of six existing research tools. This is best described "
        "as a partially agentic architecture: the supervisor makes a bounded routing decision and calls a selected tool, while the tools perform "
        "defined tasks. The code does not establish unrestricted autonomous planning, independent agent-to-agent collaboration, or long-term "
        "autonomous research.", styles['Body']
    ))
    
    story.append(Paragraph("1.2 Problem Statement", styles['SectionHeader']))
    story.append(Paragraph(
        "Students and researchers frequently need to search multiple academic sources, organise papers by topic, extract information from PDFs, "
        "and synthesise findings across publications. These tasks are commonly performed with separate search portals, PDF readers, note-taking "
        "applications, and general-purpose chat interfaces. This fragmentation makes it harder to preserve a clear connection between an analytical "
        "response and the papers that support it.", styles['Body']
    ))
    story.append(Paragraph(
        "General-purpose language models may produce plausible but unsupported statements when they are not grounded in the relevant papers. "
        "A research assistant therefore needs to retrieve relevant document passages, retain source metadata, and make limitations visible when "
        "evidence is unavailable. It should also recognise the type of research task and select a suitable operation without requiring the user "
        "to navigate to a separate tool for every request.", styles['Body']
    ))
    story.append(Paragraph(
        "The problem addressed by ResearchPilot AI is the design and implementation of an integrated academic research platform that combines "
        "paper discovery, workspace-based literature organisation, PDF processing, retrieval-grounded chat, specialised research tools, and "
        "evidence-oriented response checking within a single interface.", styles['Body']
    ))
    
    story.append(Paragraph("1.3 Motivation", styles['SectionHeader']))
    story.append(Paragraph("&bull; To reduce the effort involved in discovering and organising academic literature.", styles['Bullet']))
    story.append(Paragraph("&bull; To provide a separate workspace for each research topic or project.", styles['Bullet']))
    story.append(Paragraph("&bull; To make uploaded PDF content searchable through text extraction, chunking, embeddings, and vector retrieval.", styles['Bullet']))
    story.append(Paragraph("&bull; To help users ask questions about the papers stored in a selected workspace.", styles['Bullet']))
    story.append(Paragraph("&bull; To support structured summarisation, literature synthesis, comparison, and research-gap analysis.", styles['Bullet']))
    story.append(Paragraph("&bull; To make tool selection visible through a Supervisor Agent execution trace.", styles['Bullet']))
    story.append(Paragraph("&bull; To encourage evidence-based responses and expose cases where a claim lacks supporting material.", styles['Bullet']))
    
    story.append(Paragraph("1.4 Objectives", styles['SectionHeader']))
    story.append(Paragraph("&bull; Develop a browser-based academic research application using React, TypeScript, and Vite.", styles['Bullet']))
    story.append(PageBreak())

    # =========================================================================
    # PAGE 4: CHAPTER 1 (CONT.)
    # =========================================================================
    story.append(Paragraph("&bull; Implement backend APIs using Python and FastAPI.", styles['Bullet']))
    story.append(Paragraph("&bull; Provide user authentication and workspace-level organisation of research material.", styles['Bullet']))
    story.append(Paragraph("&bull; Search supported scholarly sources and present paper metadata and access links.", styles['Bullet']))
    story.append(Paragraph("&bull; Extract text from uploaded PDFs using PyPDF and index paper chunks in ChromaDB.", styles['Bullet']))
    story.append(Paragraph("&bull; Implement workspace RAG question answering with retrieved source passages.", styles['Bullet']))
    story.append(Paragraph("&bull; Provide six research tools: academic search, summarisation, literature review, comparison, research-gap identification, and workspace Q&A.", styles['Bullet']))
    story.append(Paragraph("&bull; Implement a Supervisor Agent that identifies intent and routes a query to one appropriate existing tool.", styles['Bullet']))
    story.append(Paragraph("&bull; Display an execution trace containing identified intent, selected tool, routing rationale, and execution status.", styles['Bullet']))
    story.append(Paragraph("&bull; Apply evidence and citation checks to generated research responses.", styles['Bullet']))
    
    story.append(Paragraph("1.5 Scope of the Project", styles['SectionHeader']))
    story.append(Paragraph(
        "The project scope covers a web application for individual academic research workflows. Users can register and sign in, create "
        "workspaces, search academic indexes, import papers into a workspace, upload PDF files, and interact with papers through chat and "
        "analysis tools. The source code includes service modules for arXiv, PubMed, Semantic Scholar, Crossref, CORE, DOAJ, IEEE, ACM, "
        "and conference proceedings sources including NeurIPS, ICML, and ICLR. OpenAlex is utilized within the discovery pipeline as an "
        "open-access URL and DOI metadata enrichment resolver rather than an initial keyword discovery adapter. Actual result availability "
        "depends on each connector and external service.", styles['Body'] # CORRECTION F
    ))
    story.append(Paragraph(
        "The backend includes a PDF extraction and vector-indexing path, section-aware text chunking, ChromaDB storage, and retrieval using "
        "dense and lexical/evidence signals. The embedding implementation attempts to load Sentence Transformers all-MiniLM-L6-v2; when it "
        "cannot load, the code uses deterministic mock vectors. This fallback is operationally important because mock vectors are not "
        "equivalent to semantic embeddings.", styles['Body']
    ))
    story.append(Paragraph(
        "The Supervisor Agent performs bounded intent classification and tool routing. The six routed tools are defined in the source code. "
        "The application should not be represented as a fully autonomous multi-agent system. The project does not claim autonomous multi-step "
        "research planning, independent agent collaboration, or persistent long-term memory beyond the database-backed workspace and chat records.", styles['Body']
    ))
    story.append(PageBreak())

    # =========================================================================
    # PAGE 5: CHAPTER 2: LITERATURE SURVEY
    # =========================================================================
    story.append(Paragraph("CHAPTER 2: LITERATURE SURVEY", styles['ChapterHeader']))
    story.append(Paragraph("2.1 Introduction", styles['SectionHeader']))
    story.append(Paragraph(
        "This chapter reviews research that informs retrieval-augmented generation, tool-using language models, academic information retrieval, "
        "and the detection of unsupported generated content. These works provide conceptual foundations for ResearchPilot AI; they are not "
        "claims that the application reproduces every research method in the cited papers.", styles['Body']
    ))
    story.append(Paragraph("2.2 Review of Existing Research", styles['SectionHeader']))
    
    lit_reviews = [
        ("1. Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks",
         "Authors: Patrick Lewis, Ethan Perez, Aleksandra Piktus, Fabio Petroni, Vladimir Karpukhin, Naman Goyal, Heinrich Küttler, Mike Lewis, Wen-tau Yih, Tim Rocktäschel, Sebastian Riedel, and Douwe Kiela. Year: 2020. Methodology: The paper combines a parametric sequence-to-sequence generator with a non-parametric dense vector index of retrieved passages. Retrieval supplies external evidence that conditions text generation. Application to ResearchPilot AI: This is the main conceptual basis for retrieving relevant chunks from a workspace before answering research questions. Limitation: RAG quality depends on the coverage, relevance, and quality of the indexed corpus and retrieval method; retrieval does not guarantee that the generator will use evidence correctly."),
        ("2. ReAct: Synergizing Reasoning and Acting in Language Models",
         "Authors: Shunyu Yao, Jeffrey Zhao, Dian Yu, Nan Du, Izhak Shafran, Karthik Narasimhan, and Yuan Cao. Year: 2023. Methodology: ReAct interleaves reasoning traces and actions, enabling a language model to interact with tools or environments. Application: The work motivates the separation of intent understanding, tool selection, tool execution, and response synthesis. ResearchPilot AI implements a narrower deterministic intent-routing mechanism rather than the full ReAct loop. Limitation: Tool use can fail through incorrect tool selection, malformed arguments, or unreliable tool outputs; reasoning text alone does not establish correctness."),
        ("3. Toolformer: Language Models Can Teach Themselves to Use Tools",
         "Authors: Timo Schick, Jane Dwivedi-Yu, Roberto Dessì, Roberta Raileanu, Maria Lomeli, Luke Zettlemoyer, Nicola Cancedda, and Thomas Scialom. Year: 2023. Methodology: Toolformer studies how language models can learn when to call APIs and how to incorporate tool responses during language modelling. Application: It provides background for systems that connect a language model to external academic search and document-analysis capabilities. ResearchPilot AI uses a supervisor and explicit tool registry rather than claiming Toolformer-style self-supervised tool learning. Limitation: Tool availability and correctness depend on API design, data quality, permissions, and robust error handling."),
        ("4. Dense Passage Retrieval for Open-Domain Question Answering",
         "Authors: Vladimir Karpukhin, Barlas Oğuz, Sewon Min, Patrick Lewis, Ledell Wu, Sergey Edunov, Danqi Chen, and Wen-tau Yih. Year: 2020. Methodology: Dense Passage Retrieval learns question and passage representations and retrieves passages by vector similarity. Application: This work informs the use of embedding-based retrieval over chunks extracted from research PDFs. ResearchPilot AI uses ChromaDB and a configured sentence-transformer model when available, supplemented by lexical and evidence-oriented scores. Limitation: Dense retrieval depends on embedding quality and domain fit; a model-loading fallback to deterministic mock vectors should not be interpreted as meaningful semantic retrieval."),
        ("5. SelfCheckGPT: Zero-Resource Black-Box Hallucination Detection for Generative Large Language Models",
         "Authors: Potsawee Manakul, Adian Liusie, and Mark Gales. Year: 2023. Methodology: SelfCheckGPT proposes checking consistency across multiple sampled responses as a zero-resource signal for possible hallucinations. Application: It provides a research basis for treating hallucination detection as a separate verification problem after generation. ResearchPilot AI's source implements evidence/citation-oriented checks; it should not be described as implementing the SelfCheckGPT sampling method. Limitation: Consistency is only an indirect signal and may fail to detect consistently repeated false statements.")
    ]
    for title, text in lit_reviews:
        story.append(Paragraph(f"<b>{title}</b>", styles['SubSectionHeader']))
        story.append(Paragraph(text, styles['BodyCompact']))
    story.append(PageBreak())

    # =========================================================================
    # PAGE 6: CHAPTER 2 (CONT.)
    # =========================================================================
    story.append(Paragraph("<b>6. A Survey on Hallucination in Large Language Models: Principles, Taxonomy, Challenges, and Open Questions</b>", styles['SubSectionHeader']))
    story.append(Paragraph(
        "Authors: Lei Huang and co-authors. Year: 2023. Methodology: The survey organises hallucination definitions, causes, detection approaches, "
        "and mitigation strategies for large language models. Application: It supports the design rationale for a separate evidence and citation "
        "verification stage and the need to report uncertainty when supporting passages are absent. Limitation: A survey organises the research "
        "landscape but does not itself provide a universally reliable detector.", styles['BodyCompact']
    ))
    
    story.append(Paragraph("2.3 Literature Comparison Table", styles['SectionHeader']))
    comp_data = [
        [Paragraph("Author / Work", styles['TableHeader']), Paragraph("Year", styles['TableHeader']), Paragraph("Core method", styles['TableHeader']), Paragraph("Relevance to ResearchPilot AI", styles['TableHeader']), Paragraph("Limitation", styles['TableHeader'])],
        [Paragraph("Lewis et al., RAG", styles['TableText']), Paragraph("2020", styles['TableText']), Paragraph("Retrieval + generation", styles['TableText']), Paragraph("Grounded workspace Q&A", styles['TableText']), Paragraph("Depends on corpus and retrieval quality", styles['TableText'])],
        [Paragraph("Yao et al., ReAct", styles['TableText']), Paragraph("2023", styles['TableText']), Paragraph("Reasoning + actions", styles['TableText']), Paragraph("Conceptual basis for bounded routing", styles['TableText']), Paragraph("Tool outputs still need validation", styles['TableText'])],
        [Paragraph("Schick et al., Toolformer", styles['TableText']), Paragraph("2023", styles['TableText']), Paragraph("Learned API use", styles['TableText']), Paragraph("Background for tool-enabled LLMs", styles['TableText']), Paragraph("Not the same as explicit rule routing", styles['TableText'])],
        [Paragraph("Karpukhin et al., DPR", styles['TableText']), Paragraph("2020", styles['TableText']), Paragraph("Dense passage retrieval", styles['TableText']), Paragraph("Embedding-based chunk retrieval", styles['TableText']), Paragraph("Embedding quality affects relevance", styles['TableText'])],
        [Paragraph("Manakul et al., SelfCheckGPT", styles['TableText']), Paragraph("2023", styles['TableText']), Paragraph("Cross-sample consistency checks", styles['TableText']), Paragraph("Hallucination detection motivation", styles['TableText']), Paragraph("Not a direct evidence guarantee", styles['TableText'])],
        [Paragraph("Huang et al., Hallucination Survey", styles['TableText']), Paragraph("2023", styles['TableText']), Paragraph("Taxonomy and review", styles['TableText']), Paragraph("Verification design rationale", styles['TableText']), Paragraph("Survey does not solve detection", styles['TableText'])],
    ]
    comp_table = Table(comp_data, colWidths=[90, 32, 105, 125, 128])
    comp_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#F1F5F9')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#64748B')),
        ('INNERGRID', (0,0), (-1,-1), 0.4, colors.HexColor('#CBD5E1')),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
    ]))
    story.append(comp_table)
    story.append(Spacer(1, 4))

    story.append(Paragraph("2.4 Research Gap", styles['SectionHeader']))
    story.append(Paragraph(
        "Prior work provides strong individual techniques for retrieval, tool use, dense passage search, and hallucination analysis. A student-oriented "
        "research workflow still needs these capabilities to be connected to practical workspace operations. Users need to move from discovery to "
        "PDF ingestion, ask questions over their own papers, and perform synthesis tasks without manually coordinating several disconnected utilities.", styles['BodyCompact']
    ))
    story.append(Paragraph(
        "ResearchPilot AI addresses this integration gap through a workspace-centred application and a bounded Supervisor Agent. Its contribution "
        "is primarily system integration: academic search services, PDF parsing, persistent vector indexing, RAG chat, specialised analysis "
        "functions, and an execution trace are exposed through one application. The evidence firewall further reflects the need to distinguish "
        "generated prose from content that can be tied to retrieved paper evidence.", styles['BodyCompact']
    ))
    story.append(Paragraph(
        "The implementation remains constrained by the reliability of external scholarly sources, PDF text extraction quality, embedding availability, "
        "retrieval ranking, language-model provider availability, and the strength of the evidence checks. These constraints are acknowledged "
        "rather than treated as solved research problems.", styles['BodyCompact']
    ))

    story.append(Paragraph("2.5 References Used in Literature Survey", styles['SectionHeader']))
    survey_refs = [
        "&bull; Lewis, P., et al. (2020). Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks. Advances in Neural Information Processing Systems 33. https://arxiv.org/abs/2005.11401",
        "&bull; Yao, S., et al. (2023). ReAct: Synergizing Reasoning and Acting in Language Models. International Conference on Learning Representations. https://arxiv.org/abs/2210.03629",
        "&bull; Schick, T., et al. (2023). Toolformer: Language Models Can Teach Themselves to Use Tools. Advances in Neural Information Processing Systems 36. https://arxiv.org/abs/2302.04761",
        "&bull; Karpukhin, V., et al. (2020). Dense Passage Retrieval for Open-Domain Question Answering. EMNLP 2020. https://arxiv.org/abs/2004.04906",
        "&bull; Manakul, P., Liusie, A., & Gales, M. (2023). SelfCheckGPT: Zero-Resource Black-Box Hallucination Detection for Generative Large Language Models. EMNLP 2023. https://arxiv.org/abs/2303.08896",
    ]
    for r in survey_refs:
        story.append(Paragraph(r, styles['Bullet']))
    story.append(PageBreak())

    # =========================================================================
    # PAGE 7: CHAPTER 2 (CONT.)
    # =========================================================================
    story.append(Paragraph("&bull; Huang, L., et al. (2023). A Survey on Hallucination in Large Language Models: Principles, Taxonomy, Challenges, and Open Questions. https://arxiv.org/abs/2311.05232", styles['Bullet']))
    story.append(Spacer(1, 15))
    story.append(Paragraph("<i>(Literature Survey references concluded. Proceed to Chapter 3 for problem definition and system specifications.)</i>", styles['Caption']))
    story.append(PageBreak())

    # =========================================================================
    # PAGE 8: CHAPTER 3: PROBLEM DEFINITION AND REQUIREMENTS
    # =========================================================================
    story.append(Paragraph("CHAPTER 3: PROBLEM DEFINITION AND REQUIREMENTS", styles['ChapterHeader']))
    story.append(Paragraph("3.1 Existing System", styles['SectionHeader']))
    story.append(Paragraph(
        "In a conventional research workflow, users search scholarly websites independently, download papers, extract important details manually, "
        "and organise findings in notes or spreadsheets. General-purpose chat assistants may help explain concepts, but unless connected to the "
        "user's papers they may not have access to the exact document content. A researcher may also need separate tools for summarisation, "
        "comparison, and literature review.", styles['Body']
    ))
    story.append(Paragraph("3.2 Limitations of Existing System", styles['SectionHeader']))
    story.append(Paragraph("&bull; Research information is distributed across multiple repositories and applications.", styles['Bullet']))
    story.append(Paragraph("&bull; Manual paper organisation makes it difficult to maintain topic-specific collections.", styles['Bullet']))
    story.append(Paragraph("&bull; Reading and comparing many long PDFs requires significant time.", styles['Bullet']))
    story.append(Paragraph("&bull; General chat responses may not be grounded in the user's selected papers.", styles['Bullet']))
    story.append(Paragraph("&bull; Separate research utilities require repeated context entry and navigation.", styles['Bullet']))
    story.append(Paragraph("&bull; Unverified generated statements or references can reduce confidence in an AI-assisted literature review.", styles['Bullet']))
    story.append(Paragraph("&bull; Scanned or image-only PDFs may not yield extractable text through ordinary text extraction.", styles['Bullet']))

    story.append(Paragraph("3.3 Proposed System", styles['SectionHeader']))
    story.append(Paragraph(
        "ResearchPilot AI integrates the main stages of an academic literature workflow in one web application. A user creates or selects a workspace, "
        "discovers papers through supported academic search connectors, imports relevant publications, and uploads PDFs where required. "
        "Extracted text is segmented into chunks and indexed in ChromaDB. The user can then ask workspace questions or request structured analysis.", styles['Body']
    ))
    story.append(Paragraph(
        "The Supervisor Agent is the control component for research chat requests. It examines the user's wording, selects one of six registered "
        "research tools according to an explicit priority order, invokes that tool, and returns a trace describing the identified intent, selected "
        "tool, routing rationale, and execution status. This is bounded tool orchestration, not unrestricted autonomous planning.", styles['Body']
    ))
    story.append(Paragraph(
        "The Hallucination Firewall is treated as an evidence-oriented validation stage. It checks whether generated research statements and "
        "citations are supported by available retrieved material. The strength of this mechanism depends on the exact verification logic and "
        "available source metadata; it cannot guarantee that every factual statement is correct.", styles['Body']
    ))

    story.append(Paragraph("3.4 Functional Requirements", styles['SectionHeader']))
    fr_data = [
        [Paragraph("ID", styles['TableHeader']), Paragraph("Functional requirement", styles['TableHeader'])],
        [Paragraph("FR01", styles['TableText']), Paragraph("The system shall allow users to register, log in, and access protected application features.", styles['TableText'])],
        [Paragraph("FR02", styles['TableText']), Paragraph("The system shall allow users to create and manage research workspaces.", styles['TableText'])],
        [Paragraph("FR03", styles['TableText']), Paragraph("The system shall search supported academic sources and display paper metadata.", styles['TableText'])],
        [Paragraph("FR04", styles['TableText']), Paragraph("The system shall allow a user to import a paper into a workspace.", styles['TableText'])],
        [Paragraph("FR05", styles['TableText']), Paragraph("The system shall accept PDF uploads and attempt text extraction using PyPDF.", styles['TableText'])],
        [Paragraph("FR06", styles['TableText']), Paragraph("The system shall divide extracted text into chunks and index them in ChromaDB.", styles['TableText'])],
        [Paragraph("FR07", styles['TableText']), Paragraph("The system shall retrieve relevant workspace passages for research questions.", styles['TableText'])],
        [Paragraph("FR08", styles['TableText']), Paragraph("The system shall provide paper summarisation, literature review, comparison, and research-gap analysis.", styles['TableText'])],
        [Paragraph("FR09", styles['TableText']), Paragraph("The Supervisor Agent shall classify a query and route it to one appropriate research tool.", styles['TableText'])],
    ]
    fr_table = Table(fr_data, colWidths=[45, 435])
    fr_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#F1F5F9')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#64748B')),
        ('INNERGRID', (0,0), (-1,-1), 0.4, colors.HexColor('#CBD5E1')),
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
    ]))
    story.append(fr_table)
    story.append(PageBreak())

    # =========================================================================
    # PAGE 9: CHAPTER 3 (CONT.)
    # =========================================================================
    fr_cont_data = [
        [Paragraph("ID", styles['TableHeader']), Paragraph("Functional requirement (continued)", styles['TableHeader'])],
        [Paragraph("FR10", styles['TableText']), Paragraph("The system shall display an execution trace for supervisor-routed requests.", styles['TableText'])],
        [Paragraph("FR11", styles['TableText']), Paragraph("The system shall expose evidence/source metadata for grounded responses where available.", styles['TableText'])],
        [Paragraph("FR12", styles['TableText']), Paragraph("The system shall handle unavailable providers, missing papers, invalid requests, and extraction errors with suitable messages.", styles['TableText'])],
    ]
    fr_cont_table = Table(fr_cont_data, colWidths=[45, 435])
    fr_cont_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#F1F5F9')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#64748B')),
        ('INNERGRID', (0,0), (-1,-1), 0.4, colors.HexColor('#CBD5E1')),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
    ]))
    story.append(fr_cont_table)
    story.append(Spacer(1, 4))

    story.append(Paragraph("3.5 Non-Functional Requirements", styles['SectionHeader']))
    story.append(Paragraph("&bull; <b>Usability:</b> clear navigation between dashboard, workspaces, search, upload, chat, and AI tools.", styles['Bullet']))
    story.append(Paragraph("&bull; <b>Security:</b> authenticated access, password hashing, token-based authorization, and workspace ownership checks.", styles['Bullet']))
    story.append(Paragraph("&bull; <b>Reliability:</b> graceful handling of failed academic connectors, unavailable LLM providers, and unsupported PDF extraction.", styles['Bullet']))
    story.append(Paragraph("&bull; <b>Maintainability:</b> modular FastAPI routers, service classes, SQLAlchemy models, and React page components.", styles['Bullet']))
    story.append(Paragraph("&bull; <b>Performance:</b> retrieval and analysis should complete within practical interactive limits; actual timings require measurement.", styles['Bullet']))
    story.append(Paragraph("&bull; <b>Portability:</b> the frontend should run in modern browsers and the backend in a supported Python environment.", styles['Bullet']))
    story.append(Paragraph("&bull; <b>Evidence quality:</b> responses should identify source material and avoid presenting unsupported content as verified.", styles['Bullet']))

    story.append(Paragraph("3.6 Hardware Requirements", styles['SectionHeader']))
    hw_data = [
        [Paragraph("Component", styles['TableHeader']), Paragraph("Suggested development requirement", styles['TableHeader'])],
        [Paragraph("Processor", styles['TableText']), Paragraph("Modern dual-core processor or better", styles['TableText'])],
        [Paragraph("RAM", styles['TableText']), Paragraph("8 GB recommended; additional memory may be useful for local embedding models", styles['TableText'])],
        [Paragraph("Storage", styles['TableText']), Paragraph("Space for source code, uploaded PDFs, SQLite database, and ChromaDB index", styles['TableText'])],
        [Paragraph("Internet", styles['TableText']), Paragraph("Required for hosted LLM providers and remote academic search sources", styles['TableText'])],
        [Paragraph("Display", styles['TableText']), Paragraph("Standard laptop or desktop display", styles['TableText'])],
    ]
    hw_table = Table(hw_data, colWidths=[110, 370])
    hw_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#F1F5F9')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#64748B')),
        ('INNERGRID', (0,0), (-1,-1), 0.4, colors.HexColor('#CBD5E1')),
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
    ]))
    story.append(hw_table)
    story.append(Spacer(1, 4))

    story.append(Paragraph("3.7 Software Requirements", styles['SectionHeader']))
    sw_data = [
        [Paragraph("Software / Service", styles['TableHeader']), Paragraph("Purpose", styles['TableHeader'])],
        [Paragraph("React 19, TypeScript, Vite", styles['TableText']), Paragraph("Frontend interface and development server", styles['TableText'])],
        [Paragraph("Python 3.9+ / FastAPI / Uvicorn", styles['TableText']), Paragraph("Backend APIs and application server", styles['TableText'])],
        [Paragraph("SQLite / SQLAlchemy", styles['TableText']), Paragraph("Relational persistence and ORM", styles['TableText'])],
        [Paragraph("ChromaDB", styles['TableText']), Paragraph("Persistent vector storage and retrieval", styles['TableText'])],
        [Paragraph("PyPDF", styles['TableText']), Paragraph("Text extraction from uploaded PDF documents", styles['TableText'])],
        [Paragraph("Sentence Transformers", styles['TableText']), Paragraph("Embedding generation when model is available (fallback: deterministic vectors)", styles['TableText'])],
        [Paragraph("Groq LLaMA 3.3 70B Versatile", styles['TableText']), Paragraph("Configured primary LLM model", styles['TableText'])],
        [Paragraph("Gemini / OpenRouter / Ollama", styles['TableText']), Paragraph("Additional provider paths configured in the LLM service, subject to settings", styles['TableText'])],
        [Paragraph("Git / Code editor / Browser", styles['TableText']), Paragraph("Development, version control, and application access", styles['TableText'])],
    ]
    sw_table = Table(sw_data, colWidths=[160, 320])
    sw_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#F1F5F9')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#64748B')),
        ('INNERGRID', (0,0), (-1,-1), 0.4, colors.HexColor('#CBD5E1')),
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
    ]))
    story.append(sw_table)
    story.append(PageBreak())

    # =========================================================================
    # PAGE 10: CHAPTER 4: SYSTEM DESIGN
    # =========================================================================
    story.append(Paragraph("CHAPTER 4: SYSTEM DESIGN", styles['ChapterHeader']))
    story.append(Paragraph("4.1 Overall System Architecture", styles['SectionHeader']))
    story.append(Paragraph(
        "The architecture is divided into a browser-based presentation layer, FastAPI application layer, service layer, relational persistence layer, "
        "vector retrieval layer, and external provider layer. React components communicate with backend endpoints. The backend validates the user "
        "and workspace context, then calls the relevant service. Relational entities are stored through SQLAlchemy, while extracted paper chunks "
        "and their embeddings are stored in ChromaDB.", styles['Body']
    ))
    story.append(Paragraph(
        "The LLM service is configured with Groq and the model name llama-3.3-70b-versatile. The implementation also contains provider functions "
        "for Gemini, OpenRouter, and Ollama. The provider chain may attempt alternatives depending on configuration; the AI_TOOLS_GROQ_ONLY setting "
        "can restrict the chain. Therefore, the report identifies Groq as the configured primary model and describes other providers as conditional "
        "fallbacks, not guaranteed active services.", styles['Body']
    ))
    
    story.append(build_diagrams.build_fig_4_1())
    story.append(Paragraph("Figure 4.1: High-level architecture of ResearchPilot AI.", styles['Caption']))
    
    story.append(Paragraph("4.2 Supervisor Agent Architecture", styles['SectionHeader']))
    story.append(Paragraph(
        "The Supervisor Agent is implemented in the backend service supervisor_agent.py. It receives a research query together with workspace and "
        "session identifiers. It loads papers belonging to the active workspace, optionally narrows the paper set when selected paper identifiers "
        "are supplied, and calls the intent-classification method. The selected tool is then executed through a corresponding method.", styles['Body']
    ))
    story.append(Paragraph(
        "The classifier uses ordered text-pattern rules evaluated in strict hierarchical priority: Comparison has the highest priority (Priority 1), "
        "followed by literature review (Priority 2), paper summarisation (Priority 3), research-gap identification (Priority 4), explicit academic "
        "search (Priority 5), and finally workspace question answering (Priority 6). This priority matters when a query contains more than one "
        "task-related phrase. The supervisor returns an execution banner that includes the detected intent, selected tool, reasoning text, and "
        "execution status.", styles['Body'] # CORRECTION A
    ))
    story.append(PageBreak())

    # =========================================================================
    # PAGE 11: CHAPTER 4 (CONT.)
    # =========================================================================
    story.append(build_diagrams.build_fig_4_2()) # CORRECTION B: Search bypasses LLM/Firewall!
    story.append(Paragraph("Figure 4.2: Supervisor Agent intent classification and tool routing.", styles['Caption']))
    
    story.append(Paragraph("4.3 Agent Roles and Responsibilities", styles['SectionHeader']))
    roles_data = [
        [Paragraph("Component", styles['TableHeader']), Paragraph("Responsibility", styles['TableHeader']), Paragraph("Output", styles['TableHeader'])],
        [Paragraph("Supervisor Agent", styles['TableText']), Paragraph("Classifies the user's research intention and selects one registered tool", styles['TableText']), Paragraph("Intent, tool selection, reasoning, execution status", styles['TableText'])],
        [Paragraph("Academic Paper Search", styles['TableText']), Paragraph("Calls the hybrid search service and formats paper metadata (bypasses LLM)", styles['TableText']), Paragraph("Search results and access links", styles['TableText'])],
        [Paragraph("Paper Summarization", styles['TableText']), Paragraph("Builds a paper evidence payload and requests a structured summary", styles['TableText']), Paragraph("Summary of objectives, methods, dataset, findings, limitations", styles['TableText'])],
        [Paragraph("Literature Review", styles['TableText']), Paragraph("Collects workspace paper evidence and synthesises themes", styles['TableText']), Paragraph("Cross-paper literature review", styles['TableText'])],
        [Paragraph("Paper Comparison", styles['TableText']), Paragraph("Prepares paper payloads and requests comparative analysis", styles['TableText']), Paragraph("Comparative matrix / narrative", styles['TableText'])],
        [Paragraph("Research Gap Identification", styles['TableText']), Paragraph("Analyses evidence from workspace papers", styles['TableText']), Paragraph("Potential gaps, limitations, and open questions", styles['TableText'])],
        [Paragraph("Workspace RAG Q&A", styles['TableText']), Paragraph("Retrieves relevant chunks and generates a grounded answer", styles['TableText']), Paragraph("Answer with source context", styles['TableText'])],
        [Paragraph("Hallucination Firewall", styles['TableText']), Paragraph("Passively checks claim and citation support against available evidence", styles['TableText']), Paragraph("Retained, flagged, or qualified response with audit stats", styles['TableText'])],
    ]
    roles_table = Table(roles_data, colWidths=[100, 220, 160])
    roles_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#F1F5F9')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#64748B')),
        ('INNERGRID', (0,0), (-1,-1), 0.4, colors.HexColor('#CBD5E1')),
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
    ]))
    story.append(roles_table)
    story.append(Spacer(1, 4))

    story.append(Paragraph("4.4 Intent Classification and Tool Selection", styles['SectionHeader']))
    story.append(Paragraph(
        "The implementation defines six tool identifiers: paper_comparison, literature_review, paper_summarization, research_gap_identification, "
        "academic_paper_search, and workspace_qa. The supervisor uses regular-expression patterns and a fixed priority order rather than an "
        "unconstrained agent planner. It also extracts search terms and attempts to match a paper title mentioned by the user to a paper in the "
        "workspace using multi-tier heuristics (quotes, substrings, and word overlap).", styles['Body']
    ))
    story.append(Paragraph(
        "Table 4.2 shows the routing map in exact execution order. When a user request satisfies higher-priority comparison or review patterns, "
        "those analytical tools are executed first. Specific single-paper summary directives take precedence over general limitation queries, while "
        "explicit repository search terms invoke academic discovery. Unmatched factual or conceptual questions default to conversational workspace RAG.", styles['Body']
    ))
    story.append(PageBreak())

    # =========================================================================
    # PAGE 12: CHAPTER 4 (CONT.) - CORRECTION A: EXACT PRIORITY TABLE 4.2
    # =========================================================================
    routing_data = [
        [Paragraph("Priority", styles['TableHeader']), Paragraph("User intention / pattern triggers", styles['TableHeader']), Paragraph("Selected tool", styles['TableHeader'])],
        [Paragraph("1", styles['TableText']), Paragraph("Compare / contrast / versus / comparative matrix / side by side", styles['TableText']), Paragraph("Paper Comparison", styles['TableText'])],
        [Paragraph("2", styles['TableText']), Paragraph("Literature review / synthesize papers / thematic review / SOTA review", styles['TableText']), Paragraph("Literature Review", styles['TableText'])],
        [Paragraph("3", styles['TableText']), Paragraph("Summarize / provide summary / key contributions / brief overview", styles['TableText']), Paragraph("Paper Summarization", styles['TableText'])],
        [Paragraph("4", styles['TableText']), Paragraph("Explicitly identify, find, detect, uncover, or explore research gaps, open questions, and unaddressed research problems", styles['TableText']), Paragraph("Research Gap Identification", styles['TableText'])],
        [Paragraph("5", styles['TableText']), Paragraph("Search or discover academic papers / search arXiv / find literature", styles['TableText']), Paragraph("Academic Paper Search", styles['TableText'])],
        [Paragraph("6", styles['TableText']), Paragraph("Specific conceptual or factual question about workspace papers (default)", styles['TableText']), Paragraph("Workspace RAG Q&A", styles['TableText'])],
    ]
    routing_table = Table(routing_data, colWidths=[38, 302, 140])
    routing_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#F1F5F9')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#64748B')),
        ('INNERGRID', (0,0), (-1,-1), 0.4, colors.HexColor('#CBD5E1')),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
    ]))
    story.append(routing_table)
    story.append(Spacer(1, 4))

    story.append(Paragraph("4.5 Research Tool Execution Workflow", styles['SectionHeader']))
    story.append(Paragraph(
        "After selecting a tool, the supervisor calls only the corresponding execution method for that request. Academic search invokes the hybrid "
        "search service. Summarisation, review, comparison, and gap analysis build evidence payloads from selected workspace papers and pass them "
        "to the LLM service. Workspace Q&A retrieves up to eight relevant chunks by default, or retrieves chunks from explicitly selected papers, "
        "then supplies the query, chat history, and paper metadata to the RAG generation method.", styles['BodyCompact']
    ))
    story.append(Paragraph(
        "The implementation includes checks for insufficient input. Literature review and comparison require at least two papers. If no paper is "
        "available for summarisation or gap analysis, the response asks the user to upload or import papers rather than inventing an analysis. "
        "The number of papers included in some operations is bounded in code: up to six for literature review and gap analysis, and up to five for comparison.", styles['BodyCompact']
    ))

    story.append(Paragraph("4.6 RAG Architecture", styles['SectionHeader']))
    story.append(Paragraph(
        "The PDF path extracts text from uploaded files using PyPDF. The vector service detects common academic section headings and divides text "
        "into paragraph-aware chunks. The configured default chunk size is 850 characters with 160 characters of overlap. Each chunk is associated "
        "with metadata such as paper identifier, workspace identifier, chunk index, title, and section. Embeddings are stored in a persistent "
        "ChromaDB collection named research_papers.", styles['BodyCompact']
    ))
    story.append(Paragraph(
        "The embedding helper attempts to load sentence-transformers/all-MiniLM-L6-v2. If the package or model cannot be loaded, it falls back to "
        "deterministic hash-derived vectors. This fallback permits the indexing code to continue, but it is not semantic embedding inference. "
        "Retrieval also includes keyword and evidence scoring. A combined score in the vector service weights dense score, keyword score, and "
        "evidence score; the code uses 0.45, 0.35, and 0.20 respectively in the scoring path.", styles['BodyCompact']
    ))
    
    story.append(build_diagrams.build_fig_4_3())
    story.append(Paragraph("Figure 4.3: PDF processing, chunking, embedding, and RAG retrieval.", styles['Caption']))
    story.append(PageBreak())

    # =========================================================================
    # PAGE 13: CHAPTER 4 (CONT.)
    # =========================================================================
    story.append(Paragraph("4.7 Hallucination Firewall Architecture", styles['SectionHeader']))
    story.append(Paragraph(
        "The LLM service contains an evidence-oriented response verification stage referred to in the implementation as a hallucination firewall. "
        "Its purpose is to reduce unsupported claims and citation mismatches by checking generated content against evidence and source metadata "
        "available to the response pipeline. It functions as a passive evidence auditor and accounting safeguard, not a mathematical proof of truth.", styles['Body'] # CORRECTION D
    ))
    story.append(Paragraph(
        "The firewall must be interpreted within the limits of the indexed corpus. If a paper is missing, a PDF is scanned, extraction is incomplete, "
        "or retrieval selects irrelevant chunks, the verification stage may not have sufficient evidence. A citation that points to a retrieved chunk "
        "can still be misinterpreted by the model. The system flags unsupported claims with an audit warning rather than attempting an autonomous "
        "text revision, making limitations transparent to the researcher.", styles['Body'] # CORRECTION D
    ))
    
    story.append(build_diagrams.build_fig_4_4()) # CORRECTION D: Passive auditor, no rewrite
    story.append(Paragraph("Figure 4.4: Evidence and citation verification concept.", styles['Caption']))
    
    story.append(Paragraph("4.8 Database Design", styles['SectionHeader']))
    story.append(Paragraph(
        "The relational model uses SQLAlchemy entities. The User entity stores account identity and password hash. A user owns multiple workspaces. "
        "A workspace contains papers, documents, and chat sessions. A chat session belongs to a user and a workspace and contains ordered chat messages. "
        "Paper records store bibliographic metadata, access URLs, local file path, extracted text, indexing status, and workspace association. "
        "Document records store generated outputs such as summaries, insights, literature reviews, comparisons, and reviews.", styles['Body']
    ))
    story.append(Paragraph(
        "ChromaDB is separate from the relational database. It stores vectorized chunks and metadata used for retrieval. The SQLite database stores "
        "application entities and does not replace the vector index.", styles['Body']
    ))
    story.append(PageBreak())

    # =========================================================================
    # PAGE 14: CHAPTER 4 (CONT.) - CORRECTION E: doc_type
    # =========================================================================
    story.append(build_diagrams.build_fig_4_5()) # CORRECTION E: doc_type
    story.append(Paragraph("Figure 4.5: Simplified relational data model based on SQLAlchemy entities.", styles['Caption']))
    
    story.append(Paragraph("4.9 Data Flow Diagram – Level 0", styles['SectionHeader']))
    story.append(Paragraph(
        "At Level 0, the researcher is the primary external actor. The user sends a query, upload, or workspace action to ResearchPilot AI and "
        "receives answers, paper metadata, and execution traces. The system may communicate with academic sources for paper discovery and with "
        "an LLM provider for generation. Uploaded PDF content is processed within the application.", styles['Body']
    ))
    
    story.append(build_diagrams.build_fig_4_6())
    story.append(Paragraph("Figure 4.6: DFD Level 0 – Context diagram.", styles['Caption']))
    story.append(PageBreak())

    # =========================================================================
    # PAGE 15: CHAPTER 4 (CONT.)
    # =========================================================================
    story.append(Paragraph("4.9 Data Flow Diagram – Level 1", styles['SectionHeader']))
    story.append(Paragraph(
        "At Level 1, the user request first passes through authentication and workspace-access checks. The relevant router or supervisor "
        "dispatches the request. Search requests use academic connectors; upload requests use PDF extraction and vector indexing; research "
        "questions use retrieval and analysis tools. The LLM service generates the requested content and the evidence-verification logic "
        "checks support before the response is returned.", styles['Body']
    ))
    
    story.append(build_diagrams.build_fig_4_7())
    story.append(Paragraph("Figure 4.7: DFD Level 1 – Internal processing.", styles['Caption']))
    
    story.append(Paragraph("4.10 Sequence Diagram", styles['SectionHeader']))
    story.append(Paragraph(
        "The sequence diagram represents the supervisor-assisted chat flow. The browser submits a query to FastAPI, which validates user and "
        "workspace access before dispatching to the Supervisor Agent. The supervisor classifies intent and invokes the selected tool. The tool "
        "retrieves ChromaDB chunks or external metadata, requesting LLM generation and firewall verification where applicable. The grounded "
        "result returns through the supervisor, which prepends the decision trace banner. FastAPI persists the exchange in the SQLite database "
        "and returns the response to the browser.", styles['Body'] # CORRECTION C
    ))
    story.append(PageBreak())

    # =========================================================================
    # PAGE 16: CHAPTER 4 (CONT.) - CORRECTION C: SEQUENCE FLOW
    # =========================================================================
    story.append(build_diagrams.build_fig_4_8()) # CORRECTION C: sequence flow
    story.append(Paragraph("Figure 4.8: Sequence diagram for a supervisor-assisted research query.", styles['Caption']))
    
    story.append(Paragraph("4.11 Use Case Diagram", styles['SectionHeader']))
    story.append(Paragraph(
        "The primary actor is the student or researcher. The user can manage an account, create or select a workspace, search and import papers, "
        "upload PDFs, chat with workspace literature, and run structured research analysis. Academic indexes are external systems used during paper discovery.", styles['Body']
    ))
    
    story.append(build_diagrams.build_fig_4_9())
    story.append(Paragraph("Figure 4.9: Use case view of ResearchPilot AI.", styles['Caption']))
    story.append(PageBreak())

    # =========================================================================
    # PAGE 17: CHAPTER 5: IMPLEMENTATION
    # =========================================================================
    story.append(Paragraph("CHAPTER 5: IMPLEMENTATION", styles['ChapterHeader']))
    story.append(Paragraph("5.1 Frontend Implementation", styles['SectionHeader']))
    story.append(Paragraph(
        "The frontend is implemented using React 19, TypeScript, and Vite. React Router DOM provides page navigation. Axios is used as the API "
        "client, and the application includes authentication and chat contexts. The available pages include Home, Login, Register, Dashboard, "
        "Workspace, DocSpace, SearchPapers, UploadPDF, ResearchChat, and AITools. Tailwind CSS is present in the frontend dependencies and styling "
        "configuration; the project prompt permits CSS or Tailwind according to the existing implementation.", styles['BodyCompact']
    ))
    story.append(Paragraph(
        "The frontend separates page-level workflows from reusable components such as the header, sidebar, protected route, markdown renderer, "
        "and floating assistant. The authentication context supports user session state and protected navigation. Chat context coordinates chat "
        "state and message submission.", styles['BodyCompact']
    ))
    
    story.append(Paragraph("5.2 Backend Implementation", styles['SectionHeader']))
    story.append(Paragraph(
        "The backend uses FastAPI and Uvicorn. Application startup registers routers for authentication, workspaces, papers, chat, assistant, "
        "tools, and system operations. SQLAlchemy provides relational persistence and dependency-managed database sessions. Pydantic schemas "
        "validate request and response structures. The service layer contains the academic source connectors, hybrid search, vector indexing, "
        "LLM provider calls, supervisor routing, and evidence guard logic.", styles['BodyCompact']
    ))
    story.append(Paragraph(
        "Authentication uses password hashing and JWT-based access control. Protected endpoints obtain the current user and check workspace "
        "ownership before accessing workspace papers or documents. Environment configuration is loaded through Pydantic settings. Secrets and "
        "provider keys should be supplied through environment variables rather than embedded in source code.", styles['BodyCompact']
    ))

    story.append(Paragraph("5.3 Database and Workspace Management", styles['SectionHeader']))
    story.append(Paragraph(
        "The User, Workspace, Paper, Document, ChatSession, and ChatMessage models form the principal relational data model. A workspace is owned "
        "by one user and can contain multiple papers, generated documents, and chat sessions. Workspace scoping is important because it prevents "
        "a research query from silently mixing documents from unrelated research projects.", styles['BodyCompact']
    ))
    story.append(Paragraph(
        "Chat sessions preserve message records in the relational database. The assistant endpoint can also accept a bounded recent history in "
        "the request. These mechanisms provide conversation context for an active research interaction; they should not be described as "
        "autonomous long-term memory or a self-updating knowledge graph.", styles['BodyCompact']
    ))

    story.append(Paragraph("5.4 Academic Paper Search Implementation", styles['SectionHeader']))
    story.append(Paragraph(
        "The HybridSearchService coordinates several source adapters concurrently. The source code queries nine initial discovery providers: "
        "API-backed services (arXiv, PubMed, Semantic Scholar, Crossref, CORE, DOAJ) and web scrapers (IEEE, ACM, and conference proceedings for "
        "NeurIPS, ICML, and ICLR). OpenAlex is integrated as a secondary resolver during access-URL enrichment rather than an initial discovery "
        "connector. It gathers results, tolerates individual provider exceptions, filters to approved sources, deduplicates records, enriches "
        "access URLs, ranks results, and diversifies the final list.", styles['BodyCompact'] # CORRECTION F
    ))
    story.append(Paragraph(
        "Source coverage depends on live service availability, rate limits, access rules, and connector configuration. Although the user-provided "
        "project brief mentions other academic sources, only the connectors present in the uploaded repository are described here. Crossref and "
        "PubMed are confirmed by the service modules; Semantic Scholar and arXiv are also present.", styles['BodyCompact']
    ))

    story.append(Paragraph("5.5 PDF Processing and Vector Storage", styles['SectionHeader']))
    story.append(Paragraph(
        "The paper upload endpoint accepts PDF files, stores them in the configured upload directory, and extracts text with PyPDF. If no text "
        "can be extracted, the endpoint returns an error indicating that the file may be scanned or image-only. A Paper record is created with "
        "the extracted text and local file path, then the vector service indexes the content.", styles['BodyCompact']
    ))
    story.append(Paragraph(
        "The vector service detects common section labels including abstract, introduction, methodology, results, limitations, future work, "
        "and references. It uses paragraph-aware chunking with a default size of 850 characters and overlap of 160 characters. Chunk metadata "
        "supports later retrieval and source attribution. ChromaDB persists the research_papers collection under the configured data directory.", styles['BodyCompact']
    ))
    story.append(PageBreak())

    # =========================================================================
    # PAGE 18: CHAPTER 5 (CONT.) - CORRECTIONS D, G, H
    # =========================================================================
    story.append(Paragraph("5.6 RAG-Based Research Chat", styles['SectionHeader']))
    story.append(Paragraph(
        "For a normal workspace question, the vector service searches the active workspace and returns up to eight chunks. If specific paper "
        "identifiers are selected, the service retrieves chunks from those papers instead. The LLM generation function receives the user "
        "question, retrieved content, chat history, and active paper metadata. The assistant API response includes a grounded flag and source "
        "descriptors containing paper ID, title, chunk index, and section where available.", styles['BodyCompact']
    ))
    story.append(Paragraph(
        "The assistant endpoint also recognises broad-context requests such as 'summarize my uploaded papers', 'compare papers', or 'literature review' "
        "and can assemble a broader set of workspace chunks. The chat experience should be understood as retrieval-grounded generation rather than "
        "a guarantee that every generated sentence is fully supported.", styles['BodyCompact']
    ))

    story.append(Paragraph("5.7 Supervisor Agent Implementation", styles['SectionHeader']))
    story.append(Paragraph(
        "The ResearchSupervisorAgent class defines the six tool identifiers and metadata. Its run method obtains workspace papers, narrows them "
        "to selected paper IDs when supplied, classifies the user's intent, and invokes the matching execution method. The response is prefixed "
        "with a supervisor banner showing intent, tool, reasoning, and execution status.", styles['BodyCompact']
    ))
    story.append(Paragraph(
        "The supervisor is a bounded controller. It does not generate an open-ended research plan, create new tools, or delegate work to "
        "independent autonomous agents. It selects one existing tool for the current request. The tool itself may perform retrieval and call "
        "the LLM service, but this does not establish multi-agent communication.", styles['BodyCompact']
    ))

    story.append(Paragraph("5.8 Intent Classification and Tool Routing", styles['SectionHeader']))
    story.append(Paragraph(
        "The classifier normalises user queries to lowercase and applies ordered regular-expression pattern matching. The execution order is "
        "deterministic: (1) Paper Comparison, (2) Literature Review, (3) Paper Summarization, (4) Research Gap Identification, (5) Academic "
        "Paper Search, and (6) Workspace RAG Q&A.", styles['BodyCompact'] # CORRECTION H
    ))
    story.append(Paragraph(
        "A critical design consideration is intent disambiguation when queries mix multiple keywords. For instance, a query such as 'Summarize the "
        "methodology, dataset, and limitations of paper X' contains both the verb 'summarize' and the keyword 'limitations'. Under the supervisor's "
        "priority rules, explicit summarization directives take precedence, preventing the query from being misrouted to Research Gap Identification. "
        "Conversely, Research Gap Identification requires explicit exploratory directives (e.g., identify, detect, uncover, unaddressed). "
        "Similarly, queries containing phrases like 'papers on deep learning' will not trigger external academic search if the user explicitly "
        "asked to 'identify gaps' or 'compare'. If a query mentions a specific paper, _extract_target_paper_title() resolves the paper record using "
        "quoted titles, exact substrings, normalized alphanumeric tokens, or stopword-filtered set overlap before tool invocation.", styles['BodyCompact'] # CORRECTION H
    ))

    story.append(Paragraph("5.9 AI Research Tools Implementation", styles['SectionHeader']))
    story.append(Paragraph(
        "Academic Paper Search calls the hybrid search service and formats preprint titles, authors, venues, publication dates, and access URLs "
        "directly into Markdown without invoking the LLM or firewall. Paper Summarization extracts up to eight relevant chunks for the resolved paper "
        "and requests a strictly structured summary containing five mandatory sections: ### Objective, ### Methodology, ### Dataset, ### Key Findings, "
        "and ### Limitations. Every factual assertion must append an inline evidence citation tag formatted as [P{paper_id}-C{chunk_index} | {Title}]. "
        "If retrieved chunks lack information for a given heading, the system explicitly outputs 'Not specified in the available paper content.' "
        "rather than generating speculative filler. Literature Review prepares evidence from up to six workspace papers and requests a thematic "
        "synthesis. Paper Comparison prepares up to five papers and constructs a side-by-side Markdown comparison matrix. Research Gap Identification "
        "analyzes methodology and limitation chunks across up to six workspace papers, categorizing open challenges with grounded paper citations.", styles['BodyCompact'] # CORRECTION G
    ))

    story.append(Paragraph("5.10 Hallucination Firewall", styles['SectionHeader']))
    story.append(Paragraph(
        "The LLM service implements a post-generation verification component termed the Automated Hallucination Firewall. Following text generation, "
        "_extract_hallucination_stats() segments the report into individual sentences and audits them against retrieved evidence citations. Sentences "
        "bearing explicit chunk citations ([P\\d+-C\\d+]) are classified as Directly Supported; sentences containing cautious phrasing (may, might, "
        "suggests) are classified as Inferred; and ungrounded statements are classified as Needs Review or Unsupported.", styles['BodyCompact'] # CORRECTION D
    ))
    story.append(PageBreak())

    # =========================================================================
    # PAGE 19: CHAPTER 5 (CONT.)
    # =========================================================================
    story.append(Paragraph(
        "The firewall calculates the exact percentage of paper-grounded claims and appends an audit block to the response. If unsupported "
        "statements exceed 10%, a visible warning banner is attached advising the user to inspect the source material. The firewall acts as an "
        "inspectable evidence-accounting mechanism; it does not autonomously rewrite generated text or guarantee absolute external factual truth.", styles['Body'] # CORRECTION D
    ))
    story.append(Spacer(1, 10))

    story.append(Paragraph("5.11 User Interface and Screenshots", styles['SectionHeader']))
    story.append(Paragraph(
        "The uploaded repository contains frontend page components but does not include a complete set of real application screenshots "
        "suitable for insertion into the report. The following figure spaces are therefore intentionally marked as screenshot placeholders. "
        "Replace each placeholder with a screenshot captured from the running project before final submission. No fabricated UI images are "
        "presented as actual application evidence.", styles['Body']
    ))
    story.append(Spacer(1, 4))
    
    figures_list = [
        "Figure 5.1: Login page – [INSERT ACTUAL SCREENSHOT]",
        "Figure 5.2: Dashboard – [INSERT ACTUAL SCREENSHOT]",
        "Figure 5.3: Workspace management – [INSERT ACTUAL SCREENSHOT]",
        "Figure 5.4: Academic paper search – [INSERT ACTUAL SCREENSHOT]",
        "Figure 5.5: PDF upload – [INSERT ACTUAL SCREENSHOT]",
        "Figure 5.6: Research Chat – [INSERT ACTUAL SCREENSHOT]",
        "Figure 5.7: Supervisor Agent execution trace – [INSERT ACTUAL SCREENSHOT]",
        "Figure 5.8: Paper summarization – [INSERT ACTUAL SCREENSHOT]",
        "Figure 5.9: Research gap analysis – [INSERT ACTUAL SCREENSHOT]",
        "Figure 5.10: Literature review – [INSERT ACTUAL SCREENSHOT]",
        "Figure 5.11: Paper comparison – [INSERT ACTUAL SCREENSHOT]",
    ]
    for fig_str in figures_list:
        story.append(Paragraph(f"&bull; {fig_str}", styles['Bullet']))
    story.append(PageBreak())

    # =========================================================================
    # PAGE 20: CHAPTER 6: TESTING AND RESULTS
    # =========================================================================
    story.append(Paragraph("CHAPTER 6: TESTING AND RESULTS", styles['ChapterHeader']))
    story.append(Paragraph("6.1 Introduction", styles['SectionHeader']))
    story.append(Paragraph(
        "Testing is required to verify authentication, workspace isolation, paper discovery, PDF extraction, vector indexing, retrieval, "
        "research-tool routing, LLM generation, and evidence checking. The repository includes test scripts named test_supervisor.py and "
        "test_agent_execution.py. These scripts define intent-classification checks and tool-execution scenarios. The presence of test scripts is "
        "not, by itself, proof that the tests were executed successfully in the environment used to prepare this report.", styles['Body']
    ))
    story.append(Paragraph(
        "This report therefore distinguishes test scenarios visible in the source code from actual execution evidence. No new test run, performance "
        "measurement, accuracy score, or deployment validation is claimed here.", styles['Body']
    ))

    story.append(Paragraph("6.2 Test Cases", styles['SectionHeader']))
    tc_data = [
        [Paragraph("Test ID", styles['TableHeader']), Paragraph("Input / Action", styles['TableHeader']), Paragraph("Expected output", styles['TableHeader']), Paragraph("Actual result / status", styles['TableHeader'])],
        [Paragraph("TC01", styles['TableText']), Paragraph("Register with valid account details", styles['TableText']), Paragraph("Account created and authenticated", styles['TableText']), Paragraph("Not independently executed – To be verified", styles['TableText'])],
        [Paragraph("TC02", styles['TableText']), Paragraph("Login with valid credentials", styles['TableText']), Paragraph("Access token/session returned", styles['TableText']), Paragraph("Not independently executed – To be verified", styles['TableText'])],
        [Paragraph("TC03", styles['TableText']), Paragraph("Access a workspace owned by another user", styles['TableText']), Paragraph("Access denied", styles['TableText']), Paragraph("To be verified", styles['TableText'])],
        [Paragraph("TC04", styles['TableText']), Paragraph("Create and select a workspace", styles['TableText']), Paragraph("Workspace appears in workspace list", styles['TableText']), Paragraph("To be verified", styles['TableText'])],
        [Paragraph("TC05", styles['TableText']), Paragraph("Search academic papers by topic", styles['TableText']), Paragraph("Relevant paper metadata and source links displayed", styles['TableText']), Paragraph("To be verified", styles['TableText'])],
        [Paragraph("TC06", styles['TableText']), Paragraph("Upload a text-based PDF", styles['TableText']), Paragraph("Text extracted and paper record created", styles['TableText']), Paragraph("To be verified", styles['TableText'])],
        [Paragraph("TC07", styles['TableText']), Paragraph("Upload scanned/image-only PDF", styles['TableText']), Paragraph("Clear extraction failure message", styles['TableText']), Paragraph("Expected behaviour from route; verify", styles['TableText'])],
        [Paragraph("TC08", styles['TableText']), Paragraph("Ask a factual question about indexed papers", styles['TableText']), Paragraph("Retrieved context and grounded answer returned", styles['TableText']), Paragraph("To be verified", styles['TableText'])],
        [Paragraph("TC09", styles['TableText']), Paragraph("Request a paper summary with no papers in workspace", styles['TableText']), Paragraph("Prompt to upload or import a paper", styles['TableText']), Paragraph("Defined in source; execution not independently verified", styles['TableText'])],
        [Paragraph("TC10", styles['TableText']), Paragraph("Request literature review with fewer than two papers", styles['TableText']), Paragraph("Insufficient-paper message displayed", styles['TableText']), Paragraph("Defined in source; execution not independently verified", styles['TableText'])],
        [Paragraph("TC11", styles['TableText']), Paragraph("Ask to compare two papers", styles['TableText']), Paragraph("Paper Comparison tool selected", styles['TableText']), Paragraph("Test script includes scenario; execution not independently verified", styles['TableText'])],
        [Paragraph("TC12", styles['TableText']), Paragraph("Ask to identify research gaps", styles['TableText']), Paragraph("Research Gap Identification selected", styles['TableText']), Paragraph("Test script includes scenario; execution not independently verified", styles['TableText'])],
        [Paragraph("TC13", styles['TableText']), Paragraph("Ask to search for recent papers", styles['TableText']), Paragraph("Academic Paper Search selected", styles['TableText']), Paragraph("Test script includes scenario; execution not independently verified", styles['TableText'])],
        [Paragraph("TC14", styles['TableText']), Paragraph("Ask a generic paper question", styles['TableText']), Paragraph("Workspace RAG Q&A selected", styles['TableText']), Paragraph("Test script includes scenario; execution not independently verified", styles['TableText'])],
        [Paragraph("TC15", styles['TableText']), Paragraph("Make a non-academic request", styles['TableText']), Paragraph("Research-scope guard rejects obvious out-of-scope request", styles['TableText']), Paragraph("To be verified", styles['TableText'])],
        [Paragraph("TC16", styles['TableText']), Paragraph("Simulate unavailable LLM provider", styles['TableText']), Paragraph("Suitable provider-unavailable message returned", styles['TableText']), Paragraph("To be verified", styles['TableText'])],
        [Paragraph("TC17", styles['TableText']), Paragraph("Inspect supervisor trace", styles['TableText']), Paragraph("Intent, tool, reasoning, and status are visible", styles['TableText']), Paragraph("Trace format present in source; UI verification pending", styles['TableText'])],
        [Paragraph("TC18", styles['TableText']), Paragraph("Check generated citations against retrieved passages", styles['TableText']), Paragraph("Unsupported citation/claim is flagged or qualified", styles['TableText']), Paragraph("To be verified", styles['TableText'])],
    ]
    tc_table = Table(tc_data, colWidths=[30, 140, 150, 160])
    tc_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#F1F5F9')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#64748B')),
        ('INNERGRID', (0,0), (-1,-1), 0.4, colors.HexColor('#CBD5E1')),
        ('TOPPADDING', (0,0), (-1,-1), 1.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 1.5),
    ]))
    story.append(tc_table)
    story.append(Spacer(1, 4))

    story.append(Paragraph("6.3 Functional Results", styles['SectionHeader']))
    story.append(Paragraph(
        "The source code demonstrates that the application has dedicated modules for authentication, workspaces, academic paper discovery, "
        "PDF upload, vector indexing, research chat, and structured analysis. It also defines a supervisor execution trace and evidence-oriented "
        "response checks. These are implementation observations derived from the repository and should not be confused with independently measured runtime results.", styles['Body']
    ))
    story.append(PageBreak())

    # =========================================================================
    # PAGE 21: CHAPTER 6 (CONT.)
    # =========================================================================
    story.append(Paragraph(
        "Before submission, the team should execute each test case and replace the status column with observed outputs. "
        "Screenshots of successful workflows, API responses, and test logs should be added where appropriate.", styles['Body']
    ))
    story.append(Paragraph("6.4 Research Tool Outputs", styles['SectionHeader']))
    story.append(Paragraph(
        "The expected output of Academic Paper Search is a list of paper records with bibliographic details and access links. "
        "Paper Summarization is expected to describe objectives, methodology, dataset, key findings, and limitations. Literature Review "
        "is expected to organise common themes and disagreements across the available papers. Paper Comparison is expected to compare "
        "selected publications across dimensions such as method, datasets, results, and limitations. Research Gap Identification is expected "
        "to derive candidate gaps from the workspace literature. Workspace RAG Q&A is expected to answer a question using retrieved chunks "
        "and available source metadata.", styles['Body']
    ))
    story.append(Paragraph(
        "These descriptions represent intended tool behaviour from the code structure and prompts. Actual output quality must be evaluated "
        "using representative research questions and human review.", styles['Body']
    ))

    story.append(Paragraph("6.5 Supervisor Agent Execution Results", styles['SectionHeader']))
    story.append(Paragraph(
        "The test_agent_execution.py file contains scenarios for an empty workspace, a populated workspace, academic search, summarisation, "
        "comparison, and literature review. It asserts that the expected tool label appears in the result and that empty-workspace gap analysis "
        "asks the user to upload or import literature instead of fabricating gaps. test_supervisor.py contains a set of intent-routing examples "
        "for checking the selected tool.", styles['Body']
    ))
    story.append(Paragraph(
        "Because this report preparation did not execute those scripts against a verified configured runtime, the results are recorded as "
        "'source test scenario present; actual run not recorded'. The team should run the scripts and attach the terminal output before treating the tests as passed.", styles['Body']
    ))

    story.append(Paragraph("6.6 Hallucination Firewall Results", styles['SectionHeader']))
    story.append(Paragraph(
        "The code contains a hallucination-firewall pathway in the LLM service. The expected evaluation is to supply responses with supported "
        "claims, unsupported claims, incorrect citations, and insufficient retrieved context. The team should record whether the guard preserves "
        "supported claims, flags unsupported statements with warnings and audit statistics, and reports evidence gaps. No numerical firewall accuracy "
        "or success rate is reported because no independently executed evaluation log was supplied.", styles['Body'] # CORRECTION D
    ))

    story.append(Paragraph("6.7 Limitations and Observations", styles['SectionHeader']))
    story.append(Paragraph("&bull; PDF text extraction depends on selectable text; scanned documents may require OCR, which is not established as part of the described upload pipeline.", styles['Bullet']))
    story.append(Paragraph("&bull; Semantic retrieval quality depends on loading the Sentence Transformers model. The deterministic mock-vector fallback is not a semantic embedding substitute.", styles['Bullet']))
    story.append(Paragraph("&bull; Academic search results depend on external source availability, access restrictions, and connector behaviour.", styles['Bullet']))
    story.append(Paragraph("&bull; LLM output depends on provider configuration, rate limits, and network availability.", styles['Bullet']))
    story.append(Paragraph("&bull; Pattern-based intent classification can misroute ambiguous multi-intent queries.", styles['Bullet']))
    story.append(Paragraph("&bull; Evidence checks reduce risk but cannot guarantee factual correctness or complete citation validity.", styles['Bullet']))
    story.append(Paragraph("&bull; No measured response time, accuracy, task-success rate, or user-satisfaction score is included.", styles['Bullet']))
    story.append(PageBreak())

    # =========================================================================
    # PAGE 22: CHAPTER 7: CONCLUSION AND FUTURE SCOPE
    # =========================================================================
    story.append(Paragraph("CHAPTER 7: CONCLUSION AND FUTURE SCOPE", styles['ChapterHeader']))
    story.append(Paragraph("7.1 Conclusion", styles['SectionHeader']))
    story.append(Paragraph(
        "ResearchPilot AI is an academic research assistant designed to support literature discovery, workspace organisation, PDF processing, "
        "retrieval-grounded question answering, and structured research analysis. The application combines a React and TypeScript frontend with "
        "a FastAPI backend, SQLite and SQLAlchemy relational persistence, ChromaDB vector storage, PyPDF extraction, and a configurable LLM provider layer.", styles['Body']
    ))
    story.append(Paragraph(
        "The Supervisor Agent is the central routing component. It identifies the user's research intention using an ordered set of classification "
        "patterns and invokes one of six specialised research tools. The execution trace makes the routing decision visible by reporting the intent, "
        "selected tool, rationale, and execution status. RAG provides document-grounded context for workspace questions, while the Hallucination "
        "Firewall provides a separate evidence-oriented check on generated claims and citations.", styles['Body']
    ))
    story.append(Paragraph(
        "The system is accurately characterised as a partially agentic AI application with a Supervisor Agent and specialised research tools. "
        "It is not a fully autonomous multi-agent system. Its practical usefulness depends on the completeness of the workspace literature, "
        "PDF extraction, retrieval quality, provider availability, and the reliability of evidence verification.", styles['Body']
    ))

    story.append(Paragraph("7.2 Limitations", styles['SectionHeader']))
    story.append(Paragraph("&bull; Academic source connectors may be affected by external service changes, rate limits, or access restrictions.", styles['Bullet']))
    story.append(Paragraph("&bull; PDF extraction may fail for scanned or image-only files without OCR.", styles['Bullet']))
    story.append(Paragraph("&bull; The embedding fallback uses deterministic mock vectors when Sentence Transformers is unavailable; this does not provide semantic similarity.", styles['Bullet']))
    story.append(Paragraph("&bull; Intent routing is pattern-based and may not resolve complex or ambiguous requests perfectly.", styles['Bullet']))
    story.append(Paragraph("&bull; LLM generation can contain unsupported or incorrectly interpreted statements even when evidence is retrieved.", styles['Bullet']))
    story.append(Paragraph("&bull; The Hallucination Firewall cannot prove truth or verify claims beyond the accessible evidence corpus.", styles['Bullet']))
    story.append(Paragraph("&bull; Provider fallback behaviour depends on environment configuration, including any Groq-only restriction.", styles['Bullet']))
    story.append(Paragraph("&bull; Runtime test results and measured performance values were not supplied with the source archive.", styles['Bullet']))

    story.append(Paragraph("7.3 Future Scope", styles['SectionHeader']))
    story.append(Paragraph("&bull; Introduce multi-step research planning with explicit user approval and inspectable intermediate steps.", styles['Bullet']))
    story.append(Paragraph("&bull; Extend orchestration to support more advanced agent coordination while preserving clear tool boundaries.", styles['Bullet']))
    story.append(Paragraph("&bull; Improve semantic retrieval with validated embeddings, reranking, query expansion, and retrieval evaluation.", styles['Bullet']))
    story.append(Paragraph("&bull; Add OCR support for scanned PDFs and improved document layout extraction.", styles['Bullet']))
    story.append(Paragraph("&bull; Develop richer persistent research memory for project notes, user annotations, and research decisions.", styles['Bullet']))
    story.append(Paragraph("&bull; Expand academic-source coverage and improve connector resilience and metadata normalisation.", styles['Bullet']))
    story.append(Paragraph("&bull; Strengthen evidence verification with claim-level provenance, citation resolution, and independent evaluation datasets.", styles['Bullet']))
    story.append(Paragraph("&bull; Add paper recommendation based on workspace topics, citation relationships, and research interests.", styles['Bullet']))
    story.append(Paragraph("&bull; Provide citation exports in BibTeX, APA, MLA, and Chicago formats.", styles['Bullet']))
    story.append(Paragraph("&bull; Add collaborative workspaces and shared research collections.", styles['Bullet']))
    story.append(Paragraph("&bull; Add visual knowledge maps linking papers, methods, datasets, and research themes.", styles['Bullet']))
    story.append(PageBreak())

    # =========================================================================
    # PAGE 23: CHAPTER 8: REFERENCES - CORRECTION J (META LLAMA FIXED, SBERT ADDED)
    # =========================================================================
    story.append(Paragraph("CHAPTER 8: REFERENCES", styles['ChapterHeader']))
    refs = [
        "1. Lewis, P., Perez, E., Piktus, A., et al. (2020). Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks. Advances in Neural Information Processing Systems 33. https://arxiv.org/abs/2005.11401",
        "2. Yao, S., Zhao, J., Yu, D., et al. (2023). ReAct: Synergizing Reasoning and Acting in Language Models. ICLR 2023. https://arxiv.org/abs/2210.03629",
        "3. Schick, T., Dwivedi-Yu, J., Dessì, R., et al. (2023). Toolformer: Language Models Can Teach Themselves to Use Tools. NeurIPS 2023. https://arxiv.org/abs/2302.04761",
        "4. Karpukhin, V., Oğuz, B., Min, S., et al. (2020). Dense Passage Retrieval for Open-Domain Question Answering. EMNLP 2020. https://arxiv.org/abs/2004.04906",
        "5. Manakul, P., Liusie, A., & Gales, M. (2023). SelfCheckGPT: Zero-Resource Black-Box Hallucination Detection for Generative Large Language Models. EMNLP 2023. https://arxiv.org/abs/2303.08896",
        "6. Huang, L., Yu, W., Ma, W., et al. (2023). A Survey on Hallucination in Large Language Models: Principles, Taxonomy, Challenges, and Open Questions. https://arxiv.org/abs/2311.05232",
        "7. Groq. Groq API Documentation. https://console.groq.com/docs",
        "8. Meta AI. (2024). Llama 3.3 Model Card and Prompt Format. Meta AI Documentation. https://www.llama.com/docs/model-cards-and-prompt-formats/llama3_3/", # CORRECTION J: clean spacing
        "9. Reimers, N., & Gurevych, I. (2019). Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks. EMNLP 2019. https://arxiv.org/abs/1908.10084", # CORRECTION J: Sentence-BERT added
        "10. FastAPI. FastAPI Documentation. https://fastapi.tiangolo.com/",
        "11. React. React Documentation. https://react.dev/",
        "12. Vite. Vite Documentation. https://vite.dev/guide/",
        "13. SQLAlchemy. SQLAlchemy Documentation. https://docs.sqlalchemy.org/",
        "14. Chroma. Chroma Documentation. https://docs.trychroma.com/",
        "15. Hugging Face. Sentence Transformers Documentation. https://www.sbert.net/",
        "16. PyPDF. PyPDF Documentation. https://pypdf.readthedocs.io/",
        "17. arXiv. arXiv API User Manual. https://info.arxiv.org/help/api/user-manual.html",
        "18. PubMed. NCBI E-utilities Documentation. https://www.ncbi.nlm.nih.gov/books/NBK25501/",
        "19. Semantic Scholar. Semantic Scholar API Documentation. https://api.semanticscholar.org/api-docs/",
        "20. Crossref. Crossref REST API Documentation. https://www.crossref.org/documentation/retrieve-metadata/rest-api/",
        "21. OpenAlex. OpenAlex API Documentation. https://docs.openalex.org/",
        "22. DOAJ. DOAJ API Documentation. https://doaj.org/api/v2/docs",
        "23. Project source code supplied for this report: ResearchPilot-AI-main repository archive (backend and frontend implementation).",
    ]
    for rf in refs:
        story.append(Paragraph(rf, styles['Bullet']))
    story.append(PageBreak())

    # =========================================================================
    # PAGE 24: APPENDIX A: IMPLEMENTATION WORKFLOW AND API RESPONSIBILITIES
    # =========================================================================
    story.append(Paragraph("APPENDIX A: IMPLEMENTATION WORKFLOW AND API RESPONSIBILITIES", styles['ChapterHeader']))
    story.append(Paragraph("A.1 Main Backend Responsibility Map", styles['SectionHeader']))
    resp_data = [
        [Paragraph("Module / file group", styles['TableHeader']), Paragraph("Main responsibility", styles['TableHeader'])],
        [Paragraph("app/routers/auth.py", styles['TableText']), Paragraph("Registration, login, token validation, and current-user dependency.", styles['TableText'])],
        [Paragraph("app/routers/workspaces.py", styles['TableText']), Paragraph("Workspace creation, listing, and ownership-scoped workspace operations.", styles['TableText'])],
        [Paragraph("app/routers/papers.py", styles['TableText']), Paragraph("Paper upload, PDF extraction, indexing, paper access, listing, and deletion.", styles['TableText'])],
        [Paragraph("app/routers/chat.py", styles['TableText']), Paragraph("Workspace chat sessions and persisted chat messages.", styles['TableText'])],
        [Paragraph("app/routers/assistant.py", styles['TableText']), Paragraph("Workspace assistant endpoint, retrieval, chat context, and source metadata.", styles['TableText'])],
        [Paragraph("app/routers/tools.py", styles['TableText']), Paragraph("Dedicated endpoints for summary, insights, review, and other analysis operations.", styles['TableText'])],
        [Paragraph("app/services/hybrid_search_service.py", styles['TableText']), Paragraph("Coordination, deduplication, ranking, and diversification of academic search results.", styles['TableText'])],
        [Paragraph("app/services/vector_service.py", styles['TableText']), Paragraph("Chunking, embedding generation, ChromaDB indexing, and retrieval scoring.", styles['TableText'])],
        [Paragraph("app/services/supervisor_agent.py", styles['TableText']), Paragraph("Intent classification, single-tool routing, tool execution, and trace generation.", styles['TableText'])],
        [Paragraph("app/services/llm_service.py", styles['TableText']), Paragraph("Prompt-based generation and configured provider handling.", styles['TableText'])],
        [Paragraph("app/services/guard_service.py", styles['TableText']), Paragraph("Research-scope query screening.", styles['TableText'])],
    ]
    resp_table = Table(resp_data, colWidths=[150, 330])
    resp_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#F1F5F9')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#64748B')),
        ('INNERGRID', (0,0), (-1,-1), 0.4, colors.HexColor('#CBD5E1')),
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
    ]))
    story.append(resp_table)
    story.append(Spacer(1, 4))

    story.append(Paragraph("A.2 Illustrative Request Processing Pseudocode", styles['SectionHeader']))
    story.append(Paragraph("The following pseudocode summarises the source-backed control flow; it is explanatory and is not copied as a complete source implementation.", styles['BodyCompact']))
    pseudo = [
        "1. Receive user query and workspace/session identifiers",
        "2. Validate the user and verify access to the workspace",
        "3. Load papers belonging to the active workspace",
        "4. Classify intent using the supervisor's ordered patterns (Comparison -> Review -> Summary -> Gaps -> Search -> RAG)",
        "5. Select one registered research tool",
        "6. Execute the selected tool:",
        "&nbsp;&nbsp;&nbsp;&nbsp;a. Search academic sources (Direct preprint metadata formatting, bypassing LLM), OR",
        "&nbsp;&nbsp;&nbsp;&nbsp;b. Build paper evidence and summarise/review/compare/analyse gaps via LLM, OR",
        "&nbsp;&nbsp;&nbsp;&nbsp;c. Retrieve workspace chunks and answer the question via RAG",
        "7. Handle missing papers, provider failures, or tool exceptions",
        "8. Apply evidence/citation verification to applicable LLM-generated responses. Academic Paper Search directly formats and returns discovery results without invoking the LLM or Hallucination Firewall.",
        "9. Return composite answer with intent, selected tool, rationale, and status",
    ]
    for ps in pseudo:
        story.append(Paragraph(ps, styles['BodyCompact']))
    story.append(PageBreak())

    # =========================================================================
    # PAGE 25: APPENDIX B: APPLICATION SCREENSHOT PLACEHOLDERS (FIG 5.1 - 5.4)
    # =========================================================================
    story.append(Paragraph("APPENDIX B: APPLICATION SCREENSHOT PLACEHOLDERS", styles['ChapterHeader']))
    story.append(Paragraph(
        "The boxes below are intentionally blank. Replace them with genuine screenshots captured from the running "
        "ResearchPilot AI application. Do not submit these placeholders as proof of execution.", styles['BodyCompact']
    ))
    story.append(Spacer(1, 2))

    story.append(Paragraph("<b>Figure 5.1 – Login page</b>", styles['SubSectionHeader']))
    story.append(build_diagrams.build_screenshot_placeholder("5.1", "Login Page"))
    story.append(Spacer(1, 2))

    story.append(Paragraph("<b>Figure 5.2 – Dashboard</b>", styles['SubSectionHeader']))
    story.append(build_diagrams.build_screenshot_placeholder("5.2", "Dashboard"))
    story.append(Spacer(1, 2))

    story.append(Paragraph("<b>Figure 5.3 – Workspace management</b>", styles['SubSectionHeader']))
    story.append(build_diagrams.build_screenshot_placeholder("5.3", "Workspace Management"))
    story.append(Spacer(1, 2))

    story.append(Paragraph("<b>Figure 5.4 – Academic paper search</b>", styles['SubSectionHeader']))
    story.append(build_diagrams.build_screenshot_placeholder("5.4", "Academic Paper Search"))
    story.append(PageBreak())

    # =========================================================================
    # PAGE 26: APPENDIX B: APPLICATION SCREENSHOT PLACEHOLDERS (FIG 5.5 - 5.8)
    # =========================================================================
    story.append(Paragraph("APPENDIX B: APPLICATION SCREENSHOT PLACEHOLDERS", styles['ChapterHeader']))
    story.append(Paragraph(
        "The boxes below are intentionally blank. Replace them with genuine screenshots captured from the running "
        "ResearchPilot AI application. Do not submit these placeholders as proof of execution.", styles['BodyCompact']
    ))
    story.append(Spacer(1, 2))

    story.append(Paragraph("<b>Figure 5.5 – PDF upload</b>", styles['SubSectionHeader']))
    story.append(build_diagrams.build_screenshot_placeholder("5.5", "PDF Upload"))
    story.append(Spacer(1, 2))

    story.append(Paragraph("<b>Figure 5.6 – Research Chat</b>", styles['SubSectionHeader']))
    story.append(build_diagrams.build_screenshot_placeholder("5.6", "Research Chat"))
    story.append(Spacer(1, 2))

    story.append(Paragraph("<b>Figure 5.7 – Supervisor Agent execution trace</b>", styles['SubSectionHeader']))
    story.append(build_diagrams.build_screenshot_placeholder("5.7", "Supervisor Agent Execution Trace"))
    story.append(Spacer(1, 2))

    story.append(Paragraph("<b>Figure 5.8 – Paper summarization</b>", styles['SubSectionHeader']))
    story.append(build_diagrams.build_screenshot_placeholder("5.8", "Paper Summarization"))
    story.append(PageBreak())

    # =========================================================================
    # PAGE 27: APPENDIX B: APPLICATION SCREENSHOT PLACEHOLDERS (FIG 5.9 - 5.11)
    # =========================================================================
    story.append(Paragraph("APPENDIX B: APPLICATION SCREENSHOT PLACEHOLDERS", styles['ChapterHeader']))
    story.append(Paragraph(
        "The boxes below are intentionally blank. Replace them with genuine screenshots captured from the running "
        "ResearchPilot AI application. Do not submit these placeholders as proof of execution.", styles['BodyCompact']
    ))
    story.append(Spacer(1, 6))

    story.append(Paragraph("<b>Figure 5.9 – Research gap analysis</b>", styles['SubSectionHeader']))
    story.append(build_diagrams.build_screenshot_placeholder("5.9", "Research Gap Analysis"))
    story.append(Spacer(1, 8))

    story.append(Paragraph("<b>Figure 5.10 – Literature review</b>", styles['SubSectionHeader']))
    story.append(build_diagrams.build_screenshot_placeholder("5.10", "Literature Review"))
    story.append(Spacer(1, 8))

    story.append(Paragraph("<b>Figure 5.11 – Paper comparison</b>", styles['SubSectionHeader']))
    story.append(build_diagrams.build_screenshot_placeholder("5.11", "Paper Comparison"))
    
    # Build Document
    doc.build(story, canvasmaker=NumberedCanvas)
    print("Report generated successfully:", output_pdf_path)

if __name__ == "__main__":
    generate_report()
