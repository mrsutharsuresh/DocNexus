import sys
import os
import flask

# Monkeypatch Flask to default template_folder/static_folder to sys._MEIPASS/docnexus/...
_orig_init = flask.Flask.__init__

def _frozen_init(self, import_name, **kwargs):
    if getattr(sys, 'frozen', False):
        base_dir = sys._MEIPASS
        # Set defaults if not provided
        # We assume build moves docnexus/templates -> docnexus/templates relative to bundle ROOT
        # So in bundle: sys._MEIPASS/docnexus/templates
        
        # But wait! scripts/build.py adds:
        # "--add-data", f"{PROJECT_ROOT / 'docnexus' / 'templates'}{os.pathsep}docnexus/templates"
        # This usually puts it in sys._MEIPASS/docnexus/templates. 
        # Correct.
        
        template_dir = os.path.join(base_dir, 'docnexus', 'templates')
        static_dir = os.path.join(base_dir, 'docnexus', 'static')
        
        kwargs.setdefault('template_folder', template_dir)
        kwargs.setdefault('static_folder', static_dir)
        
        # Debug print to stdout (visible if console=True)
        print(f"[RunHook] Frozen mode detected.")
        print(f"[RunHook] Patching Flask template_folder: {template_dir}")
        print(f"[RunHook] Patching Flask static_folder: {static_dir}")
    
    _orig_init(self, import_name, **kwargs)

flask.Flask.__init__ = _frozen_init
