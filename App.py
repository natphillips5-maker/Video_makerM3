import streamlit as st
import os
from moviepy.editor import ImageClip, AudioFileClip, CompositeVideoClip
import tempfile

# === STUDIO CONFIGURATION ===
st.set_page_config(page_title="Silas Thorne Studios", page_icon="🔮", layout="wide")

# === STYLING (Dark/Witchcore) ===
st.markdown("""
    <style>
    .stApp {
        background-color: #0e1117;
        color: #bfa5d1;
    }
    .stButton>button {
        background-color: #4b2c6e;
        color: white;
        border-radius: 5px;
        border: 1px solid #7c4dff;
    }
    h1 {
        color: #d8b4fe;
        font-family: 'Courier New', monospace;
    }
    </style>
    """, unsafe_allow_html=True)

# === HEADER ===
st.title("🔮 SILAS THORNE STUDIOS")
st.markdown("### AI Production Dashboard")

# === SIDEBAR (Controls) ===
with st.sidebar:
    st.header("⚙️ Configuration")
    mode = st.radio("Output Format", ["TikTok (9:16)", "YouTube (16:9)"])
    zoom_speed = st.slider("Zoom Intensity", 0.01, 0.10, 0.04)
    watermark_text = st.text_input("Watermark", "SILAS THORNE")

# === MAIN INTERFACE ===
col1, col2 = st.columns(2)

with col1:
    st.subheader("1. Upload Visuals")
    uploaded_image = st.file_uploader("Drop Art Here", type=['png', 'jpg', 'jpeg'])

with col2:
    st.subheader("2. Upload Audio")
    uploaded_audio = st.file_uploader("Drop Music Here", type=['mp3', 'wav'])

# === THE ENGINE ===
def process_video(image_file, audio_file):
    # Save uploads to temp files so MoviePy can read them
    tfile_img = tempfile.NamedTemporaryFile(delete=False, suffix='.png') 
    tfile_img.write(image_file.read())
    
    tfile_audio = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') 
    tfile_audio.write(audio_file.read())

    # Setup Resolution
    if mode == "TikTok (9:16)":
        W, H = 1080, 1920
    else:
        W, H = 1920, 1080

    try:
        # Load Audio
        audio = AudioFileClip(tfile_audio.name)
        duration = audio.duration
        
        # Load Image
        clip = ImageClip(tfile_img.name).set_duration(duration)
        
        # Crop to Fill
        ratio_clip = clip.w / clip.h
        ratio_target = W / H
        if ratio_clip > ratio_target:
            new_w = clip.h * ratio_target
            clip = clip.crop(x1=clip.w/2 - new_w/2, width=new_w, height=clip.h)
        else:
            new_h = clip.w / ratio_target
            clip = clip.crop(y1=clip.h/2 - new_h/2, width=clip.w, height=new_h)
            
        clip = clip.resize((W, H))
        
        # Apply Zoom
        clip = clip.resize(lambda t: 1 + zoom_speed * t).set_position('center')
        
        # Combine
        final = clip.set_audio(audio)
        
        # Write to Output
        output_path = "render.mp4"
        final.write_videofile(output_path, fps=24, codec="libx264", audio_codec="aac")
        
        return output_path
        
    except Exception as e:
        st.error(f"Render Error: {e}")
        return None

# === ACTION BUTTON ===
st.markdown("---")
if uploaded_image and uploaded_audio:
    if st.button("🚀 LAUNCH RENDER"):
        with st.spinner("Rendering Video... (This uses GPU)"):
            result_file = process_video(uploaded_image, uploaded_audio)
            
        if result_file:
            st.success("Render Complete!")
            st.video(result_file)
            with open(result_file, "rb") as file:
                btn = st.download_button(
                    label="📥 Download Video",
                    data=file,
                    file_name="silas_studio_render.mp4",
                    mime="video/mp4"
                )
else:
    st.info("Upload both an image and an audio file to enable the render engine.")

