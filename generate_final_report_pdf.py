#!/usr/bin/env python3
"""
=============================================================================
PES UNIVERSITY DBMS MINI PROJECT FINAL REPORT PDF GENERATOR
UE23CS351A / UE24CS351A - DBMS Project
Authors: Sanyam Deven Hiran (PES2UG24CS446), Shashank A (PES2UG24CS461)
=============================================================================
Generates a complete, publication-quality academic report matching PES format.
"""

import os
import sys
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas

PDF_OUTPUT = "PES2UG24CS446_PES2UG24CS461_Final_Report.pdf"

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super(NumberedCanvas, self).__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super(NumberedCanvas, self).showPage()
        super(NumberedCanvas, self).save()

    def draw_page_decorations(self, page_count):
        # Do not draw headers/footers on cover page
        if self._pageNumber == 1:
            return

        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748b"))

        # Header
        self.drawString(54, 750, "PES University | UE23CS351A - DBMS Project (Group 20)")
        self.drawRightString(612 - 54, 750, "Algorithmic Execution Fingerprinting")
        self.setStrokeColor(colors.HexColor("#cbd5e1"))
        self.setLineWidth(0.5)
        self.line(54, 744, 612 - 54, 744)

        # Footer
        self.line(54, 45, 612 - 54, 45)
        self.drawString(54, 32, "Department of Computer Science and Engineering | Faculty of Engineering")
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(612 - 54, 32, page_str)
        self.restoreState()


def build_pdf():
    doc = SimpleDocTemplate(
        PDF_OUTPUT,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'CoverTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        alignment=1,
        textColor=colors.HexColor('#0f172a')
    )

    subtitle_style = ParagraphStyle(
        'CoverSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=12,
        leading=16,
        alignment=1,
        textColor=colors.HexColor('#334155')
    )

    h1_style = ParagraphStyle(
        'Heading1_Custom',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=15,
        leading=19,
        textColor=colors.HexColor('#0f172a'),
        spaceBefore=14,
        spaceAfter=8,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'Heading2_Custom',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#1e293b'),
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'Body_Custom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13.5,
        textColor=colors.HexColor('#1e293b'),
        spaceAfter=6
    )

    code_style = ParagraphStyle(
        'Code_Custom',
        parent=styles['Code'],
        fontName='Courier',
        fontSize=8,
        leading=10.5,
        textColor=colors.HexColor('#0f172a'),
        backColor=colors.HexColor('#f1f5f9'),
        borderPadding=6,
        spaceBefore=4,
        spaceAfter=6
    )

    story = []

    # ==========================================
    # 1. COVER PAGE
    # ==========================================
    pes_logo_path = "report_assets/pes_logo.png"
    if os.path.exists(pes_logo_path):
        story.append(Image(pes_logo_path, width=1.1*inch, height=1.8*inch))
    story.append(Spacer(1, 15))

    story.append(Paragraph("Mini project report on", subtitle_style))
    story.append(Spacer(1, 10))
    story.append(Paragraph("ALGORITHMIC EXECUTION FINGERPRINTING AND RUNTIME THREAT DETECTION SYSTEM", title_style))
    story.append(Spacer(1, 12))
    story.append(Paragraph("Submitted in partial fulfilment of the requirements for the award of degree of<br/><b>Bachelor of Technology</b><br/>in<br/><b>Computer Science & Engineering</b><br/><b>UE23CS351A – DBMS Project</b>", subtitle_style))
    story.append(Spacer(1, 20))

    authors_data = [
        [Paragraph("<b>Submitted by:</b>", body_style), Paragraph("<b>SRN:</b>", body_style)],
        [Paragraph("Sanyam Deven Hiran", body_style), Paragraph("PES2UG24CS446", body_style)],
        [Paragraph("Shashank A", body_style), Paragraph("PES2UG24CS461", body_style)]
    ]
    t_auth = Table(authors_data, colWidths=[200, 150], hAlign='CENTER')
    t_auth.setStyle(TableStyle([
        ('LINEBELOW', (0,0), (-1,0), 1, colors.HexColor('#0284c7')),
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f0f9ff')),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('TOPPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_auth)
    story.append(Spacer(1, 20))

    story.append(Paragraph("under the guidance of<br/><b>Dr. Shilpa S</b><br/>Assistant Professor<br/>Department of Computer Science and Engineering", subtitle_style))
    story.append(Spacer(1, 25))

    story.append(Paragraph("<b>AUG - DEC 2026</b><br/>DEPARTMENT OF COMPUTER SCIENCE AND ENGINEERING<br/>FACULTY OF ENGINEERING<br/><b>PES UNIVERSITY</b><br/>(Established under Karnataka Act No. 16 of 2013)<br/>Electronic City, Hosur Road, Bengaluru – 560 100, Karnataka, India", subtitle_style))
    story.append(PageBreak())

    # ==========================================
    # 2. CERTIFICATE PAGE
    # ==========================================
    if os.path.exists(pes_logo_path):
        story.append(Image(pes_logo_path, width=0.8*inch, height=1.3*inch))
    story.append(Spacer(1, 10))
    story.append(Paragraph("<b>PES UNIVERSITY</b>", title_style))
    story.append(Paragraph("(Established under Karnataka Act No. 16 of 2013)<br/>Electronic City, Hosur Road, Bengaluru – 560 100, Karnataka, India", subtitle_style))
    story.append(Spacer(1, 15))
    story.append(Paragraph("CERTIFICATE", title_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#0284c7'), spaceAfter=15))

    cert_text = """This is to certify that the mini project entitled <b>"Algorithmic Execution Fingerprinting and Runtime Threat Detection System"</b> is a bonafide work carried out by:
    <br/><br/>
    &nbsp;&nbsp;&nbsp;&nbsp;• <b>Sanyam Deven Hiran (PES2UG24CS446)</b><br/>
    &nbsp;&nbsp;&nbsp;&nbsp;• <b>Shashank A (PES2UG24CS461)</b><br/>
    <br/>
    In partial fulfilment for the completion of fifth semester <b>DBMS Project (UE23CS351A / UE24CS351A)</b> in the Program of Study - <i>Bachelor of Technology in Computer Science and Engineering</i> under rules and regulations of PES University, Bengaluru during the period <b>AUG. 2026 – DEC. 2026</b>.
    <br/><br/>
    It is certified that all corrections / suggestions indicated for internal assessment have been incorporated in the report. The project has been approved as it satisfies the 5th semester academic requirements in respect of project work.
    """
    story.append(Paragraph(cert_text, body_style))
    story.append(Spacer(1, 40))

    sig_data = [
        [Paragraph("____________________________<br/><b>Dr. Shilpa S</b><br/>Assistant Professor<br/>Guide", body_style),
         Paragraph("____________________________<br/><b>Dr. Sandesh B J</b><br/>Professor & Chairperson<br/>Dept. of CSE", body_style)]
    ]
    t_sig = Table(sig_data, colWidths=[250, 250])
    story.append(t_sig)
    story.append(PageBreak())

    # ==========================================
    # 3. DECLARATION & ACKNOWLEDGEMENT
    # ==========================================
    story.append(Paragraph("DECLARATION", title_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#0284c7'), spaceAfter=15))

    decl_text = """We hereby declare that the DBMS Project entitled <b>"Algorithmic Execution Fingerprinting and Runtime Threat Detection System"</b> has been carried out by us under the guidance of <b>Dr. Shilpa S</b>, Assistant Professor, Department of Computer Science and Engineering, and submitted in partial fulfilment of the course requirements for the award of degree of Bachelor of Technology in Computer Science and Engineering of PES University, Bengaluru during the academic semester <b>AUG – DEC 2026</b>.
    <br/><br/>
    We further declare that this report has not been submitted previously to any other university or institution for any academic degree or diploma.
    """
    story.append(Paragraph(decl_text, body_style))
    story.append(Spacer(1, 20))

    dec_tbl = [
        [Paragraph("<b>Student Name</b>", body_style), Paragraph("<b>SRN</b>", body_style), Paragraph("<b>Signature</b>", body_style)],
        [Paragraph("Sanyam Deven Hiran", body_style), Paragraph("PES2UG24CS446", body_style), Paragraph("____________________", body_style)],
        [Paragraph("Shashank A", body_style), Paragraph("PES2UG24CS461", body_style), Paragraph("____________________", body_style)]
    ]
    t_dec = Table(dec_tbl, colWidths=[180, 140, 180])
    t_dec.setStyle(TableStyle([
        ('LINEBELOW', (0,0), (-1,0), 1, colors.HexColor('#0284c7')),
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f8fafc')),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('TOPPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_dec)
    story.append(Spacer(1, 30))

    story.append(Paragraph("ACKNOWLEDGEMENT", title_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#0284c7'), spaceAfter=15))
    ack_text = """We would like to express our gratitude to <b>Dr. Shilpa S</b>, Department of Computer Science and Engineering, PES University, for her continuous guidance, assistance, and encouragement throughout the development of this UE23CS351A - DBMS Project.
    <br/><br/>
    We take this opportunity to thank <b>Dr. Sandesh B J</b>, Professor, Chairperson, Department of Computer Science and Engineering, PES University, for all the knowledge and support we have received from the department.
    <br/><br/>
    We are deeply grateful to <b>Prof. Jawahar Doreswamy</b>, Chancellor – PES University, and <b>Dr. Suryaprasad J</b>, Vice-Chancellor, PES University for providing us various opportunities and enlightenment every step of the way. Finally, this project could not have been completed without the continual support and encouragement received from our families and peers.
    """
    story.append(Paragraph(ack_text, body_style))
    story.append(PageBreak())

    # ==========================================
    # 4. ABSTRACT & TABLE OF CONTENTS
    # ==========================================
    story.append(Paragraph("ABSTRACT", title_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#0284c7'), spaceAfter=15))
    abs_text = """Modern computing infrastructures across high-performance computing (HPC) clusters, enterprise clouds, and quantitative finance platforms face increasing risks from stealthy malicious workloads such as zero-day cryptojacking miners, reconnaissance port scanners, and cache-timing side-channel attacks. Traditional signature-based endpoint detection mechanisms rely upon static file hashes and byte-level heuristics that are trivial for adversaries to bypass through binary obfuscation, polymorphic compilation, and memory-only execution.
    <br/><br/>
    This project designs and implements an end-to-end <b>Algorithmic Execution Fingerprinting and Threat Detection Platform</b> centered on low-level microarchitectural hardware performance telemetry. By profiling runtime hardware counter vectors—including <b>Instructions Per Cycle (IPC)</b>, <b>L1/L3 Cache Miss Rates</b>, <b>Branch Misprediction Rates</b>, <b>Peak Memory Allocations</b>, and <b>Execution Durations</b>—the system captures an immutable physical signature of any executing process that cannot be obfuscated.
    <br/><br/>
    The platform combines a tripartite database architecture:
    <br/>
    1. <b>Relational Core (MySQL 8.0+)</b>: 7 strongly typed entities enforcing strict relational constraints, 1:1 run-to-fingerprint integrity, automated cascading, complex join queries, correlated subqueries, stored procedures, functions, automated threat-mitigation triggers, and recursive Common Table Expressions (CTEs) for polymorphic algorithm lineage tracking.
    <br/>
    2. <b>Graph Database (Neo4j / Cypher)</b>: A graph-native data model capturing multi-hop relationships (AUTHORED, EXECUTED_IN, RUNS_ON, FLAGGED_AS, DERIVED_FROM) to execute real-time threat blast-radius traversals and evaluate lateral attack propagation across cluster compute nodes.
    <br/>
    3. <b>Multidimensional Vector Database</b>: Normalized continuous telemetry vectorization utilizing Cosine Similarity and k-Nearest Neighbor (k-NN) indexing for sub-millisecond zero-day and anomalous workload detection against golden reference baselines, supplemented by complete Vector RUD (Read/Search, Update, Delete) capabilities.
    <br/><br/>
    The platform provides a modern <b>Next.js</b> fullstack dashboard featuring dual-tier <b>Role-Based Access Control (RBAC)</b> implemented synchronously at the database layer (sec_admin and sec_analyst) and front-end session layer. The system demonstrates automated containment through database triggers that terminate critical rogue processes in real time.
    """
    story.append(Paragraph(abs_text, body_style))
    story.append(Spacer(1, 25))

    story.append(Paragraph("TABLE OF CONTENTS", title_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#0284c7'), spaceAfter=15))

    toc_data = [
        [Paragraph("<b>Chapter</b>", body_style), Paragraph("<b>Title</b>", body_style), Paragraph("<b>Page</b>", body_style)],
        [Paragraph("1", body_style), Paragraph("INTRODUCTION & DOMAIN CONTEXT", body_style), Paragraph("5", body_style)],
        [Paragraph("2", body_style), Paragraph("PROBLEM DEFINITION & CONSTRAINTS", body_style), Paragraph("6", body_style)],
        [Paragraph("3", body_style), Paragraph("ER MODEL & ENTITY IDENTIFICATION", body_style), Paragraph("7", body_style)],
        [Paragraph("4", body_style), Paragraph("ER TO RELATIONAL MAPPING ALGORITHM", body_style), Paragraph("8", body_style)],
        [Paragraph("5", body_style), Paragraph("TECHNOLOGY JUSTIFICATION (MYSQL, NEO4J, VECTOR)", body_style), Paragraph("9", body_style)],
        [Paragraph("6", body_style), Paragraph("DDL STATEMENTS WITH CONSTRAINTS", body_style), Paragraph("10", body_style)],
        [Paragraph("7", body_style), Paragraph("DML STATEMENTS & DATA GENERATION ENGINE", body_style), Paragraph("11", body_style)],
        [Paragraph("8", body_style), Paragraph("RELATIONAL QUERIES, CTEs & RECURSIVE LINEAGE", body_style), Paragraph("12", body_style)],
        [Paragraph("9", body_style), Paragraph("ADVANCED SQL: PROCEDURES, FUNCTIONS & TRIGGERS", body_style), Paragraph("13", body_style)],
        [Paragraph("10", body_style), Paragraph("NOSQL GRAPH DATABASE (NEO4J) & BLAST RADIUS", body_style), Paragraph("14", body_style)],
        [Paragraph("11", body_style), Paragraph("VECTOR DATABASE & k-NN ZERO-DAY DETECTION", body_style), Paragraph("15", body_style)],
        [Paragraph("12", body_style), Paragraph("ROLE-BASED ACCESS CONTROL (RBAC) & AUTH", body_style), Paragraph("16", body_style)],
        [Paragraph("13", body_style), Paragraph("FRONT END DEVELOPMENT (NEXT.JS & API)", body_style), Paragraph("17", body_style)],
        [Paragraph("14", body_style), Paragraph("GIT/GITHUB & DOCUMENTATION", body_style), Paragraph("18", body_style)],
        [Paragraph("15", body_style), Paragraph("ORIGINALITY, CONTRIBUTIONS & VIVA PREPARATION", body_style), Paragraph("19", body_style)],
        [Paragraph("16", body_style), Paragraph("REFERENCES & BIBLIOGRAPHY", body_style), Paragraph("20", body_style)]
    ]
    t_toc = Table(toc_data, colWidths=[50, 390, 60])
    t_toc.setStyle(TableStyle([
        ('LINEBELOW', (0,0), (-1,0), 1, colors.HexColor('#0284c7')),
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f8fafc')),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
    ]))
    story.append(t_toc)
    story.append(PageBreak())

    # ==========================================
    # CHAPTERS 1 & 2
    # ==========================================
    story.append(Paragraph("1. INTRODUCTION", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#0284c7'), spaceAfter=8))
    intro_p1 = """<b>1.1 Domain Context & Microarchitectural Profiling:</b><br/>
    In modern high-performance computing clusters and cloud environments, software processes execute directly upon physical CPU silicon. Every program, irrespective of its source language (C++, Rust, Go, Python), produces a distinctive stream of hardware micro-events captured by CPU Hardware Performance Counters (HPCs). Key profiled metrics include:
    <br/>
    • <b>Instructions Per Cycle (IPC):</b> Measure of instruction retirement throughput. High-performance compute routines exhibit high IPC (2.5 – 3.5), whereas stalls and memory bottlenecks yield low IPC (0.3 – 0.8).<br/>
    • <b>Cache Miss Rate (%):</b> Frequency of memory requests failing in L1/L3 CPU caches and stalling upon main system DRAM. Memory-hard cryptomining loops (e.g. RandomX, Ethash) exhibit characteristic cache thrashing (30% – 50%).<br/>
    • <b>Branch Misprediction Rate (%):</b> Failure frequency of branch prediction units, elevated in network socket scanning and reconnaissance loops (10% – 20%).<br/>
    • <b>Peak Memory Footprint (MB):</b> Physical resident memory allocated by the operating system.
    """
    story.append(Paragraph(intro_p1, body_style))
    story.append(Spacer(1, 4))

    intro_p2 = """<b>1.2 Motivation & Threat Landscape:</b><br/>
    Adversaries routinely bypass traditional file-hash (MD5/SHA-256) Antivirus scanners using polymorphic compilation, binary obfuscation, and fileless execution. However, software cannot hide its physical execution footprint on the hardware. Profiling these physical counters provides an immutable behavioral fingerprint capable of unmasking hidden malware.
    """
    story.append(Paragraph(intro_p2, body_style))
    story.append(Spacer(1, 10))

    story.append(Paragraph("2. PROBLEM DEFINITION", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#0284c7'), spaceAfter=8))
    prob_p1 = """To design, implement, and evaluate an <b>Algorithmic Execution Fingerprinting and Runtime Threat Detection System</b> that captures low-level microprocessor telemetry into a normalized relational database, models lateral entity interactions in a graph database, classifies zero-day anomalies using a vector database, enforces multi-role access control, and surfaces real-time insights through a responsive Next.js frontend.
    <br/><br/>
    <b>Domain Constraints Enforced:</b><br/>
    1. <b>Strict 1:1 Run-to-Fingerprint Mapping:</b> Each completed execution run produces exactly one fingerprint.<br/>
    2. <b>Chronological Consistency:</b> For all finished runs, <i>end_time > start_time</i>.<br/>
    3. <b>Counter Bounds:</b> IPC ratio must be non-negative; cache miss and branch misprediction rates strictly within [0.00%, 100.00%].<br/>
    4. <b>Automated Defense:</b> Real-time database triggers must immediately terminate runs flagged as Critical threats.
    """
    story.append(Paragraph(prob_p1, body_style))
    story.append(PageBreak())

    # ==========================================
    # CHAPTER 3: ER MODEL
    # ==========================================
    story.append(Paragraph("3. ER MODEL", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#0284c7'), spaceAfter=8))
    er_desc = """The Entity-Relationship model comprises seven entities capturing the lifecycle of algorithmic execution, compute hardware, golden reference profiles, and security detection audits.
    <br/><br/>
    <b>Entities & Structural Cardinalities:</b><br/>
    • <b>DEVELOPER (1) to ALGORITHM (N):</b> Authorship relationship.<br/>
    • <b>COMPUTE_NODE (1) to EXECUTION_RUN (N):</b> Cluster hosting relationship.<br/>
    • <b>ALGORITHM (1) to EXECUTION_RUN (N):</b> Instantiation relationship.<br/>
    • <b>EXECUTION_RUN (1) to FINGERPRINT (1):</b> Strict 1:1 hardware telemetry profile.<br/>
    • <b>FINGERPRINT (M) to BASELINE_PATTERN (N) via DETECTION_LOG:</b> Many-to-many junction relationship capturing similarity evaluation and threat classification.<br/>
    • <b>ALGORITHM (1) to ALGORITHM (N):</b> Unary self-referencing relationship representing polymorphic version lineages.
    """
    story.append(Paragraph(er_desc, body_style))
    story.append(Spacer(1, 8))

    er_img_path = "report_assets/er_diagram.png"
    if os.path.exists(er_img_path):
        story.append(Paragraph("<b>Figure 3.1: Entity-Relationship (ER) Diagram (Canva)</b>", h2_style))
        story.append(Image(er_img_path, width=6.2*inch, height=5.6*inch))
    story.append(PageBreak())

    # ==========================================
    # CHAPTER 4: ER TO RELATIONAL MAPPING
    # ==========================================
    story.append(Paragraph("4. ER TO RELATIONAL MAPPING", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#0284c7'), spaceAfter=8))
    map_text = """<b>4.1 Steps of Algorithm for Chosen Problem:</b><br/>
    • <b>Step 1 (Strong Entities):</b> Map DEVELOPER, COMPUTE_NODE, and BASELINE_PATTERN into independent relations with primary keys dev_id, node_id, and baseline_id.<br/>
    • <b>Step 2 (1:N Relationships):</b> In ALGORITHM, place dev_id as foreign key referencing DEVELOPER(dev_id). Add parent_algo_id referencing ALGORITHM(algo_id). In EXECUTION_RUN, place algo_id and node_id as foreign keys.<br/>
    • <b>Step 3 (1:1 Relationship):</b> Map FINGERPRINT by placing run_id as foreign key referencing EXECUTION_RUN(run_id) with a UNIQUE constraint to guarantee 1:1 cardinality.<br/>
    • <b>Step 4 (M:N Relationship):</b> Create junction relation DETECTION_LOG with foreign keys fingerprint_id and baseline_id, plus similarity_score, alert_level, and classification_result.
    """
    story.append(Paragraph(map_text, body_style))
    story.append(Spacer(1, 8))

    schema_img_path = "report_assets/schema_diagram.png"
    if os.path.exists(schema_img_path):
        story.append(Paragraph("<b>Figure 4.1: Complete Diagram of Relational Mapping (Canva)</b>", h2_style))
        story.append(Image(schema_img_path, width=6.2*inch, height=4.2*inch))
    story.append(PageBreak())

    # ==========================================
    # CHAPTER 5: TECHNOLOGY JUSTIFICATION
    # ==========================================
    story.append(Paragraph("5. TECHNOLOGY JUSTIFICATION", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#0284c7'), spaceAfter=8))
    tech_text = """<b>5.1 Relational Database: MySQL 8.0+</b><br/>
    • <b>ACID Transactions & Strict Integrity:</b> Hardware performance telemetry must be recorded with transactional consistency. Cascading foreign keys prevent orphaned execution records.<br/>
    • <b>Zero-Latency Trigger Containment:</b> When a detection log with 'Critical' alert is inserted, an in-database trigger synchronously mutates the execution run status to 'Terminated', isolating rogue processes in real time.<br/>
    • <b>Advanced SQL & RBAC:</b> Native support for recursive CTEs, window functions, stored procedures, deterministic functions, and native role-based access control (sec_admin and sec_analyst).
    <br/><br/>
    <b>5.2 NoSQL Graph Database: Neo4j & Cypher</b><br/>
    • <b>Overcoming Relational Join Degradation:</b> Analyzing lateral attack propagation (e.g. "Which compute servers and developers are reachable within 3 hops of a compromised algorithm?") requires recursive multi-table joins in SQL that scale at O(N^k). Neo4j uses index-free adjacency to perform pointer traversals in O(k) constant time.<br/>
    • <b>Threat Blast Radius:</b> Cypher queries traverse relationships (AUTHORED, EXECUTED_IN, RUNS_ON, FLAGGED_AS) to compute the full blast radius of infected processes.
    <br/><br/>
    <b>5.3 Multidimensional Vector Database (Cosine Sim & k-NN)</b><br/>
    • <b>Continuous Coordinate Nature:</b> Hardware telemetry is fundamentally continuous: v = [IPC, CacheMiss, BranchMispred, PeakMem, Duration].<br/>
    • <b>Zero-Day Polymorphic Detection:</b> Attackers obfuscate code to change file hashes, but cannot alter execution physics. The vector engine calculates Cosine Similarity against golden baselines and historical attacks, detecting novel zero-day cryptojacking variants with >97% similarity.<br/>
    • <b>Complete Vector RUD:</b> Full Read/Search (k-NN), Update, and Delete lifecycle management.
    <br/><br/>
    <b>5.4 Fullstack Application: Next.js & Python API</b><br/>
    Next.js provides a reactive, server-rendered dashboard with Tailwind CSS. FastAPI delivers high-throughput connectivity to PyMySQL, Neo4j, and the Vector DB.
    """
    story.append(Paragraph(tech_text, body_style))
    story.append(PageBreak())

    # ==========================================
    # CHAPTER 6: DDL STATEMENTS
    # ==========================================
    story.append(Paragraph("6. DDL STATEMENTS WITH CONSTRAINTS", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#0284c7'), spaceAfter=8))
    ddl_code = """-- Database Schema Definition with Constraints
CREATE DATABASE IF NOT EXISTS algo_fingerprint_db;
USE algo_fingerprint_db;

CREATE TABLE DEVELOPER (
    dev_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    team VARCHAR(50) NOT NULL
);

CREATE TABLE COMPUTE_NODE (
    node_id INT PRIMARY KEY AUTO_INCREMENT,
    hostname VARCHAR(100) NOT NULL UNIQUE,
    ip_address VARCHAR(45) NOT NULL,
    cpu_architecture VARCHAR(50) NOT NULL,
    os_name VARCHAR(50) NOT NULL
);

CREATE TABLE BASELINE_PATTERN (
    baseline_id INT PRIMARY KEY AUTO_INCREMENT,
    pattern_name VARCHAR(100) NOT NULL UNIQUE,
    category VARCHAR(50) NOT NULL,
    expected_ipc DECIMAL(5,2) NOT NULL,
    expected_cache_miss_rate DECIMAL(5,2) NOT NULL
);

CREATE TABLE ALGORITHM (
    algo_id INT PRIMARY KEY AUTO_INCREMENT,
    dev_id INT NOT NULL,
    algo_name VARCHAR(100) NOT NULL,
    language VARCHAR(50) NOT NULL,
    version VARCHAR(20) NOT NULL,
    parent_algo_id INT NULL,
    FOREIGN KEY (dev_id) REFERENCES DEVELOPER(dev_id) ON DELETE CASCADE,
    FOREIGN KEY (parent_algo_id) REFERENCES ALGORITHM(algo_id) ON DELETE SET NULL
);

CREATE TABLE EXECUTION_RUN (
    run_id INT PRIMARY KEY AUTO_INCREMENT,
    algo_id INT NOT NULL,
    node_id INT NOT NULL,
    start_time DATETIME NOT NULL,
    end_time DATETIME NULL,
    execution_status VARCHAR(30) NOT NULL,
    peak_memory_mb DECIMAL(10,2) NULL,
    FOREIGN KEY (algo_id) REFERENCES ALGORITHM(algo_id) ON DELETE CASCADE,
    FOREIGN KEY (node_id) REFERENCES COMPUTE_NODE(node_id) ON DELETE CASCADE
);

CREATE TABLE FINGERPRINT (
    fingerprint_id INT PRIMARY KEY AUTO_INCREMENT,
    run_id INT NOT NULL UNIQUE,
    ipc_ratio DECIMAL(6,3) NOT NULL,
    cache_miss_rate DECIMAL(5,2) NOT NULL,
    branch_misprediction_rate DECIMAL(5,2) NOT NULL,
    signature_hash VARCHAR(64) NOT NULL UNIQUE,
    FOREIGN KEY (run_id) REFERENCES EXECUTION_RUN(run_id) ON DELETE CASCADE
);

CREATE TABLE DETECTION_LOG (
    detection_id INT PRIMARY KEY AUTO_INCREMENT,
    fingerprint_id INT NOT NULL,
    baseline_id INT NOT NULL,
    similarity_score DECIMAL(5,2) NOT NULL,
    alert_level VARCHAR(20) NOT NULL,
    classification_result VARCHAR(50) NOT NULL,
    FOREIGN KEY (fingerprint_id) REFERENCES FINGERPRINT(fingerprint_id) ON DELETE CASCADE,
    FOREIGN KEY (baseline_id) REFERENCES BASELINE_PATTERN(baseline_id) ON DELETE CASCADE
);"""
    story.append(Paragraph(ddl_code.replace('\n', '<br/>').replace(' ', '&nbsp;'), code_style))
    story.append(PageBreak())

    # ==========================================
    # CHAPTER 7: DML STATEMENTS
    # ==========================================
    story.append(Paragraph("7. DML STATEMENTS & DATA INGESTION", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#0284c7'), spaceAfter=8))
    dml_text = """A custom synthetic data generator built with Faker and NumPy generated semantically congruent execution traces across 5 core archetypes:
    <br/><br/>
    • <b>HPC Matrix BLAS:</b> High IPC (2.5 – 3.5), low cache miss (1.5% – 5.0%), peak memory > 1 GB.<br/>
    • <b>Cryptojacking Malware:</b> Low IPC (0.5 – 0.85), high cache miss (30% – 48%), high branch mispred (12% – 22%).<br/>
    • <b>Port Scan SYN Probe:</b> Low IPC (0.3 – 0.6), high cache miss (20% – 35%), low memory (< 256 MB).<br/>
    • <b>Financial HFT:</b> Moderate IPC (1.2 – 1.7), low cache miss (5% – 9%).<br/>
    • <b>Sorting Utilities:</b> Moderate IPC (1.9 – 2.4), cache miss (6% – 11%).
    <br/><br/>
    <b>Ingestion Verification Table Counts:</b>
    """
    story.append(Paragraph(dml_text, body_style))
    story.append(Spacer(1, 6))

    counts_data = [
        [Paragraph("<b>Table Name</b>", body_style), Paragraph("<b>Populated Tuples</b>", body_style), Paragraph("<b>Integrity Constraints Enforced</b>", body_style)],
        [Paragraph("DEVELOPER", body_style), Paragraph("75", body_style), Paragraph("Unique email addresses across 5 engineering teams", body_style)],
        [Paragraph("COMPUTE_NODE", body_style), Paragraph("35", body_style), Paragraph("Unique hostnames & private CIDR IP addresses", body_style)],
        [Paragraph("BASELINE_PATTERN", body_style), Paragraph("25", body_style), Paragraph("Golden reference profiles across 8 domains", body_style)],
        [Paragraph("ALGORITHM", body_style), Paragraph("300", body_style), Paragraph("Polyglot (C++, Rust, Go, Python, C) with semantic versions", body_style)],
        [Paragraph("EXECUTION_RUN", body_style), Paragraph("4,000", body_style), Paragraph("Chronological constraint (end_time > start_time)", body_style)],
        [Paragraph("FINGERPRINT", body_style), Paragraph("3,637", body_style), Paragraph("Strict 1:1 foreign key with SHA-256 signature hash", body_style)],
        [Paragraph("DETECTION_LOG", body_style), Paragraph("9,078", body_style), Paragraph("Cross-baseline similarity scores and severity alerts", body_style)],
        [Paragraph("vw_critical_security_anomalies", body_style), Paragraph("1,716", body_style), Paragraph("Relational security audit view (Critical & High)", body_style)]
    ]
    t_cnt = Table(counts_data, colWidths=[150, 90, 260])
    t_cnt.setStyle(TableStyle([
        ('LINEBELOW', (0,0), (-1,0), 1, colors.HexColor('#0284c7')),
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f0f9ff')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('TOPPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_cnt)
    story.append(PageBreak())

    # ==========================================
    # CHAPTER 8: RELATIONAL QUERIES
    # ==========================================
    story.append(Paragraph("8. RELATIONAL QUERIES & ADVANCED SQL", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#0284c7'), spaceAfter=8))

    q_text = """<b>8.1 Simple Aggregate Query with GROUP BY:</b>"""
    story.append(Paragraph(q_text, body_style))
    story.append(Paragraph("""SELECT cn.cpu_architecture, COUNT(DISTINCT r.run_id) AS runs,
       ROUND(AVG(f.ipc_ratio), 3) AS mean_ipc, ROUND(AVG(f.cache_miss_rate), 2) AS mean_cm
FROM COMPUTE_NODE cn
JOIN EXECUTION_RUN r ON cn.node_id = r.node_id
JOIN FINGERPRINT f ON r.run_id = f.run_id
GROUP BY cn.cpu_architecture;""".replace('\n', '<br/>').replace(' ', '&nbsp;'), code_style))

    story.append(Paragraph("<b>8.2 Correlated Subquery:</b> Peak memory exceeding programming language average:", body_style))
    story.append(Paragraph("""SELECT a1.algo_name, a1.language, er1.run_id, er1.peak_memory_mb
FROM ALGORITHM a1
JOIN EXECUTION_RUN er1 ON a1.algo_id = er1.algo_id
WHERE er1.peak_memory_mb > (
    SELECT AVG(er2.peak_memory_mb)
    FROM ALGORITHM a2
    JOIN EXECUTION_RUN er2 ON a2.algo_id = er2.algo_id
    WHERE a2.language = a1.language
)
ORDER BY er1.peak_memory_mb DESC LIMIT 5;""".replace('\n', '<br/>').replace(' ', '&nbsp;'), code_style))

    story.append(Paragraph("<b>8.3 Common Table Expression (CTE):</b> Team threat density scoring:", body_style))
    story.append(Paragraph("""WITH TeamMetrics AS (
    SELECT d.team, COUNT(DISTINCT r.run_id) AS total_runs,
           SUM(CASE WHEN dl.alert_level = 'Critical' THEN 1 ELSE 0 END) AS critical_count
    FROM DEVELOPER d
    JOIN ALGORITHM a ON d.dev_id = a.dev_id
    JOIN EXECUTION_RUN r ON a.algo_id = r.algo_id
    JOIN FINGERPRINT f ON r.run_id = f.run_id
    JOIN DETECTION_LOG dl ON f.fingerprint_id = dl.fingerprint_id
    GROUP BY d.team
)
SELECT team, total_runs, critical_count, ROUND((critical_count / total_runs) * 100, 2) AS threat_density_pct
FROM TeamMetrics ORDER BY threat_density_pct DESC;""".replace('\n', '<br/>').replace(' ', '&nbsp;'), code_style))

    story.append(Paragraph("<b>8.4 Recursive CTE Query:</b> Polymorphic Algorithm Lineage Traversal:", body_style))
    story.append(Paragraph("""WITH RECURSIVE AlgoLineage AS (
    SELECT algo_id, algo_name, version, parent_algo_id, 1 AS lineage_depth, CAST(algo_name AS CHAR(500)) AS lineage_path
    FROM ALGORITHM
    WHERE parent_algo_id IS NULL AND algo_id IN (2, 4, 6, 14)
    UNION ALL
    SELECT a.algo_id, a.algo_name, a.version, a.parent_algo_id, al.lineage_depth + 1, CONCAT(al.lineage_path, ' -> ', a.algo_name)
    FROM ALGORITHM a
    JOIN AlgoLineage al ON a.parent_algo_id = al.algo_id
    WHERE al.lineage_depth < 10
)
SELECT algo_id, lineage_depth, lineage_path FROM AlgoLineage ORDER BY lineage_path;""".replace('\n', '<br/>').replace(' ', '&nbsp;'), code_style))
    story.append(PageBreak())

    # ==========================================
    # CHAPTER 9: PROCEDURES, FUNCTIONS & TRIGGERS
    # ==========================================
    story.append(Paragraph("9. ADVANCED SQL: PROCEDURES, FUNCTIONS & TRIGGERS", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#0284c7'), spaceAfter=8))

    story.append(Paragraph("<b>9.1 Stored Procedure: GetRunFingerprintProfile</b>", body_style))
    story.append(Paragraph("""DELIMITER //
CREATE PROCEDURE GetRunFingerprintProfile(IN p_run_id INT)
BEGIN
    SELECT er.run_id, a.algo_name, a.language, d.name AS dev_name, cn.hostname,
           er.start_time, er.end_time, er.peak_memory_mb, fp.ipc_ratio, fp.cache_miss_rate,
           bp.pattern_name AS matched_pattern, dl.similarity_score, dl.alert_level, dl.classification_result
    FROM EXECUTION_RUN er
    JOIN ALGORITHM a ON er.algo_id = a.algo_id
    JOIN DEVELOPER d ON a.dev_id = d.dev_id
    JOIN COMPUTE_NODE cn ON er.node_id = cn.node_id
    LEFT JOIN FINGERPRINT fp ON er.run_id = fp.run_id
    LEFT JOIN DETECTION_LOG dl ON fp.fingerprint_id = dl.fingerprint_id
    LEFT JOIN BASELINE_PATTERN bp ON dl.baseline_id = bp.baseline_id
    WHERE er.run_id = p_run_id;
END //
DELIMITER ;""".replace('\n', '<br/>').replace(' ', '&nbsp;'), code_style))

    story.append(Paragraph("<b>9.2 Stored Function: CalculateIPCDeviation</b>", body_style))
    story.append(Paragraph("""DELIMITER //
CREATE FUNCTION CalculateIPCDeviation(p_fingerprint_id INT) RETURNS DECIMAL(6,2)
READS SQL DATA DETERMINISTIC
BEGIN
    DECLARE v_meas DECIMAL(6,3); DECLARE v_exp DECIMAL(5,2);
    SELECT fp.ipc_ratio, bp.expected_ipc INTO v_meas, v_exp
    FROM FINGERPRINT fp
    JOIN DETECTION_LOG dl ON fp.fingerprint_id = dl.fingerprint_id
    JOIN BASELINE_PATTERN bp ON dl.baseline_id = bp.baseline_id
    WHERE fp.fingerprint_id = p_fingerprint_id LIMIT 1;
    IF v_meas IS NULL OR v_exp IS NULL THEN RETURN NULL; END IF;
    RETURN ROUND((ABS(v_meas - v_exp) / v_exp) * 100, 2);
END //
DELIMITER ;""".replace('\n', '<br/>').replace(' ', '&nbsp;'), code_style))

    story.append(Paragraph("<b>9.3 Automated Threat Mitigation Trigger (AFTER INSERT):</b>", body_style))
    story.append(Paragraph("""DELIMITER //
CREATE TRIGGER trg_auto_terminate_critical_threat 
AFTER INSERT ON DETECTION_LOG FOR EACH ROW
BEGIN
    IF NEW.alert_level = 'Critical' THEN
        UPDATE EXECUTION_RUN
        SET execution_status = 'Terminated'
        WHERE run_id = (SELECT run_id FROM FINGERPRINT WHERE fingerprint_id = NEW.fingerprint_id);
    END IF;
END //
DELIMITER ;""".replace('\n', '<br/>').replace(' ', '&nbsp;'), code_style))
    story.append(PageBreak())

    # ==========================================
    # CHAPTERS 10 & 11: NEO4J & VECTOR DB
    # ==========================================
    story.append(Paragraph("10. NOSQL GRAPH DATABASE (NEO4J) & BLAST RADIUS", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#0284c7'), spaceAfter=8))
    neo_text = """The Neo4j database models the connected entities of the system:
    <br/>
    • <b>Nodes:</b> (:Developer), (:Algorithm), (:ExecutionRun), (:ComputeNode), (:BaselinePattern)<br/>
    • <b>Edges:</b> (:Developer)-[:AUTHORED]->(:Algorithm), (:Algorithm)-[:EXECUTED_IN]->(:ExecutionRun), (:ExecutionRun)-[:RUNS_ON]->(:ComputeNode), (:Algorithm)-[:DERIVED_FROM]->(:Algorithm)<br/>
    <br/>
    <b>Threat Blast Radius Cypher Query:</b>
    """
    story.append(Paragraph(neo_text, body_style))
    story.append(Paragraph("""MATCH path = (a:Algorithm {algo_id: 2})-[:EXECUTED_IN|RUNS_ON|AUTHORED*1..3]-(n)
RETURN path;""".replace('\n', '<br/>').replace(' ', '&nbsp;'), code_style))

    story.append(Spacer(1, 10))
    story.append(Paragraph("11. VECTOR DATABASE & k-NN ZERO-DAY DETECTION", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#0284c7'), spaceAfter=8))
    vec_text = """The vector database models continuous microarchitectural counters across 5 normalized dimensions:
    <br/>
    v = [IPC, CacheMiss%, BranchMispred%, PeakMemoryMB, DurationSeconds]
    <br/><br/>
    <b>Cosine Similarity Formula:</b><br/>
    Sim(u, v) = (u • v) / (||u|| ||v||) * 100%
    <br/><br/>
    <b>Zero-Day Threat Retrieval:</b> When an unknown polymorphic miner executes with IPC = 0.62, Cache Miss = 36.5%, and Branch Mispred = 15.2%, the k-NN vector search matches known cryptojacking signatures with <b>98.19% similarity</b>, correctly classifying the zero-day workload.
    <br/><br/>
    <b>Vector RUD Implementation:</b><br/>
    • <b>Read (Search):</b> Top-K nearest neighbor retrieval via cosine distance.<br/>
    • <b>Update:</b> Dynamically recalibrates embedding coordinates upon process completion.<br/>
    • <b>Delete:</b> Purges obsolete or benchmark calibration vectors from index.
    """
    story.append(Paragraph(vec_text, body_style))
    story.append(PageBreak())

    # ==========================================
    # CHAPTERS 12 & 13: RBAC & FRONTEND
    # ==========================================
    story.append(Paragraph("12. ROLE-BASED ACCESS CONTROL (RBAC)", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#0284c7'), spaceAfter=8))
    rbac_text = """Dual-tier Role-Based Access Control is enforced at both the MySQL database engine level and the frontend Next.js interface:
    <br/><br/>
    1. <b>sec_admin (SecOps Administrator):</b> Possesses full administrative authority (GRANT ALL PRIVILEGES). Permitted to execute DDL, alter schema, calibrate baselines, and quarantine compute nodes.<br/>
    2. <b>sec_analyst (Security Analyst):</b> Possesses restricted SELECT privileges across all tables and views, INSERT privileges on telemetry logs, and EXECUTE on stored procedures and functions. Explicitly restricted from DDL, DROP, and user manipulation.
    """
    story.append(Paragraph(rbac_text, body_style))
    story.append(Paragraph("""CREATE ROLE IF NOT EXISTS 'sec_admin', 'sec_analyst';
GRANT ALL PRIVILEGES ON algo_fingerprint_db.* TO 'sec_admin' WITH GRANT OPTION;
GRANT SELECT ON algo_fingerprint_db.* TO 'sec_analyst';
GRANT INSERT ON algo_fingerprint_db.detection_log TO 'sec_analyst';
GRANT EXECUTE ON PROCEDURE algo_fingerprint_db.GetRunFingerprintProfile TO 'sec_analyst';
CREATE USER IF NOT EXISTS 'admin_user'@'localhost' IDENTIFIED BY 'Admin@Sec2026!';
CREATE USER IF NOT EXISTS 'analyst_user'@'localhost' IDENTIFIED BY 'Analyst@Sec2026!';
GRANT 'sec_admin' TO 'admin_user'@'localhost';
GRANT 'sec_analyst' TO 'analyst_user'@'localhost';
FLUSH PRIVILEGES;""".replace('\n', '<br/>').replace(' ', '&nbsp;'), code_style))

    story.append(Spacer(1, 10))
    story.append(Paragraph("13. FRONT END DEVELOPMENT & API INTEGRATION", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#0284c7'), spaceAfter=8))
    ui_text = """The frontend is constructed using <b>Next.js</b> (React, TypeScript, Tailwind CSS) connected to a high-speed Python FastAPI backend (Uvicorn).
    <br/><br/>
    <b>Interactive Modules:</b><br/>
    1. <b>Telemetry Dashboard:</b> Overview KPIs (4,000 runs, 3,637 fingerprints, 827 critical alerts), architecture distribution, and alert severities.<br/>
    2. <b>Threat Detection Log:</b> Live view of vw_critical_security_anomalies with 1-click compute node quarantine.<br/>
    3. <b>Neo4j Threat Graph Explorer:</b> Visual multi-hop blast radius explorer with depth slider.<br/>
    4. <b>Vector DB k-NN Matcher:</b> Interactive hardware counter sliders computing real-time Cosine Similarity against golden baselines.<br/>
    5. <b>SQL Playground:</b> Query runner executing recursive CTEs, correlated subqueries, procedures, and trigger bounds tests with live RBAC permission checks.
    """
    story.append(Paragraph(ui_text, body_style))
    story.append(PageBreak())

    # ==========================================
    # CHAPTERS 14, 15 & 16: GIT, VIVA, REFERENCES
    # ==========================================
    story.append(Paragraph("14. GIT/GITHUB & DOCUMENTATION", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#0284c7'), spaceAfter=8))
    git_text = """The project repository is maintained under structured Git version control:
    <br/>
    • <b>Source Repository:</b> Mini-project codebase containing SQL scripts, Python data generators, FastAPI server, Next.js frontend, and report documentation.<br/>
    • <b>GitHub Link:</b> https://github.com/Mint-SDH/DBMS-Mini-Project
    """
    story.append(Paragraph(git_text, body_style))

    story.append(Spacer(1, 10))
    story.append(Paragraph("15. ORIGINALITY, CONTRIBUTIONS & VIVA PREPARATION", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#0284c7'), spaceAfter=8))
    viva_text = """<b>15.1 Originality of the Work:</b><br/>
    Unlike traditional database projects focused on business billing or hostel management, this project innovates by treating microarchitectural hardware performance counters as database entities. The convergence of relational ACID integrity (MySQL), relationship-first blast radius traversal (Neo4j), and continuous metric spaces (Vector DB) provides a multi-model defense architecture.
    <br/><br/>
    <b>15.2 Individual Contributions:</b><br/>
    • <b>Sanyam Deven Hiran (PES2UG24CS446):</b> Conceptualized domain counter distribution, formulated the ER schema and relational mapping, authored MySQL DDL, stored procedures, deterministic functions, and automated threat mitigation triggers. Engineered the Vector Database engine and FastAPI backend.<br/>
    • <b>Shashank A (PES2UG24CS461):</b> Engineered synthetic data generation using Faker/NumPy, formulated complex relational queries and recursive CTEs, integrated the Neo4j Graph Database and Cypher traversals, developed the Next.js frontend UI, and compiled documentation.
    <br/><br/>
    <b>15.3 Key Viva Voce Concepts:</b><br/>
    • <b>1:1 Cardinality Enforcement:</b> Enforced by declaring FINGERPRINT(run_id) as both FOREIGN KEY and UNIQUE.<br/>
    • <b>Trigger Threat Mitigation:</b> trg_auto_terminate_critical_threat intercepts critical alerts upon insertion and synchronously updates execution_run.execution_status to 'Terminated'.<br/>
    • <b>Why Vector DB over SQL:</b> Continuous hardware telemetry is not discrete. Zero-day attacks modify code to alter static hashes, but vector cosine distance matches their continuous performance coordinates with >98% accuracy.
    """
    story.append(Paragraph(viva_text, body_style))

    story.append(Spacer(1, 10))
    story.append(Paragraph("16. REFERENCES & BIBLIOGRAPHY", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#0284c7'), spaceAfter=8))
    refs = """1. Elmasri, R., & Navathe, S. B. (2015). <i>Fundamentals of Database Systems</i> (7th ed.). Pearson.<br/>
    2. Silberschatz, A., Korth, H. F., & Sudarshan, S. (2019). <i>Database System Concepts</i> (7th ed.). McGraw-Hill.<br/>
    3. MySQL 8.0 Reference Manual. (2026). <i>Triggers, Stored Procedures, and Common Table Expressions</i>. Oracle Corporation.<br/>
    4. Robinson, I., Webber, J., & Eifrem, E. (2015). <i>Graph Databases: New Opportunities for Connected Data</i>. O'Reilly Media.<br/>
    5. Han, J., Kamber, M., & Pei, J. (2011). <i>Data Mining: Concepts and Techniques</i> (3rd ed.). Morgan Kaufmann.<br/>
    6. Intel Corporation. (2026). <i>Intel 64 and IA-32 Architectures Software Developer’s Manual: Hardware Performance Counter Monitoring</i>.<br/>
    7. PES University CSE Department. (2026). <i>UE23CS351A / UE24CS351A Mini Project Guidelines & Evaluation Rubrics</i>.
    """
    story.append(Paragraph(refs, body_style))

    # Build the document
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Successfully generated academic report PDF: {PDF_OUTPUT}")

if __name__ == "__main__":
    build_pdf()

