"""
build_dashboard.py
----------------
Combines dashboard_template.html + dashboard_app.js + outputs/dashboard_data.json
into a single self-contained outputs/dashboard.html (no separate files needed -
works by just double-clicking it, no server, no internet required except for
the two CDN font/Plotly links).
"""

import json

with open("dashboard_template.html") as f:
    html = f.read()
with open("dashboard_app.js") as f:
    js = f.read()
with open("outputs/dashboard_data.json") as f:
    data = json.load(f)

data_json = json.dumps(data, separators=(",", ":"))

html = html.replace("/*__DASHBOARD_DATA__*/", data_json)
html = html.replace(
    '<script src="dashboard_app.js"></script>',
    f"<script>\n{js}\n</script>"
)

with open("outputs/dashboard.html", "w") as f:
    f.write(html)

print(f"Wrote outputs/dashboard.html ({len(html)} bytes)")
