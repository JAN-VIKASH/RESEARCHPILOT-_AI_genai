"""
Vector diagram definitions for ResearchPilot AI Report using ReportLab Graphics.
Generates Figures 4.1 through 4.9 and screenshot placeholders for Figures 5.1 through 5.11.
"""

from reportlab.graphics.shapes import Drawing, Rect, String, Line, Group, Polygon
from reportlab.lib import colors

def draw_box(d, x, y, w, h, title, subtitle="", fill_color="#F8FAFC", stroke_color="#64748B", text_color="#0F172A", rx=3, ry=3, font_size=8, sub_size=6.5):
    """Utility to draw a rounded rectangular node with centered text."""
    d.add(Rect(x, y, w, h, rx=rx, ry=ry, fillColor=colors.HexColor(fill_color), strokeColor=colors.HexColor(stroke_color), strokeWidth=0.8))
    if subtitle:
        d.add(String(x + w / 2.0, y + h / 2.0 + 3, title, textAnchor="middle", fontName="Helvetica-Bold", fontSize=font_size, fillColor=colors.HexColor(text_color)))
        d.add(String(x + w / 2.0, y + h / 2.0 - 7, subtitle, textAnchor="middle", fontName="Helvetica", fontSize=sub_size, fillColor=colors.HexColor("#475569")))
    else:
        d.add(String(x + w / 2.0, y + h / 2.0 - 3, title, textAnchor="middle", fontName="Helvetica-Bold", fontSize=font_size, fillColor=colors.HexColor(text_color)))

def draw_arrow(d, x1, y1, x2, y2, color="#475569", width=0.8, label="", label_pos="right", label_size=6.5):
    """Draws a connecting line with a directional arrowhead."""
    d.add(Line(x1, y1, x2, y2, strokeColor=colors.HexColor(color), strokeWidth=width))
    # Draw arrow head
    if x1 == x2: # vertical arrow
        direction = 1 if y2 > y1 else -1
        arrow_poly = Polygon([
            x2, y2,
            x2 - 3, y2 - 4 * direction,
            x2 + 3, y2 - 4 * direction
        ], fillColor=colors.HexColor(color), strokeColor=colors.HexColor(color), strokeWidth=0.5)
        d.add(arrow_poly)
        if label:
            lx = x2 + 4 if label_pos == "right" else x2 - 4
            d.add(String(lx, (y1 + y2) / 2.0 - 2, label, fontName="Helvetica", fontSize=label_size, fillColor=colors.HexColor("#64748B"), textAnchor="start" if label_pos=="right" else "end"))
    elif y1 == y2: # horizontal arrow
        direction = 1 if x2 > x1 else -1
        arrow_poly = Polygon([
            x2, y2,
            x2 - 4 * direction, y2 - 3,
            x2 - 4 * direction, y2 + 3
        ], fillColor=colors.HexColor(color), strokeColor=colors.HexColor(color), strokeWidth=0.5)
        d.add(arrow_poly)
        if label:
            d.add(String((x1 + x2) / 2.0, y1 + 3, label, fontName="Helvetica", fontSize=label_size, fillColor=colors.HexColor("#64748B"), textAnchor="middle"))

def build_fig_4_1():
    """Figure 4.1: High-Level Architecture of ResearchPilot AI"""
    d = Drawing(480, 190)
    # Background panel
    d.add(Rect(0, 0, 480, 190, rx=4, ry=4, fillColor=colors.HexColor("#FAFAFA"), strokeColor=colors.HexColor("#E2E8F0"), strokeWidth=0.8))
    
    # 1. User
    draw_box(d, 180, 155, 120, 26, "Researcher / Student", fill_color="#F1F5F9", stroke_color="#0F172A", font_size=8)
    draw_arrow(d, 240, 155, 240, 138, label="HTTP / JSON")
    
    # 2. Frontend
    draw_box(d, 160, 114, 160, 24, "React + TypeScript + Vite UI", fill_color="#E0F2FE", stroke_color="#0284C7", text_color="#0369A1", font_size=8)
    draw_arrow(d, 240, 114, 240, 97)
    
    # 3. FastAPI Backend
    draw_box(d, 160, 73, 160, 24, "FastAPI Backend / API Routers", fill_color="#EDE9FE", stroke_color="#7C3AED", text_color="#6D28D9", font_size=8)
    
    # Arrows from Backend to sublayers
    draw_arrow(d, 190, 73, 80, 48, label="persistence", label_pos="left")
    draw_arrow(d, 240, 73, 240, 48, label="routing")
    draw_arrow(d, 290, 73, 400, 48, label="services", label_pos="right")

    # 4. Storage & Processing Layers
    # Left: SQLite
    draw_box(d, 20, 12, 125, 36, "SQLite + SQLAlchemy", "Users • Workspaces • Papers", fill_color="#FEF3C7", stroke_color="#D97706", text_color="#B45309", font_size=7.5, sub_size=6)
    
    # Center: Supervisor & ChromaDB
    draw_box(d, 175, 12, 130, 36, "Supervisor Agent (ChromaDB)", "Intent Routing • Vector Chunks", fill_color="#DCFCE7", stroke_color="#16A34A", text_color="#15803D", font_size=7.5, sub_size=6)
    
    # Right: LLM & Services
    draw_box(d, 335, 12, 125, 36, "LLM Provider Layer", "Groq Primary • Cloud Fallbacks", fill_color="#FCE7F3", stroke_color="#DB2777", text_color="#BE185D", font_size=7.5, sub_size=6)
    
    return d

def build_fig_4_2():
    """Figure 4.2: Supervisor Agent Single-Tool Routing Workflow (Corrected: Search bypasses LLM/Firewall)"""
    d = Drawing(480, 205)
    d.add(Rect(0, 0, 480, 205, rx=4, ry=4, fillColor=colors.HexColor("#FAFAFA"), strokeColor=colors.HexColor("#E2E8F0"), strokeWidth=0.8))

    # Top: Query & Guard
    draw_box(d, 170, 175, 140, 20, "User Research Query", fill_color="#F8FAFC", stroke_color="#334155", font_size=7.5)
    draw_arrow(d, 240, 175, 240, 160)
    
    draw_box(d, 170, 142, 140, 18, "Research-Scope Guard", fill_color="#FEF2F2", stroke_color="#DC2626", text_color="#991B1B", font_size=7.5)
    draw_arrow(d, 240, 142, 240, 127)

    # Supervisor Intent Classifier
    draw_box(d, 150, 107, 180, 20, "Supervisor: Intent Classification", fill_color="#EDE9FE", stroke_color="#6D28D9", text_color="#5B21B6", font_size=8)
    
    # Horizontal distribution line
    d.add(Line(40, 95, 440, 95, strokeColor=colors.HexColor("#94A3B8"), strokeWidth=0.8))
    draw_arrow(d, 240, 107, 240, 95)

    # 6 Tool Nodes
    tool_boxes = [
        (10, 68, 70, 22, "Academic Search", "#E0F2FE", "#0284C7"),
        (88, 68, 70, 22, "Paper Summary", "#DCFCE7", "#16A34A"),
        (166, 68, 70, 22, "Lit Review", "#FEF3C7", "#D97706"),
        (244, 68, 70, 22, "Comparison", "#FCE7F3", "#DB2777"),
        (322, 68, 70, 22, "Research Gaps", "#F3E8FF", "#7C3AED"),
        (400, 68, 70, 22, "Workspace Q&A", "#F1F5F9", "#475569"),
    ]
    
    for x, y, w, h, name, bg, stroke in tool_boxes:
        draw_arrow(d, x + w/2.0, 95, x + w/2.0, 90)
        draw_box(d, x, y, w, h, name, fill_color=bg, stroke_color=stroke, font_size=6.5)

    # CORRECTION B:
    # Academic Search bypasses LLM & Firewall completely!
    # Direct line from Academic Search (x=45) down to Final Answer
    draw_arrow(d, 45, 68, 45, 18, color="#0284C7", label="Direct API format", label_pos="left", label_size=6)
    
    # Other 5 generative tools connect to Evidence + LLM Generation
    d.add(Line(123, 60, 435, 60, strokeColor=colors.HexColor("#94A3B8"), strokeWidth=0.8))
    for x, y, w, h, name, bg, stroke in tool_boxes[1:]:
        d.add(Line(x + w/2.0, 68, x + w/2.0, 60, strokeColor=colors.HexColor("#94A3B8"), strokeWidth=0.8))
    
    draw_arrow(d, 279, 60, 279, 48)
    draw_box(d, 195, 34, 170, 16, "Evidence Pack + LLM Generation", fill_color="#FFFBEB", stroke_color="#B45309", text_color="#78350F", font_size=7)
    
    draw_arrow(d, 279, 34, 279, 24)
    draw_box(d, 195, 8, 170, 16, "Hallucination Firewall Verification", fill_color="#F0FDF4", stroke_color="#15803D", text_color="#166534", font_size=7)

    # Converge into Final Response
    draw_arrow(d, 45, 18, 115, 18, color="#0284C7")
    draw_arrow(d, 195, 16, 175, 16, color="#15803D")
    draw_box(d, 115, 6, 60, 20, "Final Response", fill_color="#0F172A", stroke_color="#0F172A", text_color="#FFFFFF", font_size=6.5)

    return d

def build_fig_4_3():
    """Figure 4.3: PDF Processing and Workspace RAG Pipeline"""
    d = Drawing(480, 150)
    d.add(Rect(0, 0, 480, 150, rx=4, ry=4, fillColor=colors.HexColor("#FAFAFA"), strokeColor=colors.HexColor("#E2E8F0"), strokeWidth=0.8))

    # Top boxes
    draw_box(d, 165, 124, 150, 18, "Uploaded PDF / Imported Preprint", fill_color="#F1F5F9", stroke_color="#334155", font_size=7.5)
    draw_arrow(d, 240, 124, 240, 112)

    draw_box(d, 165, 96, 150, 16, "PyPDF Text & Font Heading Extraction", fill_color="#E0F2FE", stroke_color="#0284C7", font_size=7)
    draw_arrow(d, 240, 96, 240, 84)

    draw_box(d, 150, 68, 180, 16, "Section Detection + Chunking (850c / 160o)", fill_color="#EDE9FE", stroke_color="#7C3AED", font_size=7)
    
    # 3 parallel indexing signals
    draw_arrow(d, 170, 68, 80, 52)
    draw_arrow(d, 240, 68, 240, 52)
    draw_arrow(d, 310, 68, 400, 52)

    draw_box(d, 20, 36, 120, 16, "TF-IDF / Keyword Scoring", fill_color="#FEF3C7", stroke_color="#D97706", font_size=6.5)
    draw_box(d, 160, 36, 160, 16, "Dense Embeddings (384d / MiniLM)", fill_color="#DCFCE7", stroke_color="#16A34A", font_size=6.5)
    draw_box(d, 340, 36, 120, 16, "Citation / Chunk Metadata", fill_color="#FCE7F3", stroke_color="#DB2777", font_size=6.5)

    draw_arrow(d, 80, 36, 200, 20)
    draw_arrow(d, 240, 36, 240, 20)
    draw_arrow(d, 400, 36, 280, 20)

    draw_box(d, 160, 4, 160, 16, "ChromaDB Persistent Vector Store", fill_color="#0F172A", stroke_color="#0F172A", text_color="#FFFFFF", font_size=7)

    return d

def build_fig_4_4():
    """Figure 4.4: Evidence & Citation Verification (Corrected: Passive Auditor, no auto-rewrite)"""
    d = Drawing(480, 145)
    d.add(Rect(0, 0, 480, 145, rx=4, ry=4, fillColor=colors.HexColor("#FAFAFA"), strokeColor=colors.HexColor("#E2E8F0"), strokeWidth=0.8))

    draw_box(d, 165, 120, 150, 18, "Generated Research Response", fill_color="#F8FAFC", stroke_color="#334155", font_size=7.5)
    draw_arrow(d, 240, 120, 240, 106)

    draw_box(d, 155, 90, 170, 16, "Extract & Inspect Citation Tags [P-C]", fill_color="#E0F2FE", stroke_color="#0284C7", font_size=7)
    draw_arrow(d, 240, 90, 240, 76)

    draw_box(d, 150, 60, 180, 16, "Sentence-Level Citation Audit Algorithm", fill_color="#EDE9FE", stroke_color="#7C3AED", font_size=7)

    # 3 outcomes
    draw_arrow(d, 180, 60, 80, 44)
    draw_arrow(d, 240, 60, 240, 44)
    draw_arrow(d, 300, 60, 400, 44)

    draw_box(d, 15, 26, 130, 18, "Supported Claims", "Retain [P-C] Chunk Citation", fill_color="#DCFCE7", stroke_color="#16A34A", font_size=6.5, sub_size=5.5)
    draw_box(d, 165, 26, 150, 18, "Unsupported / Weak Claims", "Flag with Audit Warning (No rewrite)", fill_color="#FEF2F2", stroke_color="#DC2626", font_size=6.5, sub_size=5.5)
    draw_box(d, 335, 26, 130, 18, "Missing Information", "Explicit 'Not specified' Fallback", fill_color="#FEF3C7", stroke_color="#D97706", font_size=6.5, sub_size=5.5)

    draw_arrow(d, 80, 26, 200, 14)
    draw_arrow(d, 240, 26, 240, 14)
    draw_arrow(d, 400, 26, 280, 14)

    draw_box(d, 170, 2, 140, 14, "Grounded Output + Audit Metrics", fill_color="#0F172A", stroke_color="#0F172A", text_color="#FFFFFF", font_size=6.5)

    return d

def build_fig_4_5():
    """Figure 4.5: Relational Data Model (Corrected: DOCUMENTS attribute doc_type)"""
    d = Drawing(480, 130)
    d.add(Rect(0, 0, 480, 130, rx=4, ry=4, fillColor=colors.HexColor("#FAFAFA"), strokeColor=colors.HexColor("#E2E8F0"), strokeWidth=0.8))

    # Row 1: Users, Workspaces, Papers, Documents
    draw_box(d, 15, 80, 95, 38, "USERS", "id • email • password", fill_color="#EFF6FF", stroke_color="#3B82F6", font_size=7, sub_size=6)
    draw_box(d, 135, 80, 95, 38, "WORKSPACES", "id • user_id • name", fill_color="#EFF6FF", stroke_color="#3B82F6", font_size=7, sub_size=6)
    draw_box(d, 255, 80, 95, 38, "PAPERS", "id • workspace_id • title", fill_color="#EFF6FF", stroke_color="#3B82F6", font_size=7, sub_size=6)
    # CORRECTION E: doc_type instead of type!
    draw_box(d, 370, 80, 95, 38, "DOCUMENTS", "id • workspace_id • doc_type", fill_color="#EFF6FF", stroke_color="#3B82F6", font_size=7, sub_size=6)

    # Connections Row 1
    draw_arrow(d, 110, 99, 135, 99, label="1:N", label_pos="right", label_size=6)
    draw_arrow(d, 230, 99, 255, 99, label="1:N", label_pos="right", label_size=6)
    draw_arrow(d, 230, 99, 370, 99, label="1:N", label_pos="right", label_size=6)

    # Row 2: Chat Sessions & Chat Messages
    draw_box(d, 135, 15, 100, 36, "CHAT_SESSIONS", "id • workspace_id • user_id", fill_color="#F5F3FF", stroke_color="#8B5CF6", font_size=7, sub_size=6)
    draw_box(d, 275, 15, 100, 36, "CHAT_MESSAGES", "id • session_id • role", fill_color="#F5F3FF", stroke_color="#8B5CF6", font_size=7, sub_size=6)

    draw_arrow(d, 182, 80, 182, 51, label="1:N", label_pos="right", label_size=6)
    draw_arrow(d, 235, 33, 275, 33, label="1:N", label_pos="right", label_size=6)

    return d

def build_fig_4_6():
    """Figure 4.6: DFD Level 0 - Context Diagram"""
    d = Drawing(480, 100)
    d.add(Rect(0, 0, 480, 100, rx=4, ry=4, fillColor=colors.HexColor("#FAFAFA"), strokeColor=colors.HexColor("#E2E8F0"), strokeWidth=0.8))

    draw_box(d, 25, 30, 100, 40, "Student / Researcher", "External Primary Actor", fill_color="#EFF6FF", stroke_color="#2563EB", font_size=7.5, sub_size=6)
    draw_box(d, 180, 25, 120, 50, "ResearchPilot AI", "Intelligent Platform Core", fill_color="#F8FAFC", stroke_color="#0F172A", font_size=8, sub_size=6.5)
    draw_box(d, 350, 30, 105, 40, "External Repositories & LLMs", "arXiv, PubMed, Groq, etc.", fill_color="#FDF2F8", stroke_color="#DB2777", font_size=7, sub_size=6)

    draw_arrow(d, 125, 55, 180, 55, label="queries / uploads", label_size=6)
    draw_arrow(d, 180, 42, 125, 42, label="answers / reports", label_size=6)

    draw_arrow(d, 300, 55, 350, 55, label="API search / prompt", label_size=6)
    draw_arrow(d, 350, 42, 300, 42, label="preprints / tokens", label_size=6)

    return d

def build_fig_4_7():
    """Figure 4.7: DFD Level 1 - Internal Processing"""
    d = Drawing(480, 130)
    d.add(Rect(0, 0, 480, 130, rx=4, ry=4, fillColor=colors.HexColor("#FAFAFA"), strokeColor=colors.HexColor("#E2E8F0"), strokeWidth=0.8))

    draw_box(d, 175, 102, 130, 20, "User Request Ingestion", fill_color="#F1F5F9", stroke_color="#334155", font_size=7.5)
    draw_arrow(d, 240, 102, 240, 88)

    draw_box(d, 160, 72, 160, 16, "Auth Check & Supervisor Intent Routing", fill_color="#EDE9FE", stroke_color="#7C3AED", font_size=7)

    # 4 subprocess boxes
    draw_arrow(d, 180, 72, 70, 52)
    draw_arrow(d, 220, 72, 185, 52)
    draw_arrow(d, 260, 72, 295, 52)
    draw_arrow(d, 300, 72, 410, 52)

    draw_box(d, 15, 32, 105, 20, "1.0 Academic Search", fill_color="#E0F2FE", stroke_color="#0284C7", font_size=6.5)
    draw_box(d, 130, 32, 110, 20, "2.0 PDF & ChromaDB Index", fill_color="#DCFCE7", stroke_color="#16A34A", font_size=6.5)
    draw_box(d, 250, 32, 95, 20, "3.0 Analysis Tools", fill_color="#FEF3C7", stroke_color="#D97706", font_size=6.5)
    draw_box(d, 355, 32, 110, 20, "4.0 LLM & Evidence Guard", fill_color="#FCE7F3", stroke_color="#DB2777", font_size=6.5)

    draw_arrow(d, 67, 32, 200, 16)
    draw_arrow(d, 185, 32, 220, 16)
    draw_arrow(d, 297, 32, 260, 16)
    draw_arrow(d, 410, 32, 280, 16)

    draw_box(d, 170, 4, 140, 16, "Synthesized Trace + Response", fill_color="#0F172A", stroke_color="#0F172A", text_color="#FFFFFF", font_size=7)

    return d

def build_fig_4_8():
    """Figure 4.8: Sequence Diagram (Corrected: Return through Supervisor -> FastAPI -> DB -> Browser)"""
    d = Drawing(480, 170)
    d.add(Rect(0, 0, 480, 170, rx=4, ry=4, fillColor=colors.HexColor("#FAFAFA"), strokeColor=colors.HexColor("#E2E8F0"), strokeWidth=0.8))

    lifelines = [
        (45, "User/Browser"),
        (125, "FastAPI API"),
        (205, "Supervisor"),
        (285, "Tool/RAG"),
        (365, "LLM/Firewall"),
        (445, "SQLite DB")
    ]
    
    # Draw top lifeline boxes and vertical dashed lines
    for x, name in lifelines:
        draw_box(d, x - 35, 146, 70, 18, name, fill_color="#F1F5F9", stroke_color="#475569", font_size=6.5)
        d.add(Line(x, 146, x, 12, strokeColor=colors.HexColor("#CBD5E1"), strokeWidth=0.6, strokeDashArray=[2, 2]))

    # Sequence calls
    # 1. Submit
    draw_arrow(d, 45, 134, 125, 134, label="1. Submit Query", label_size=5.5)
    # 2. Access check
    draw_arrow(d, 125, 120, 445, 120, label="2. Check Workspace", label_size=5.5)
    # 3. Route
    draw_arrow(d, 125, 106, 205, 106, label="3. Classify & Route", label_size=5.5)
    # 4. Invoke
    draw_arrow(d, 205, 92, 285, 92, label="4. Execute Tool", label_size=5.5)
    # 5. LLM
    draw_arrow(d, 285, 78, 365, 78, label="5. Prompt + Audit", label_size=5.5)
    # 6. Verified text back to Supervisor (CORRECTION C)
    draw_arrow(d, 365, 64, 205, 64, color="#15803D", label="6. Return Grounded Result", label_size=5.5)
    # 7. Trace synthesis back to FastAPI
    draw_arrow(d, 205, 50, 125, 50, color="#15803D", label="7. Synthesize Trace", label_size=5.5)
    # 8. Persist to DB
    draw_arrow(d, 125, 36, 445, 36, label="8. Persist Message", label_size=5.5)
    # 9. Return to Browser
    draw_arrow(d, 125, 22, 45, 22, color="#0284C7", label="9. Render Response", label_size=5.5)

    return d

def build_fig_4_9():
    """Figure 4.9: Use Case View of ResearchPilot AI"""
    d = Drawing(480, 135)
    d.add(Rect(0, 0, 480, 135, rx=4, ry=4, fillColor=colors.HexColor("#FAFAFA"), strokeColor=colors.HexColor("#E2E8F0"), strokeWidth=0.8))

    # Primary Actor: Student / Researcher
    draw_box(d, 20, 45, 90, 40, "Student / Researcher", "Primary Actor", fill_color="#EFF6FF", stroke_color="#2563EB", font_size=7, sub_size=6)

    # Secondary Actor: Academic Indexes
    draw_box(d, 370, 75, 90, 36, "Academic Indexes", "arXiv, PubMed, IEEE", fill_color="#FDF2F8", stroke_color="#DB2777", font_size=7, sub_size=6)

    # Use Case boundary
    d.add(Rect(130, 6, 220, 122, rx=6, ry=6, fillColor=colors.HexColor("#FFFFFF"), strokeColor=colors.HexColor("#94A3B8"), strokeWidth=0.8, strokeDashArray=[3, 3]))
    d.add(String(240, 116, "ResearchPilot AI Core", textAnchor="middle", fontName="Helvetica-Bold", fontSize=7, fillColor=colors.HexColor("#64748B")))

    cases = [
        (145, 92, 190, 16, "Manage Account & Workspaces"),
        (145, 70, 190, 16, "Search & Import Academic Papers"),
        (145, 48, 190, 16, "Upload & Process PDF Documents"),
        (145, 26, 190, 16, "Chat with Workspace Literature (RAG)"),
        (145, 10, 190, 16, "Run AI Analysis Tools (Summary, Gaps)"),
    ]

    for cx, cy, cw, ch, cname in cases:
        d.add(Rect(cx, cy, cw, ch, rx=8, ry=8, fillColor=colors.HexColor("#F8FAFC"), strokeColor=colors.HexColor("#64748B"), strokeWidth=0.6))
        d.add(String(cx + cw/2.0, cy + ch/2.0 - 2.5, cname, textAnchor="middle", fontName="Helvetica", fontSize=6.5, fillColor=colors.HexColor("#0F172A")))
        draw_arrow(d, 110, 65, cx, cy + ch/2.0)

    # Connect Search & Import Papers to Academic Indexes
    draw_arrow(d, 335, 78, 370, 88, color="#DB2777", label="live query", label_size=5.5)

    return d

def build_screenshot_placeholder(fig_label, caption):
    """Draws a clean placeholder box with dashed border for figures 5.1 through 5.11."""
    d = Drawing(480, 140)
    # Dashed rectangle
    d.add(Rect(10, 10, 460, 120, rx=4, ry=4, fillColor=colors.HexColor("#FAFAFA"), strokeColor=colors.HexColor("#94A3B8"), strokeWidth=1, strokeDashArray=[4, 4]))
    d.add(String(240, 75, f"[INSERT ACTUAL SCREENSHOT HERE: {caption.upper()}]", textAnchor="middle", fontName="Helvetica-Bold", fontSize=8.5, fillColor=colors.HexColor("#64748B")))
    d.add(String(240, 55, "(Captured from running frontend application)", textAnchor="middle", fontName="Helvetica-Oblique", fontSize=7, fillColor=colors.HexColor("#94A3B8")))
    return d

print("build_diagrams.py loaded successfully")

