"""
Generate clean, professional SVG icons for Searcher Browser.
Uses precise Lucide/Feather-style paths with consistent stroke widths.
"""
import os

ICON_DIR = os.path.join(os.path.dirname(__file__), "assets", "icons")
os.makedirs(ICON_DIR, exist_ok=True)

# Icon definitions: name -> SVG path data
# All icons use 24x24 viewBox, stroke-based, no fill
ICONS = {
    "back": '<path d="M15 18l-6-6 6-6"/>',
    "forward": '<path d="M9 18l6-6-6-6"/>',
    "reload": '<path d="M1 4v6h6"/><path d="M3.51 15a9 9 0 1 0 2.13-9.36L1 10"/>',
    "home": '<path d="M3 9.5L12 3l9 6.5V20a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1V9.5z"/><path d="M9 21V12h6v9"/>',
    "lock": '<rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/>',
    "search": '<circle cx="11" cy="11" r="8"/><path d="M21 21l-4.35-4.35"/>',
    "ai": '<path d="M12 2L2 7l10 5 10-5-10-5z"/><path d="M2 17l10 5 10-5"/><path d="M2 12l10 5 10-5"/>',
    "mobile": '<rect x="5" y="2" width="14" height="20" rx="2" ry="2"/><path d="M12 18h.01"/>',
    "star": '<polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>',
    "star_active": '<polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>',
    "menu": '<line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="18" x2="21" y2="18"/>',
    "plus": '<line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/>',
    "close": '<line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>',
    "shield": '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>',
}

# Color variants
VARIANTS = {
    "white": "#CBD5E1",     # Soft slate for dark theme (not pure white)
    "black": "#475569",     # Slate for light theme
}

def make_svg(path_data, color, stroke_width="1.75", fill="none"):
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="{fill}" stroke="{color}" stroke-width="{stroke_width}" stroke-linecap="round" stroke-linejoin="round">{path_data}</svg>'

for icon_name, path_data in ICONS.items():
    for variant, color in VARIANTS.items():
        # star_active gets a filled variant
        if icon_name == "star_active":
            svg = make_svg(path_data, "#FBBF24", "1.75", "#FBBF24")
        else:
            svg = make_svg(path_data, color)
        
        filename = f"{icon_name}_{variant}.svg" if icon_name != "star_active" else "star_active.svg"
        filepath = os.path.join(ICON_DIR, filename)
        
        # Skip duplicate star_active for black variant
        if icon_name == "star_active" and variant == "black":
            continue
            
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(svg)
        print(f"  OK: {filename}")

print(f"\nDone! {len(os.listdir(ICON_DIR))} icons in {ICON_DIR}")
