import os

assets_dir = 'c:\\Users\\amita\\myprojects\\searcher_browser\\assets\\icons'
os.makedirs(assets_dir, exist_ok=True)

icons = {
    'star': '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"></polygon></svg>',
    'ai': '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2L15 8L21 11L15 14L12 20L9 14L3 11L9 8L12 2Z"></path></svg>'
}

colors = {'light': '#e8eaed', 'dark': '#202124'}

for name, svg_template in icons.items():
    for theme, color in colors.items():
        filename = f'{name}_white.svg' if theme == 'light' else f'{name}_black.svg'
        filepath = os.path.join(assets_dir, filename)
        with open(filepath, 'w') as f:
            f.write(svg_template.replace('{color}', color))
print('Created SVG icons successfully.')
