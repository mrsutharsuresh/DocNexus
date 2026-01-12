import os
import sys
from pathlib import Path

PLUGIN_DIR = Path(__file__).parent
ENABLED_FILE = PLUGIN_DIR / "ENABLED"
DEPENDENCIES = ["xhtml2pdf"]

import io

def export_pdf(content_html: str) -> bytes:
    """
    Export content to PDF using xhtml2pdf.
    Returns bytes.
    """
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        from xhtml2pdf import pisa
        from bs4 import BeautifulSoup
        import re
        # Prepare content with robust CSS handling
        # xhtml2pdf crashes on CSS variables (var(--...)).
        # We must:
        # 1. Inline external stylesheets
        # 2. Sanitize all 'var(--...)' usages in both HTML styles and inlined CSS
        
        import re
        
        # Regex to find CSS variable usage: var(--name, fallback) or var(--name)
        # We replace with a safe color (black/gray) to prevent crash
        css_var_pattern = re.compile(r'var\s*\([^)]+\)')
        
        def sanitize_css(text):
            # Replace common specific vars with reasonable values
            replacements = {
                'var(--color-fg-default)': '#000000',
                'var(--color-canvas-default)': '#ffffff',
                'var(--color-border-default)': '#cccccc',
                'var(--color-accent-fg)': '#0969da',
                'var(--color-neutral-muted)': '#afb8c1',
            }
            for k, v in replacements.items():
                text = text.replace(k, v)
            
            # Nuke remaining vars to generic gray to prevent crash
            return css_var_pattern.sub('#888888', text)

        # 0. Clean & Restructure HTML using BeautifulSoup
        try:
            soup = BeautifulSoup(content_html, 'html.parser')

            # Identify Key Content Areas
            # Target the Main Document Container (includes Title, Metadata, Server-Side TOC, Content)
            # This respects the "On-Page" structure the user sees, excluding Navbar/Sidebar.
            main_container = soup.find(id='documentContent')
            
            if not main_container:
                # Fallback for pages that might not have the ID
                main_container = soup.find(class_='markdown-content')
            
            if main_container:
                # 1. Remove Header Permalinks (Double Square Artifacts)
                # These are usually <a class="headerlink">¶</a>
                for permalink in main_container.find_all('a', class_='headerlink'):
                    permalink.decompose()

                # 2. Fix Internal Links (TOC & Anchors)
                # xhtml2pdf often needs <a name="id"></a> for internal linking to work reliably.
                # Find all elements with an ID and inject a named anchor.
                for element in main_container.find_all(id=True):
                    anchor_name = element['id']
                    # Create a new anchor tag
                    new_anchor = soup.new_tag('a')
                    new_anchor['name'] = anchor_name
                    # Insert *inside* the element at the beginning, or before it.
                    # Putting it inside is usually safer for keeping context.
                    element.insert(0, new_anchor)

                # 3. Handle Emojis (Square Artifacts)
                # Strip wide unicode characters (likely emojis) that xhtml2pdf default fonts can't render.
                # This prevents the "tofu" boxes.
                def remove_emojis(text):
                    if not text: return text
                    # Regex to match emojis / symbols outside basic multilingual plane
                    return re.sub(r'[^\x00-\x7F\x80-\xFF\u0100-\u017F\u0180-\u024F\u1E00-\u1EFF]', '', text)

                # Recursively clean text nodes
                for text_node in main_container.find_all(string=True):
                    if text_node.parent.name not in ['script', 'style']: # formatting tags are fine
                        cleaned_text = remove_emojis(text_node)
                        if cleaned_text != text_node:
                            text_node.replace_with(cleaned_text)

                # 4. Handle Mermaid Diagrams
                # Handled Client-Side: The frontend now rasterizes SVG -> PNG Data URI before sending HTML.
                # This ensures WYSIWYG results and offline support. 
                # We just leave this here as a placeholder in case any un-processed blocks remain (rendered as text).
                pass


                # Create a fresh clean DOM
                new_soup = BeautifulSoup('<html><body></body></html>', 'html.parser')
                body = new_soup.body
                
                # Append the main container
                body.append(main_container)
                
                # Remove any screen-only elements that might be inside
                for garbage in body.find_all(['script', 'button', 'nav']): 
                    garbage.decompose()

                # Update content to be just this clean structure
                content_html = str(new_soup)
            else:
                 logger.warning("PDFExport: Could not find #documentContent or .markdown-content")

        except Exception as e:
            logger.error(f"PDFExport: preprocessing failed: {e}")
            pass

        # "SAFE MODE": Strip all external stylesheets to prevent xhtml2pdf crash on modern CSS
        # We replace them with a robust internal stylesheet optimized for print.
        
        # 1. Remove all <link rel="stylesheet"> tags
        link_pattern = re.compile(r'<link[^>]+rel=["\']stylesheet["\'][^>]*>', re.IGNORECASE)
        full_html = link_pattern.sub('', content_html)
        
        # 2. Remove all <style>...</style> blocks (Nuclear option)
        # Use DOTALL to match newlines inside style tags
        style_block_pattern = re.compile(r'<style\b[^>]*>.*?</style>', re.IGNORECASE | re.DOTALL)
        full_html = style_block_pattern.sub('', full_html)
        
        # 3. Remove all style="..." attributes (Nuclear option)
        # This removes inline styles that might contain vars
        # We match style=" anything except quote "
        # Hacky regex but sufficient for standard HTML
        style_attr_pattern = re.compile(r'\sstyle=["\'][^"\']*["\']', re.IGNORECASE)
        full_html = style_attr_pattern.sub('', full_html)
        
        # 4. Add Safe Internal Stylesheet
        # This provides a clean, professional look without relying on the web UI's complex CSS
            
        # 3. Add Print Override Styles
        full_html = f"""
        <html>
        <head>
            {full_html}
            <style>
                @page {{
                    size: A4;
                    margin: 2cm;
                }}
                body {{
                    font-family: Helvetica, Arial, sans-serif;
                    font-size: 10pt;
                    color: #000000;
                    background-color: #ffffff;
                }}
                /* Force simplified styling for PDF */
                .markdown-body {{ font-family: Helvetica, Arial, sans-serif !important; color: black !important; background: white !important; }}
                h1, h2, h3, h4, h5, h6 {{ color: #333 !important; page-break-after: avoid; }}
                h1 {{ border-bottom: 2px solid #333; padding-bottom: 5px; }}
                code, pre {{ font-family: Courier; background: #f5f5f5; border: 1px solid #eee; }}
                table {{ border-collapse: collapse; width: 100%; margin-top: 10px; }}
                td, th {{ border: 1px solid #ccc; padding: 6px; text-align: left; }}
                th {{ background-color: #f3f4f6; font-weight: bold; }}

                /* Document Header Styling (Title & Metadata) */
                .document-header {{ margin-bottom: 20px; border-bottom: 1px solid #ccc; padding-bottom: 10px; }}
                .document-title {{ font-size: 24pt; font-weight: bold; margin: 0 0 10px 0; border: none !important; }}
                .document-path {{ color: #666; font-size: 9pt; font-style: italic; }}

                /* TOC Styling (Professional Print) */
                .toc-container {{
                    background-color: transparent;
                    border: none;
                    padding: 0;
                    margin-bottom: 40px;
                    page-break-after: always;
                }}
                .toc-header {{
                    font-size: 14pt;
                    font-weight: bold;
                    text-transform: uppercase;
                    letter-spacing: 2px;
                    margin-bottom: 20px;
                    border-bottom: 3px solid #000;
                    padding-bottom: 10px;
                    color: #000;
                }}
                .toc-content ul {{ list-style-type: none; padding-left: 0; }}
                .toc-content li {{ margin-bottom: 8px; }}
                
                /* Top Level Items */
                .toc-content > ul > li > a {{
                    font-weight: bold;
                    font-size: 11pt;
                    color: #000;
                }}
                
                /* Nested Items */
                .toc-content ul ul {{ 
                    padding-left: 20px; 
                    margin-top: 4px;
                }}
                .toc-content ul ul li a {{
                    font-weight: normal;
                    font-size: 10pt;
                    color: #444;
                }}
                
                .toc-content a {{ text-decoration: none; }}
            </style>
        </head>
        <body>
        """
        
        # Convert to PDF in memory
        result = io.BytesIO()
        
        pisa_status = pisa.CreatePDF(
            full_html,              # the HTML to convert
            dest=result             # file handle to recieve result
        )
            
        if pisa_status.err:
            raise RuntimeError(f"PDF generation error: {pisa_status.err}")
            
        logger.info(f"PDFExport: Generated {result.getbuffer().nbytes} bytes.")
        return result.getvalue()
        
    except ImportError as ie:
        import traceback
        import sys
        
        # Capture full context
        tb = traceback.format_exc()
        
        # Try to find what exactly failed
        error_msg = f"xhtml2pdf import failed. Cause: {ie}. Path: {sys.path}"
        print(f"DEBUG_IMPORT_FAIL: {error_msg}")
        print(tb) # Print to console/log
        
        raise RuntimeError(f"xhtml2pdf library is missing/broken. Detail: {ie}")
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise RuntimeError(f"PDF Export Failed: {e}")

def get_features():
    from docnexus.features.registry import Feature, FeatureType, FeatureState
    from docnexus.core.state import PluginState
    
    # Check "Enabled" status via Config
    is_enabled = "pdf_export" in PluginState.get_instance().get_installed_plugins()
    
    features = []
    
    # We register the feature but mark it as installed/not installed
    features.append(
        Feature(
            "pdf_export",
            feature_type=FeatureType.EXPORT_HANDLER,
            handler=export_pdf,
            state=FeatureState.EXPERIMENTAL,
            meta={
                "extension": "pdf",
                "label": "PDF Document (.pdf)",
                "installed": is_enabled,
                "description": "Generates professional PDF documents from your markdown.",
                "version": "1.0.0"
            }
        )
    )
    
    return features

# Metadata
PLUGIN_METADATA = {
    'name': 'PDF Export',
    'description': 'Converts documentation to professional PDF format with Table of Contents, cover page, and optimized print layout.',
    'category': 'export',
    'icon': 'fa-file-pdf',
    'preinstalled': False
}
