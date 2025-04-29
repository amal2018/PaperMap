import streamlit as st
from PIL import Image
import io
import datetime  # <-- ADD THIS

st.set_page_config(page_title="Composite Layout", page_icon="assets/br_logo.png", layout="wide")
# --- Align Help Expander to Top Right ---
col1, col2 = st.columns([7, 3])
with col2:
    with st.expander("❓ Help", expanded=False):
        st.markdown("""
        **Contact:**  
        📧 [amalrenv@gmail.com](https://mail.google.com/mail/?view=cm&to=amalrenv@gmail.com
)  
        
        """)


col1, col2, col3 = st.columns([1,2,1])
with col2:
    st.image("assets/PaperMap_logo.png", width=180)
st.title("🖼️ Composite Layout & Download")

def resize_image(im, width):
    return im.resize((width, int(im.height * width / im.width)), Image.LANCZOS)

def combine_images(imgs_left, img_right):
    small_width = 300
    small_imgs = [resize_image(im, small_width) for im in imgs_left]
    h1, h2, h3 = [im.height for im in small_imgs]
    right_aspect = img_right.height / img_right.width
    big_width = 700
    big_height = int(big_width * right_aspect)
    total_left_height = h1 + h2 + h3
    canvas_height = max(total_left_height, big_height)
    if total_left_height > big_height:
        big_height = total_left_height
        big_width = int(big_height / right_aspect)
        img_right_resized = img_right.resize((big_width, big_height), Image.LANCZOS)
    else:
        img_right_resized = img_right.resize((big_width, big_height), Image.LANCZOS)
    canvas_width = small_width + big_width
    gap = (canvas_height - (h1 + h2 + h3)) // 2 if canvas_height > (h1 + h2 + h3) else 0
    y1 = 0
    y2 = h1 + gap
    y3 = y2 + h2 + gap
    left_strip = Image.new('RGBA', (small_width, canvas_height), (255,255,255,255))
    left_strip.paste(small_imgs[0], (0, y1))
    left_strip.paste(small_imgs[1], (0, y2))
    left_strip.paste(small_imgs[2], (0, y3))
    combined = Image.new('RGBA', (canvas_width, canvas_height), (255,255,255,255))
    combined.paste(left_strip, (0,0))
    combined.paste(img_right_resized, (small_width, 0))
    return combined

# --- Load from session_state ---
imgs_left = []
for key in ['india_map', 'state_map', 'district_map']:
    buf = st.session_state.get(key)
    if buf is not None:
        buf.seek(0)
        imgs_left.append(Image.open(buf))
    else:
        imgs_left.append(None)

buf_right = st.session_state.get('study_area_map')
img_right = None
if buf_right is not None:
    buf_right.seek(0)
    img_right = Image.open(buf_right)

if all(imgs_left) and img_right:
    combined = combine_images(imgs_left, img_right)
    st.image(combined, caption="Final Layout", use_container_width=True)
    buf = io.BytesIO()
    combined.save(buf, format="PNG")
    buf.seek(0)
    st.download_button(
        "📥 Download Final Layout as PNG",
        data=buf,
        file_name="PaperMaP.png",
        mime="image/png",
        use_container_width=True
    )
else:
    st.info("Please generate India, State, District, and Study Area maps on the previous pages first.")



# ----------- ADD CITATION AT BOTTOM -----------
import datetime

today_str = datetime.date.today().strftime("%d %B %Y")
st.markdown(
    f"""
    <hr>
    <div style="font-size:0.95em; color: #444; margin-top: 30px; background: #fafafa; border-left: 4px solid #3498db; padding: 1em;">
    <strong>How to cite this app:</strong><br>
    Radhakrishnan, Amal (2024) <i>PaperMap – Publication-Quality Study Area Map Generator (Streamlit App)</i>. Available at: <a href="https://github.com/amal2018/PaperMap/" target="_blank">https://github.com/amal2018/PaperMap/</a> (Accessed: {today_str}).
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <div style="display: flex; align-items: center; margin-top: 30px; background-color: #fff8dc; padding: 1em; border-left: 4px solid #f7b733; border-radius: 6px;">
        <div style="flex-shrink: 0;">
            <a href="https://www.buymeacoffee.com/amalr" target="_blank">
                <img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" 
                     alt="Buy Me A Coffee" 
                     style="height: 45px; width: 162px;">
            </a>
        </div>
        <div style="margin-left: 15px; font-size: 0.9em; color: #444;">
            Enjoying PaperMap or using it in your work? <br>
            You can support continued development by buying me a coffee ☕.<br>
            Every little bit helps!
        </div>
    </div>
    """,
    unsafe_allow_html=True
)
