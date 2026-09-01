# generator.py
import os
import sys
import random
import math
import logging
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPDF
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# --- LOGGING SETUP ---
def setup_logging():
    """Setup logging based on environment variable"""
    log_level = os.environ.get("MATH_WORKSHEET_LOG", "WARNING").upper()
    
    # Create logs directory
    log_dir = os.environ.get("MATH_WORKSHEET_LOG_DIR")
    if not log_dir:
        if getattr(sys, 'frozen', False):
            log_dir = os.path.dirname(sys.executable)
        else:
            log_dir = os.path.dirname(os.path.abspath(__file__))

    # Fallback to current directory if not writable
    if not os.access(log_dir, os.W_OK):
        log_dir = os.getcwd()

    log_file = os.path.join(log_dir, "math_worksheet.log")
  
    
    logging.basicConfig(
        level=getattr(logging, log_level, logging.WARNING),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

logger = setup_logging()

# --- PATH HANDLING (works for both normal and bundled execution) ---
def get_base_path():
    """Returns the base path whether running normally or as PyInstaller bundle."""
    if getattr(sys, 'frozen', False):
        # Running as PyInstaller bundle
        base_path = sys._MEIPASS
        logger.info(f"Running as PyInstaller bundle, MEIPASS: {base_path}")
    else:
        # Running normally
        base_path =  os.path.dirname(os.path.abspath(__file__))
        logger.info(f"Running normally, base path: {base_path}")
    return base_path

BASE_PATH = get_base_path()
ICONS_DIR = os.path.join(BASE_PATH, "icons")
FONTS_DIR = os.path.join(BASE_PATH, "fonts")

logger.info(f"ICONS_DIR: {ICONS_DIR}")
logger.info(f"FONTS_DIR: {FONTS_DIR}")
logger.info(f"ICONS_DIR exists: {os.path.exists(ICONS_DIR)}")
logger.info(f"FONTS_DIR exists: {os.path.exists(FONTS_DIR)}")

FONT_FILENAME = "DCH-Basisschrift.ttf"
FONT_PATH = os.path.join(FONTS_DIR, FONT_FILENAME)

logger.info(f"Looking for font at: {FONT_PATH}")
logger.info(f"Font file exists: {os.path.exists(FONT_PATH)}")

if os.path.exists(FONT_PATH):
    try:
        pdfmetrics.registerFont(TTFont("DCH-Basisschrift", FONT_PATH))
        CUSTOM_FONT = "DCH-Basisschrift"
        logger.info(f"✅ Successfully registered font: {CUSTOM_FONT}")
    except Exception as e:
        logger.error(f"❌ Failed to register font: {e}")
        CUSTOM_FONT = "Helvetica-Bold"
else:
    logger.warning(f"⚠️ Font not found at {FONT_PATH}, falling back to Helvetica-Bold")

    if os.path.exists(FONTS_DIR):
        logger.info(f"📂 Files actually inside {FONTS_DIR}: {os.listdir(FONTS_DIR)}")
    else:
        logger.warning(f"❌ FONTS_DIR does not exist at all!")
        
    CUSTOM_FONT = "Helvetica-Bold"
    

def draw_svg_image(c, svg_path, x, y, size=60, rotation=0):
    """Reads an SVG and draws it centered at (x, y) with optional rotation."""
    drawing = svg2rlg(svg_path)
    if drawing:
        sx = size / drawing.width
        sy = size / drawing.height
        drawing.width = size
        drawing.height = size
        drawing.scale(sx, sy)
        
        c.saveState()
        c.translate(x, y)
        c.rotate(rotation)
        renderPDF.draw(drawing, c, -size / 2, -size / 2)
        c.restoreState()

def draw_digit_text(c, x, y, number, rotation=0):
    """Fallback: draws the number as text."""
    c.saveState()
    c.translate(x, y)
    c.rotate(rotation)
    c.setFont(CUSTOM_FONT, 48)
    c.drawCentredString(0, -15, str(number))
    c.restoreState()

def draw_icon(c, x, y, number, set_name, rotation=0):
    """
    Draws an icon for the given number and set.
    - If set_name is 'digits', always uses text rendering
    - If set_name is 'hands' and 6 <= number <= 10, uses composite hands
    - Otherwise, tries to load SVG from icons/setname/setname_number.svg
    - Falls back to text if SVG doesn't exist or number is too large
    """
    # Special case: digits always use text
    if set_name == "digits":
        draw_digit_text(c, x, y, number, rotation)
        return
    
    # Special case: hands with 6 <= number <= 10 use composite
    if set_name == "hands" and 5 < number <= 10:
        draw_hands_composite(c, x, y, number, rotation)
        return
    
    # For all other sets, try to load SVG
    svg_path = os.path.join(ICONS_DIR, set_name, f"{set_name}_{number}.svg")
    
    if os.path.exists(svg_path):
        draw_svg_image(c, svg_path, x, y, size=60, rotation=rotation)
    else:
        # Icon doesn't exist for this number, use text fallback
        draw_digit_text(c, x, y, number, rotation)

def draw_hands_composite(c, x, y, number, rotation=0, size=60):
    """
    Draws hands for any number by composing multiple hand SVGs.
    For numbers > 5, breaks into chunks of 5 and remainder.
    Mirrors alternate hands to look like left/right hands.
    """
    full_hands = number // 5
    remainder = number % 5
    
    hands_to_draw = []
    for _ in range(full_hands):
        hands_to_draw.append(5)
    if remainder > 0:
        hands_to_draw.append(remainder)
    
    num_hands = len(hands_to_draw)
    spacing = size * 0.15  # 15% spacing between hands
    total_width = num_hands * size + (num_hands - 1) * spacing
    
    c.saveState()
    c.translate(x, y)
    c.rotate(rotation)
    
    start_x = -total_width / 2 + size / 2
    
    for i, hand_num in enumerate(hands_to_draw):
        svg_path = os.path.join(ICONS_DIR, "hands", f"hands_{hand_num}.svg")
        if os.path.exists(svg_path):
            drawing = svg2rlg(svg_path)
            if drawing:
                # Scale to fit
                sx = size / drawing.width
                sy = size / drawing.height
                drawing.width = size
                drawing.height = size
                drawing.scale(sx, sy)
                
                pos_x = start_x + i * (size + spacing)
                
                # Mirror alternate hands for left/right effect
                if i % 2 == 1:
                    c.saveState()
                    c.translate(pos_x, 0)
                    c.scale(-1, 1)  # Flip horizontally
                    renderPDF.draw(drawing, c, -size / 2, -size / 2)
                    c.restoreState()
                else:
                    renderPDF.draw(drawing, c, pos_x - size / 2, -size / 2)
    
    c.restoreState()

def generate_worksheet(min_range, max_range, count, icon_styles, icon_weights, icon_replacement_rate, filename="worksheet.pdf"):
    """
    Generate worksheet with random numbers from a specified range.
    
    :param min_range: Minimum number in the range (inclusive)
    :param max_range: Maximum number in the range (inclusive)
    :param count: How many numbers to randomly select from the range
    :param icon_styles: List of icon set names (e.g., ['dice', 'hands'])
    :param icon_weights: Relative weights for distributing among icon sets
    :param icon_replacement_rate: 0.0 to 1.0, percentage of numbers replaced by icons
    :param filename: Output PDF filename
    """
    c = canvas.Canvas(filename, pagesize=A4)
    width, height = A4
    
    c.setFont(CUSTOM_FONT, 16)
    c.drawString(2*cm, height - 2*cm, f"Zahlen Wettrennen Arbeitsblatt ({min_range} bis {max_range})")
    c.setFont(CUSTOM_FONT, 12)
    c.drawString(2*cm, height - 2.8*cm, "Name: ___________________________   Zeit: ______________")

    margin = 2.5 * cm
    top_margin = 4 * cm
    usable_width = width - 2 * margin
    usable_height = height - top_margin - margin
    
    aspect = usable_width / usable_height
    cols = math.ceil(math.sqrt(count * aspect))
    rows = math.ceil(count / cols)
    
    cell_width = usable_width / cols
    cell_height = usable_height / rows
    
    jitter_x = cell_width * 0.3
    jitter_y = cell_height * 0.3
    max_rotation = 15
    
    positions = []
    for r in range(rows):
        for col in range(cols):
            cx = margin + col * cell_width + cell_width / 2
            cy = (height - top_margin) - (r * cell_height + cell_height / 2)
            positions.append((cx, cy))
    
    random.shuffle(positions)
    positions = positions[:count]
    
    # Generate random numbers from the specified range
    # Use random.sample to ensure no duplicates
    available_numbers = list(range(min_range, max_range + 1))
    selected_numbers = random.sample(available_numbers, count)
    
    for i, number in enumerate(selected_numbers):
        cx, cy = positions[i]
        x = cx + random.uniform(-jitter_x, jitter_x)
        y = cy + random.uniform(-jitter_y, jitter_y)
        rotation = random.uniform(-max_rotation, max_rotation)
        
        # Decide if this number should be replaced by an icon
        if icon_styles and random.random() < icon_replacement_rate:
            # Replace with an icon
            chosen_style = random.choices(icon_styles, weights=icon_weights, k=1)[0]
            draw_icon(c, x, y, number, chosen_style, rotation)
        else:
            # Keep as digit (text)
            draw_digit_text(c, x, y, number, rotation)
    
    c.save()