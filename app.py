# app.py
import streamlit as st
import generator
import pymupdf as fitz  # Updated import
import os
import base64
import logging

import datetime
print(f"📅 App loaded at: {datetime.datetime.now()}")
print(f"📄 File: {__file__}")

logging.getLogger("watchdog").setLevel(logging.WARNING)

# --- PAGE CONFIG ---
st.set_page_config(page_title="Math Worksheet Generator", layout="centered")
st.title("🎲 Zahlen Wettrennen Generator V1.0.0")
st.write("Create custom number recognition worksheets for your students.")

# --- AUTO-DISCOVER ICON SETS ---
def get_available_icon_sets():
    """Scans the icons/ folder and returns a list of available set names."""
    icons_dir = "icons"
    if not os.path.exists(icons_dir):
        return []
    
    sets = []
    for item in os.listdir(icons_dir):
        item_path = os.path.join(icons_dir, item)
        if os.path.isdir(item_path):
            sets.append(item)
    
    return sorted(sets)

available_sets = get_available_icon_sets()

# --- SIDEBAR CONTROLS ---
st.sidebar.header("Worksheet Settings")

# 1. Number Range
st.sidebar.subheader("Number Range")
min_range = st.sidebar.number_input("Minimum number", min_value=0, max_value=9999, value=1, step=1)
max_range = st.sidebar.number_input("Maximum number", min_value=0, max_value=9999, value=100, step=1)

# Validate range
if min_range > max_range:
    st.sidebar.error("⚠️ Minimum number cannot be greater than maximum number!")
    st.stop()

# Calculate how many unique numbers are available
available_count = max_range - min_range + 1

# 2. Amount of numbers
st.sidebar.subheader("Amount")
count = st.sidebar.number_input(
    "How many numbers to generate?",
    min_value=1,
    max_value=available_count,
    value=min(10, available_count),
    step=1
)

# 3. Icon Replacement Rate
st.sidebar.subheader("Icon Replacement")
icon_replacement_rate = st.sidebar.slider(
    "How many numbers should be replaced by icons?",
    min_value=0,
    max_value=100,
    value=50,
    help="0% = all digits, 100% = all icons"
) / 100.0

# 4. Select Icon Sets (only shown if replacement rate > 0)
if icon_replacement_rate > 0:
    st.sidebar.subheader("Icon Styles")
    
    if not available_sets:
        st.sidebar.warning("⚠️ No icon sets found in 'icons/' folder!")
        selected_styles = []
    else:
        selected_styles = []
        for set_name in available_sets:
            if st.sidebar.checkbox(set_name.capitalize(), value=True, key=f"chk_{set_name}"):
                selected_styles.append(set_name)
    
    # 5. Icon Distribution (only shown if at least one icon set selected)
    if selected_styles:
        st.sidebar.subheader("Icon Distribution (%)")
        st.sidebar.caption("How to distribute icons among selected sets")
        
        weights_dict = {}
        for set_name in selected_styles:
            weights_dict[set_name] = st.sidebar.slider(
                f"{set_name.capitalize()} %", 
                0, 100, 
                100 // len(selected_styles),
                key=f"w_{set_name}"
            )
        
        total_weight = sum(weights_dict.values())
        if total_weight == 0:
            st.sidebar.warning("⚠️ Total icon weight cannot be zero.")
            st.stop()
        
        # Normalize weights
        icon_weights = [weights_dict[s] / total_weight for s in selected_styles]
    else:
        icon_weights = []
else:
    selected_styles = []
    icon_weights = []

# --- MAIN PAGE ---
st.divider()

preview_container = st.container()

if st.button("🚀 Generate Worksheet", type="primary", use_container_width=True):
    with st.spinner("Drawing your worksheet..."):
        output_file = "generated_worksheet.pdf"
        
        generator.generate_worksheet(
            min_range=min_range,
            max_range=max_range,
            count=count,
            icon_styles=selected_styles,
            icon_weights=icon_weights,
            icon_replacement_rate=icon_replacement_rate,
            filename=output_file
        )
        
        # --- PDF PREVIEW ---
        preview_container.subheader("📄 Preview")
        
        try:
            doc = fitz.open(output_file)
            page = doc[0]
            
            mat = fitz.Matrix(2, 2)
            pix = page.get_pixmap(matrix=mat)
            img_bytes = pix.tobytes("png")
            doc.close()
            
            img_base64 = base64.b64encode(img_bytes).decode()
            
            preview_html = f"""
            <div style="display: flex; justify-content: center; padding: 20px 0;">
                <img src="data:image/png;base64,{img_base64}" 
                     style="border: 2px solid #555; 
                            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
                            max-width: 100%;
                            background-color: white;
                            padding: 0;" />
            </div>
            """
            preview_container.markdown(preview_html, unsafe_allow_html=True)
            
        except Exception as e:
            preview_container.error(f"Could not generate preview: {e}")
        
        # --- DOWNLOAD BUTTON ---
        preview_container.divider()
        with open(output_file, "rb") as file:
            preview_container.download_button(
                label="📥 Download PDF",
                data=file,
                file_name=f"worksheet_{count}_nums.pdf",
                mime="application/pdf",
                use_container_width=True
            )
            
        preview_container.success("✅ Worksheet generated successfully!")