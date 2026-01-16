
import os
import sys

# Add project root to path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from docnexus.plugins.pdf_export.plugin import export_pdf

# 1. Create HTML with Footnotes (simulating PyMdown output)
# Note: Python Markdown standard footnote output uses &#8617; (↩)
html_content = """
<html>
<body>
    <div id="documentContent" class="markdown-content">
        <p>Here is a footnote reference<sup id="fnref:1"><a class="footnote-ref" href="#fn:1">1</a></sup>.</p>
        
        <div class="footnote">
            <hr>
            <ol>
                <li id="fn:1">
                    <p>This is the footnote content. <a class="footnote-backref" href="#fnref:1" title="Jump back to footnote 1 in the text">&#8617;</a></p>
                </li>
            </ol>
        </div>
    </div>
</body>
</html>
"""

print("Generating PDF with Footnote...")
try:
    pdf_bytes = export_pdf(html_content)
    output_file = os.path.join(current_dir, "repro_footnote.pdf")
    with open(output_file, "wb") as f:
        f.write(pdf_bytes)
    print(f"SUCCESS: Generated {output_file}")
except Exception as e:
    print(f"FAILURE: {e}")
    import traceback
    traceback.print_exc()
