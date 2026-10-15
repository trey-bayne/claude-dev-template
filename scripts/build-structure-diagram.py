import html, xml.etree.ElementTree as ET

CELLS, _id = [], [10]
def nid():
    _id[0] += 1
    return f"n{_id[0]}"

def box(x, y, w, h, label, style, sub=None):
    i = nid()
    if sub:
        lab = (f'<b>{html.escape(label)}</b>'
               f'<div style="font-size:9px;color:#555555;margin-top:1px">{html.escape(sub)}</div>')
    else:
        lab = f'<b>{html.escape(label)}</b>'
    CELLS.append(
        f'        <mxCell id="{i}" value="{html.escape(lab)}" style="{style}" vertex="1" parent="1">\n'
        f'          <mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" as="geometry" />\n'
        f'        </mxCell>')
    return i

def text(x, y, w, h, label, size=12, bold=False, color="#333333", align="left"):
    i = nid()
    st = (f"text;html=1;strokeColor=none;fillColor=none;align={align};verticalAlign=middle;"
          f"whiteSpace=wrap;fontSize={size};fontColor={color};"
          f"fontStyle={'1' if bold else '0'}")
    CELLS.append(
        f'        <mxCell id="{i}" value="{html.escape(label)}" style="{st}" vertex="1" parent="1">\n'
        f'          <mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" as="geometry" />\n'
        f'        </mxCell>')
    return i

ITEM  = ("rounded=0;whiteSpace=wrap;html=1;align=left;spacingLeft=10;verticalAlign=middle;"
         "fontSize=11;fillColor={f};strokeColor={s};")
DIR   = ("rounded=0;whiteSpace=wrap;html=1;align=left;verticalAlign=top;spacingLeft=10;spacingTop=6;"
         "fontSize=12;fontStyle=1;fillColor=#FAFAFA;strokeColor=#9E9E9E;dashed=1;")
T0 = {"f": "#FFF2CC", "s": "#D6B656"}   # tier 0 — before anything
T1 = {"f": "#DAE8FC", "s": "#6C8EBF"}   # tier 1 — every session
T2 = {"f": "#D5E8D4", "s": "#82B366"}   # tier 2 — on demand
T3 = {"f": "#E1D5E7", "s": "#9673A6"}   # tier 3 — rarely
CFG = {"f": "#F5F5F5", "s": "#9E9E9E"}  # config / tooling
CMD = {"f": "#FFFFFF", "s": "#9E9E9E"}  # slash commands

def item(x, y, w, label, sub, pal, dashed=False):
    st = ITEM.format(**pal) + ("dashed=1;" if dashed else "")
    return box(x, y, w, 32, label, st, sub)

# ───────────────────────── title ─────────────────────────
text(40, 18, 1020, 24, "Project structure created by claude-dev-template", 17, True, "#000000")
text(40, 44, 1020, 18,
     "Solid boxes: everything the bootstrap creates — verified against a real project at this stage. "
     "Dashed red: what appears later. Colour = context tier, i.e. when Claude Code loads the file.", 11, False, "#555555")

# ───────────────────── left: project root ─────────────────────
box(40, 84, 390, 328, "project/", DIR)
ROOT = [
    ("CLAUDE.md",        "Tier 1 — read every session. Hard limit: 200 lines", T1),
    ("TASKS.md",         "Tier 1 — build tracker. Resume Here + Phase Index",  T1),
    ("PROJECT_BRIEF.md", "Tier 3 — full design doc, read only when scope is in question", T3),
    ("PERMISSIONS.md",   "Rationale for every allow/deny rule in settings.json", CFG),
    (".env.example",     "Key list only, always committed. .env never is",      CFG),
    (".gitignore",        "From gitignore.template. Must NOT ignore CLAUDE.md / TASKS.md", CFG),
    (".git/",            "Created by git init in Step 7, on the dev branch", CFG),
]
y = 116
for name, sub, pal in ROOT:
    item(58, y, 354, name, sub, pal)
    y += 42

# ───────────────────── left: docs/ ─────────────────────
box(40, 434, 390, 328, "docs/     Tier 2 — loaded on demand, never preloaded", DIR)
DOCS = [
    ("INDEX.md",        "Navigation map: 'I need X -> read Y'. Entry point for Tier 2"),
    ("QUICK_REF.md",    "One-page command cheat sheet for this stack"),
    ("ARCHITECTURE.md", "Data flows, service map, ownership model"),
    ("PHASE_NOTES.md",  "Per-phase goal + Definition of Done. /phase-test's spec"),
    ("DECISIONS.md",    "Tech choices and why. 'Do not relitigate'"),
    ("ENV_VARS.md",     "Full variable reference with descriptions"),
    ("SYSTEM_STATE.md", "Post-build: patterns that became the standard"),
]
y = 466
for name, sub in DOCS:
    item(58, y, 354, name, sub, T2)
    y += 42

# ───────────────────── right: .claude/ ─────────────────────
box(456, 84, 604, 636, ".claude/", DIR)
item(474, 116, 568, "settings.json",
     "Permission allow/deny lists + the hooks block that registers the hook below", CFG)

box(474, 166, 568, 84, "hooks/", DIR)
item(492, 198, 532, "session-start.sh",
     "Tier 0 — runs before CLAUDE.md. Inert unless registered in settings.json", T0)

box(474, 266, 568, 436, "commands/     16 slash commands", DIR)
CMDS = [
    ("checkpoint.md",      "snapshot before risky work",   False),
    ("status.md",          "where am I, what's healthy",   False),
    ("phase-review.md",    "Opus scores the next phase",   False),
    ("phase-run.md",       "execute the phase",            False),
    ("phase-test.md",      "verify against the DoD",       False),
    ("phase-complete.md",  "close out, commit, push",      False),
    ("phase-auto.md",      "the whole cycle, unattended",  False),
    ("codebase-review.md", "parallel multi-domain audit",  False),
    ("sync-issues.md",     "GitHub issues -> TASKS.md",    False),
    ("prj-manage.md",      "image + dependency age",       False),
    ("prj-drift.md",       "drift vs the template",        False),
    ("prj-convert.md",     "adopt an existing project",    False),
    ("dev-build.md",       "build + test on dev",          True),
    ("ship.md",            "promote dev -> stable",        True),
    ("phase-release.md",   "tagged release",               True),
    ("phase-rollback.md",  "revert to previous tag",       True),
]
col_w, col_x = 272, (492, 776)
for n, (name, sub, two) in enumerate(CMDS):
    cx = col_x[n // 8]
    cy = 300 + (n % 8) * 48
    item(cx, cy, col_w, name, sub, CMD, dashed=two)
text(492, 668, 540, 26,
     "Dashed = installed only when the project uses the two-branch promotion workflow. "
     "A single-branch project omits these four.", 9, False, "#666666")

# ──────────── what the bootstrap does NOT create ────────────
LATER_STYLE = ("rounded=0;whiteSpace=wrap;html=1;align=left;spacingLeft=10;verticalAlign=middle;"
               "fontSize=11;fillColor=#FFFFFF;strokeColor=#B85450;dashed=1;dashPattern=1 2;")
box(40, 786, 1020, 196,
    "Everything above is all the bootstrap creates. These appear later — do not expect them "
    "in a freshly bootstrapped project:", DIR)
LATER = [
    (".env",                     "You create it from .env.example. Never committed"),
    (".claude/settings.local.json", "Claude Code writes this itself for local permission choices"),
    ("docker-compose.yml",       "NOT generated by the bootstrap — Phase 1 builds it"),
    ("source directories",       "services/ src/ app/ — whatever the phases build"),
    ("scripts/",                 "Rebuild and deploy helpers the promotion commands call"),
    ("config/ , logs/",          "Runtime state produced by the stack, usually gitignored"),
]
for n, (name, sub) in enumerate(LATER):
    i = nid()
    cx = 58 + (n % 3) * 336
    cy = 834 + (n // 3) * 46
    lab = (f'<b>{name}</b><div style="font-size:9px;color:#555555;margin-top:1px">{sub}</div>')
    import html as _h
    CELLS.append(
        f'        <mxCell id="{i}" value="{_h.escape(lab)}" style="{LATER_STYLE}" vertex="1" parent="1">\n'
        f'          <mxGeometry x="{cx}" y="{cy}" width="320" height="32" as="geometry" />\n'
        f'        </mxCell>')
text(58, 930, 990, 40,
     "Worth knowing: eight commands assume a Docker Compose stack (/status, /phase-complete, "
     "/phase-review, /phase-test, /codebase-review, /prj-manage, /phase-release, /phase-rollback) "
     "but the bootstrap never writes a compose file. Phase 1 has to, or those commands have "
     "nothing to talk to.", 9, False, "#B85450")

# ───────────────────── legend ─────────────────────
box(40, 1006, 1020, 108, "Context tiers — the reason for the split", DIR)
LEG = [
    ("Tier 0", "session-start.sh — fires before anything else", T0),
    ("Tier 1", "CLAUDE.md, TASKS.md — every session, always",   T1),
    ("Tier 2", "docs/* — pulled only when relevant",            T2),
    ("Tier 3", "PROJECT_BRIEF.md — rarely",                     T3),
    ("Config", "settings.json, PERMISSIONS.md, .env.example",    CFG),
]
for n, (name, sub, pal) in enumerate(LEG):
    item(58 + (n % 3) * 336, 1040 + (n // 3) * 40, 320, name, sub, pal)

text(40, 1124, 1020, 30,
     "Every line in a Tier 1 file is loaded at the start of every session, so phase detail, "
     "env var tables and architecture diagrams belong in docs/ instead. That is the whole point "
     "of the structure: keep the always-loaded context small and relevant.", 10, False, "#555555")

xml = ('<mxfile host="app.diagrams.net" type="device" version="24.7.17">\n'
       '  <diagram id="claude-dev-template-structure" name="Project structure">\n'
       '    <mxGraphModel dx="1422" dy="800" grid="1" gridSize="10" guides="1" tooltips="1"'
       ' connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="1100" pageHeight="1180"'
       ' math="0" shadow="0">\n'
       '      <root>\n'
       '        <mxCell id="0" />\n'
       '        <mxCell id="1" parent="0" />\n'
       + "\n".join(CELLS) + "\n"
       '      </root>\n'
       '    </mxGraphModel>\n'
       '  </diagram>\n'
       '</mxfile>\n')

out = "/home/trey/prj/claude_dev/docs/folder-structure.drawio"
open(out, "w").write(xml)
ET.parse(out)   # fails loudly if the XML is malformed
print("wrote", out)
print("cells:", len(CELLS), " bytes:", len(xml))
