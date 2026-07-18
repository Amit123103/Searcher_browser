import os

assets_dir = 'c:\\Users\\amita\\myprojects\\searcher_browser\\assets\\icons'
os.makedirs(assets_dir, exist_ok=True)

icons = {
    'close': '<svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>',
}

colors = {'light': '#e8eaed', 'dark': '#202124'}

for name, svg_template in icons.items():
    for theme, color in colors.items():
        filename = f'{name}_white.svg' if theme == 'light' else f'{name}_black.svg'
        filepath = os.path.join(assets_dir, filename)
        with open(filepath, 'w') as f:
            f.write(svg_template.replace('{color}', color))
print('Created close SVG icons successfully.')
