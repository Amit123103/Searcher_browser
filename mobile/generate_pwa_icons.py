"""
Generate PWA icons for the Searcher Browser mobile app.
Creates 192x192 and 512x512 PNG icons from the existing logo.
"""
import os
from PIL import Image

def generate_icons():
    # Paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    source_logo = os.path.join(script_dir, '..', 'assets', 'logo.png')
    icons_dir = os.path.join(script_dir, 'icons')
    
    # Create icons directory
    os.makedirs(icons_dir, exist_ok=True)
    
    if not os.path.exists(source_logo):
        print(f"Error: Source logo not found at {source_logo}")
        print("Creating placeholder icons instead...")
        create_placeholder_icons(icons_dir)
        return
    
    # Open and resize
    img = Image.open(source_logo)
    
    # Convert to RGBA if needed
    if img.mode != 'RGBA':
        img = img.convert('RGBA')
    
    # Generate sizes
    sizes = [192, 512]
    for size in sizes:
        resized = img.resize((size, size), Image.LANCZOS)
        output_path = os.path.join(icons_dir, f'icon-{size}.png')
        resized.save(output_path, 'PNG')
        print(f"Created: {output_path} ({size}x{size})")
    
    print("Done! PWA icons generated successfully.")


def create_placeholder_icons(icons_dir):
    """Create simple placeholder icons if the source logo is missing."""
    for size in [192, 512]:
        img = Image.new('RGBA', (size, size), (56, 189, 248, 255))
        
        # Draw a simple "S" shape using pixels (very basic)
        # Just create a solid colored circle as placeholder
        from PIL import ImageDraw
        draw = ImageDraw.Draw(img)
        margin = size // 8
        draw.ellipse([margin, margin, size - margin, size - margin], fill=(10, 14, 26, 255))
        
        # Inner circle
        inner_margin = size // 4
        draw.ellipse([inner_margin, inner_margin, size - inner_margin, size - inner_margin], fill=(56, 189, 248, 255))
        
        output_path = os.path.join(icons_dir, f'icon-{size}.png')
        img.save(output_path, 'PNG')
        print(f"Created placeholder: {output_path} ({size}x{size})")


if __name__ == '__main__':
    generate_icons()
