from pathlib import Path

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_ALIGN_VERTICAL, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "COMP4145_PD2_Final_Report.docx"
ASSETS = ROOT / "docs" / "assets"
INK = "17324D"
LINE = "D9D9D9"
PALE = "EAF0F5"


def set_cell_fill(cell, color):
    properties = cell._tc.get_or_add_tcPr()
    shading = properties.find(qn("w:shd"))
    if shading is None:
        shading = OxmlElement("w:shd")
        properties.append(shading)
    shading.set(qn("w:fill"), color)


def set_cell_borders(cell, color=LINE):
    properties = cell._tc.get_or_add_tcPr()
    borders = properties.first_child_found_in("w:tcBorders")
    if borders is None:
        borders = OxmlElement("w:tcBorders")
        properties.append(borders)
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        element = borders.find(qn(f"w:{edge}"))
        if element is None:
            element = OxmlElement(f"w:{edge}")
            borders.append(element)
        element.set(qn("w:val"), "single")
        element.set(qn("w:sz"), "6")
        element.set(qn("w:color"), color)


def format_table(table, widths=None):
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    for row_index, row in enumerate(table.rows):
        for column_index, cell in enumerate(row.cells):
            cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
            set_cell_borders(cell)
            if widths:
                cell.width = Inches(widths[column_index])
            for paragraph in cell.paragraphs:
                paragraph.paragraph_format.space_before = Pt(2)
                paragraph.paragraph_format.space_after = Pt(2)
                for run in paragraph.runs:
                    run.font.name = "Arial"
                    run.font.size = Pt(8.5)
                    run.font.color.rgb = RGBColor(0, 0, 0)
            if row_index == 0:
                set_cell_fill(cell, INK)
                for run in cell.paragraphs[0].runs:
                    run.bold = True
                    run.font.color.rgb = RGBColor(255, 255, 255)
    table.rows[0]._tr.get_or_add_trPr().append(OxmlElement("w:tblHeader"))


def add_table(doc, headers, rows, widths):
    table = doc.add_table(rows=1, cols=len(headers))
    for index, header in enumerate(headers):
        table.rows[0].cells[index].text = header
    for row in rows:
        cells = table.add_row().cells
        for index, value in enumerate(row):
            cells[index].text = str(value)
    format_table(table, widths)
    return table


def heading(doc, text, level=1):
    paragraph = doc.add_heading(text, level=level)
    paragraph.paragraph_format.space_before = Pt(5)
    paragraph.paragraph_format.space_after = Pt(4)
    paragraph.paragraph_format.keep_with_next = True
    return paragraph


def paragraph(doc, text, bold_lead=None):
    item = doc.add_paragraph()
    item.paragraph_format.space_after = Pt(4)
    item.paragraph_format.line_spacing = 1.02
    if bold_lead:
        run = item.add_run(bold_lead)
        run.bold = True
    item.add_run(text)
    return item


def bullets(doc, items):
    for text in items:
        item = doc.add_paragraph(style="List Bullet")
        item.paragraph_format.space_after = Pt(2)
        item.paragraph_format.left_indent = Inches(0.2)
        item.paragraph_format.first_line_indent = Inches(-0.14)
        item.add_run(text)


def page_title(doc, title, subtitle):
    title_paragraph = doc.add_paragraph(style="Title")
    title_paragraph.paragraph_format.space_after = Pt(2)
    title_paragraph.add_run(title)
    subtitle_paragraph = doc.add_paragraph(subtitle)
    subtitle_paragraph.paragraph_format.space_after = Pt(7)
    subtitle_paragraph.runs[0].italic = True
    subtitle_paragraph.runs[0].font.color.rgb = RGBColor(82, 101, 119)


def add_page_break(doc):
    doc.add_page_break()


def configure(doc):
    section = doc.sections[0]
    section.page_width = Inches(8.5)
    section.page_height = Inches(11)
    section.top_margin = Inches(0.48)
    section.bottom_margin = Inches(0.48)
    section.left_margin = Inches(0.58)
    section.right_margin = Inches(0.58)
    normal = doc.styles["Normal"]
    normal.font.name = "Arial"
    normal.font.size = Pt(9.6)
    normal.font.color.rgb = RGBColor(0, 0, 0)
    for name, size in (("Title", 22), ("Heading 1", 14), ("Heading 2", 11.5)):
        style = doc.styles[name]
        style.font.name = "Arial"
        style.font.size = Pt(size)
        style.font.bold = True
        style.font.color.rgb = RGBColor(0, 0, 0)
        if name == "Title":
            properties = style.element.get_or_add_pPr()
            borders = properties.find(qn("w:pBdr"))
            if borders is not None:
                properties.remove(borders)
    footer = section.footer.paragraphs[0]
    footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
    footer.add_run("COMP4145 PD2 Stock Trading Analytics Platform")
    footer.runs[0].font.name = "Arial"
    footer.runs[0].font.size = Pt(8)
    footer.runs[0].font.color.rgb = RGBColor(82, 101, 119)
    doc.core_properties.title = "COMP4145 PD2 Final Project Report"
    doc.core_properties.subject = "Stock Trading Analytics Platform"
    doc.core_properties.author = ""


def build():
    doc = Document()
    configure(doc)

    page_title(doc, "Stock Trading Analytics Platform", "COMP4145 Project Development 2 Final Report | Revised 4 November 2026")
    paragraph(doc, "The project extended the working Lab 2 application through two one-week sprints. Management priorities were to preserve proven functionality, deliver useful comparison and risk features early, and contain the higher uncertainty of portfolio backtesting through a feasibility gate and a constrained MVP. Three PD2 features are delivered; remote deployment remains incomplete.")
    heading(doc, "Requirements and Success Boundaries", 1)
    add_table(doc, ["Requirement", "Success boundary", "Evidence gate"], [
        ["Preserve Lab 2", "Keep the MSFT strategy, charts, statistics and trade records working", "Legacy calculation and UI regressions"],
        ["Week 1 decision support", "Compare 2-5 stocks and explain return, volatility and drawdown", "Known-value tests, live data and usable error states"],
        ["Week 2 portfolio MVP", "Model capital, positions, costs and causal crossover fills across 3-5 stocks", "Accounting invariants and deterministic fixtures"],
        ["Management and release", "Maintain risk/issue evidence, a clean install and a verified public deployment", "Actual records and public URL; no assumed completion"],
    ], [2.0, 3.1, 2.15])
    heading(doc, "Feature Prioritization", 1)
    add_table(doc, ["Feature and assigned owner", "Why it was sequenced this way", "Scope decision"], [
        ["Comparison M2 and Risk M3", "Both reused the existing provider and chart stack, delivered visible user value, and exposed data-quality assumptions early", "Complete basic Week 1 MVPs before the hard engine"],
        ["Portfolio Backtesting M4", "Moving-average signals alone did not solve execution timing, concurrent positions, cash limits, costs or unequal calendars", "Week 1 feasibility only; Week 2 equal-sleeve MVP with validation"],
        ["Integration and Cloud M5", "Deployment depended on stable features, clean dependencies, Git availability, authorization and public verification", "Test locally first; never claim cloud completion without a live URL"],
    ], [2.0, 3.4, 1.85])
    heading(doc, "Initial Risk Mitigation Strategy", 1)
    add_table(doc, ["Planned risk", "Initial response", "Management purpose"], [
        ["R01-R03 market data and calculations", "Cache requests, isolate errors, reject invalid prices, define units and use known-result tests", "Prevent plausible-looking but unsupported analytics"],
        ["R04 and R09 portfolio complexity and bias", "Separate feasibility from implementation; require delayed execution, a cash ledger and invariants", "Avoid look-ahead and return aggregation errors"],
        ["R05 time and scope", "Prioritize two easy MVPs; defer optional analytics and rebalancing", "Protect required delivery and testing depth"],
        ["R06 regression", "Preserve the original strategy and keep legacy tests in every integration run", "Avoid trading new scope for broken Lab 2 behavior"],
        ["R07 deployment", "Pin runtime packages, test a clean environment and require authorization plus a public smoke test", "Separate local readiness from external release"],
    ], [2.25, 3.35, 1.65])
    paragraph(doc, "Assigned owners describe planned responsibility, not verified individual contribution. The coding-time log is blank, so compliance with the 180-minute limit and any team approval require confirmation.", bold_lead="Evidence boundary  ")

    add_page_break(doc)
    page_title(doc, "Sprint Execution and Monitoring", "Project challenges were managed through scope gates, evidence checks and explicit incomplete status")
    doc.add_picture(str(ASSETS / "scrum_progress_comparison.png"), width=Inches(7.2))
    heading(doc, "Problem Impact Decision Outcome", 1)
    add_table(doc, ["Problem or challenge", "Impact and available options", "Decision", "Outcome"], [
        ["Portfolio accounting and execution were more complex than reusing the Lab 2 trade list", "Averaging independent trades could misstate portfolio return and same-close fills could introduce look-ahead. Options were reuse, a shared ledger, or independent sleeves.", "Build a separate equal-sleeve ledger; signal at Close t, execute next observed Close, mark open positions, and defer rebalancing.", "Eight deterministic engine tests and runtime invariants passed. Advanced execution and rebalancing remain outside scope by design."],
        ["Yahoo data reliability was an identified external risk; no production outage occurred", "Unequal calendars, invalid symbols, revisions and deprecation warnings could distort results or crash the UI. Filling gaps would create unsupported data.", "Use adjusted Close explicitly, strict validation, caching/error isolation, common dates for comparison and native sessions for risk/signals.", "Live calls and failure-handling tests passed. Provider availability, revisions and warnings remain residual risks."],
        ["Git commands actually failed because Apple Command Line Tools were unavailable", "Current Git status and a new commit baseline could not be obtained. Options were toolchain repair, pause work, or preserve a separate archive.", "Create a checksum-verified Week 1 archive, avoid reset/checkout, continue locally, and disclose the limitation.", "No files were discarded and testing continued. Git-based staging and remote release remain unresolved."],
        ["Cloud release depended on explicit authorization, working Git and public verification", "T13 could not meet its acceptance gate without external access. Options were an unauthorized release or local readiness with pending status.", "Complete clean installation, tests, secret scan, health and browser checks; keep T13 Blocked until authorized.", "Local deployment preparation passed. No public URL or cloud result is claimed."],
        ["Required quality competed with optional portfolio breadth; actual time evidence was unavailable", "Adding optimization, rebalancing or realistic execution would increase orders, costs and validation effort. A timeline delay cannot be claimed without records.", "Deliver easy features first, use a feasibility gate, constrain the portfolio MVP, and retain the full legacy regression suite.", "All required application features passed 23 tests. Optional breadth was deferred and time compliance remains unverified."],
    ], [1.55, 2.05, 1.9, 1.75])
    paragraph(doc, "The Scrum snapshots are unchanged. Risks are not presented as incidents: R01 did not become an outage, while R04 shaped the design and the Git failure became an actual issue.")

    add_page_break(doc)
    page_title(doc, "Final Project Update", "Planned scope is compared with delivered evidence and remaining boundaries")
    heading(doc, "Planned and Delivered", 1)
    add_table(doc, ["Area", "Planned", "Delivered and verified", "Status"], [
        ["Lab 2 baseline", "Preserve the existing single-stock workflow", "Strategy, chart, statistics, records and CSV retained in regression tests", "Done"],
        ["Comparison", "Week 1 easy MVP for 2-5 stocks", "Adjusted prices, common-date normalization, ranking, cache and errors", "Done"],
        ["Risk dashboard", "Week 1 basic risk MVP", "Return, sample volatility, drawdown, charts and coverage", "Done"],
        ["Portfolio", "Week 1 feasibility then Week 2 equal-weight MVP", "Equal sleeves, delayed crossover fills, cash/cost accounting, benchmark, contributions and trades", "Done"],
        ["Integration", "Validate all features together", "23 tests, clean installation, live data, desktop/mobile browser and health checks", "Done"],
        ["Cloud release", "Authorized Streamlit deployment and verified public URL", "Local readiness only; Git/authorization/public verification unavailable", "Blocked"],
    ], [1.1, 1.85, 3.55, 0.75])
    heading(doc, "Portfolio MVP Boundary", 1)
    add_table(doc, ["Category", "Evidence-supported conclusion"], [
        ["Working MVP", "Three to five stocks, equal initial sleeves, idle sleeve cash, fractional shares, configurable MAs/costs, equity curve, benchmark, contributions and trade history"],
        ["Validated functionality", "No-signal, buy/sell cycle, multiple stocks, missing sessions, costs, allocation, look-ahead, drawdown and open-position cases passed"],
        ["Technical assumptions", "Adjusted Close, next observed Close execution, union valuation calendar, last-price valuation only, terminal marking and 252-session annualization"],
        ["Intentional exclusions", "Automatic rebalancing, optimization, short selling, leverage and real-time/broker execution were outside the approved MVP, not failed requirements"],
        ["Remaining limitations", "No spread, slippage, taxes, whole-share constraint, cash dividends, FX conversion or delisted-symbol dataset; provider history can change"],
    ], [1.65, 5.6])
    heading(doc, "Verified Results", 1)
    bullets(doc, [
        "23 automated tests passed in the working and clean Python 3.13 environments; compilation and dependency checks also passed.",
        "Live AAPL, MSFT and NVDA backtesting reconciled equity to sleeve values; live numbers are smoke evidence, while deterministic fixtures support correctness.",
        "Desktop and 390-pixel browser checks covered the original and portfolio workflows without document-level horizontal overflow.",
    ])
    paragraph(doc, "Public application URL  Pending authorization and Streamlit Community Cloud verification", bold_lead="True deployment status  ")

    add_page_break(doc)
    page_title(doc, "Evaluation and Reflection", "The main lessons concern planning, risk, scope, evidence and unresolved external dependencies")
    heading(doc, "Project Management Evaluation", 1)
    add_table(doc, ["Area", "Evaluation and lesson"], [
        ["Planning effectiveness", "Sequencing two lower-risk features before the hard feature created early evidence and kept feasibility as an explicit gate before implementation. Future plans should make external release prerequisites explicit at sprint start."],
        ["Risk management", "Known-value tests and strict data policies reduced calculation risk. Risk records were most useful when they drove design choices; they should not be reported as failures when no incident occurred."],
        ["Scope management", "The equal-sleeve MVP met the user story without automatic rebalancing or optimization. Clear Must/Should/Future boundaries prevented optional breadth from weakening accounting validation."],
        ["Quality versus delivery", "The project chose legacy regression coverage, causal fills and clean-environment testing over additional features. This produced stronger evidence, although it did not resolve Git or cloud dependencies."],
        ["Monitoring evidence", "Three board checkpoints show actual status, but the blank time log prevents conclusions about effort, delay or compliance with the 180-minute rule."],
    ], [1.7, 5.55])
    heading(doc, "Problems Not Fully Resolved", 1)
    add_table(doc, ["Open item", "Current effect", "Next action"], [
        ["Git toolchain", "Current Git status, staging and remote workflow remain unavailable", "Repair Apple Command Line Tools, then review intended changes before staging"],
        ["Cloud deployment", "T13 remains Blocked and no public URL exists", "Obtain authorization, push, deploy and repeat live smoke tests"],
        ["Provider dependency", "Yahoo availability/revisions and pandas deprecation warnings remain external exposure", "Monitor provider compatibility and rerun regression tests before upgrades"],
        ["Team evidence", "No verified coding time, individual contribution record or team sign-off", "Five members must confirm actual records; do not infer them from software artifacts"],
    ], [1.55, 3.15, 2.55])
    heading(doc, "Brief Vibe Coding Reflection", 1)
    paragraph(doc, "AI assistance accelerated drafting, implementation and test construction, but it did not decide which financial assumptions were acceptable or prove that outputs were correct. Human oversight remained necessary to define scope, reject look-ahead, calculate independent expected results, inspect the interface and report incomplete work honestly. Future projects should treat AI output as work requiring review, not as a substitute for governance.")
    heading(doc, "Claims Requiring Team Confirmation", 1)
    bullets(doc, [
        "Actual coding time and compliance with the 180-minute course limit.",
        "Individual contributions, team discussions, stakeholder approval and final sign-off.",
        "Authorization to push/deploy and the final verified public application URL.",
    ])
    paragraph(doc, "Whole-share execution, slippage/spread models, cash dividends, FX conversion, delisted-symbol data, rebalancing and cloud monitoring are proposed future improvements, not delivered outcomes.", bold_lead="Proposed improvements  ")

    doc.save(OUTPUT)
    print(OUTPUT)


if __name__ == "__main__":
    build()
