import streamlit as st
import base64
from PIL import Image
import io
import json
from groq import Groq
import os
from dotenv import load_dotenv

# Load API key from .env file automatically
load_dotenv()
saved_key = os.getenv("GROQ_API_KEY", "")

# ─── Page Config ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="FaunaSense",
    page_icon="🦁",
    layout="centered",
)

# ─── Custom CSS ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=DM+Sans:wght@300;400;500&display=swap');

html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }

.stApp {
    background: linear-gradient(135deg, #0d1b2a 0%, #1b2d45 50%, #0d1b2a 100%);
    min-height: 100vh;
}

.fauna-title {
    font-family: 'Playfair Display', serif;
    font-size: 3.2rem;
    font-weight: 700;
    background: linear-gradient(90deg, #f5c842, #f58c42);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    text-align: center;
    margin-bottom: 0.2rem;
    letter-spacing: -1px;
}

.fauna-subtitle {
    text-align: center;
    color: #8ba3be;
    font-size: 1rem;
    font-weight: 300;
    margin-bottom: 2rem;
    letter-spacing: 0.1em;
    text-transform: uppercase;
}

.result-card {
    background: linear-gradient(135deg, rgba(245,200,66,0.12), rgba(245,140,66,0.06));
    border: 1px solid rgba(245, 200, 66, 0.3);
    border-radius: 20px;
    padding: 1.8rem 2rem;
    margin: 1.5rem 0;
}

.result-animal-name {
    font-family: 'Playfair Display', serif;
    font-size: 2.2rem;
    color: #f5c842;
    margin-bottom: 0.3rem;
}

.result-confidence {
    color: #f58c42;
    font-size: 0.85rem;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    margin-bottom: 1rem;
}

.result-description { color: #c8d8e8; font-size: 0.97rem; line-height: 1.7; }

.result-facts {
    margin-top: 1rem;
    padding-top: 1rem;
    border-top: 1px solid rgba(245,200,66,0.2);
}

.fact-item { color: #a8c0d4; font-size: 0.9rem; margin: 0.35rem 0; padding-left: 0.5rem; }

hr { border-color: rgba(245,200,66,0.15) !important; }

.stButton > button {
    background: linear-gradient(90deg, #f5c842, #f58c42) !important;
    color: #0d1b2a !important;
    font-weight: 600 !important;
    border: none !important;
    border-radius: 50px !important;
    padding: 0.6rem 2rem !important;
    font-family: 'DM Sans', sans-serif !important;
    letter-spacing: 0.05em !important;
}

.tab-content { padding: 1rem 0; }
</style>
""", unsafe_allow_html=True)

# ─── Header ─────────────────────────────────────────────────────────────────
st.markdown('<div class="fauna-title">🦁 FaunaSense</div>', unsafe_allow_html=True)
st.markdown('<div class="fauna-subtitle">AI-Powered Animal Recognition System</div>', unsafe_allow_html=True)

# ─── Animal List ─────────────────────────────────────────────────────────────
ANIMALS = [
    "antelope", "badger", "bat", "bear", "bee", "beetle", "bison", "boar",
    "butterfly", "cat", "caterpillar", "chimpanzee", "cockroach", "cow",
    "coyote", "crab", "crow", "deer", "dog", "dolphin", "donkey", "dragonfly",
    "duck", "eagle", "elephant", "flamingo", "fly", "fox", "goat", "goldfish",
    "goose", "gorilla", "grasshopper", "hamster", "hare", "hedgehog",
    "hippopotamus", "hornbill", "horse", "hummingbird", "hyena", "jellyfish",
    "kangaroo", "koala", "ladybugs", "leopard", "lion", "lizard", "lobster",
    "mosquito", "moth", "mouse", "octopus", "okapi", "orangutan", "otter",
    "owl", "ox", "oyster", "panda", "parrot", "pelecaniformes", "penguin",
    "pig", "pigeon", "porcupine", "possum", "raccoon", "rat", "reindeer",
    "rhinoceros", "sandpiper", "seahorse", "seal", "shark", "sheep", "snake",
    "sparrow", "squid", "squirrel", "starfish", "swan", "tiger", "turkey",
    "turtle", "whale", "wolf", "wombat", "woodpecker", "zebra"
]

# ─── Sidebar ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Settings")
    api_key = st.text_input(
        "Groq API Key",
        value=saved_key,
        type="password",
        placeholder="gsk_...",
        help="Auto-loaded from .env file"
    )
    if saved_key:
        st.success("✅ API Key loaded from .env!")

    st.markdown("---")
    voice_enabled = st.toggle("🔊 Voice Announcement", value=True)
    st.markdown("---")
    st.markdown("### 🐾 Supported Animals")
    st.markdown("This system can identify **90+ animals**")
    cols = st.columns(2)
    for i, animal in enumerate(ANIMALS[:20]):
        cols[i % 2].markdown(f"• {animal.capitalize()}")
    st.markdown(f"*...and {len(ANIMALS) - 20} more!*")

# ─── Voice Function ──────────────────────────────────────────────────────────
def speak_animal(animal_name, description):
    if voice_enabled:
        text = f"Animal detected! This is a {animal_name}. {description}"
        import streamlit.components.v1 as components
        components.html(f"""
        <div style="margin-top:10px;">
            <button onclick="speakNow()" style="
                background: linear-gradient(90deg, #f5c842, #f58c42);
                color: #0d1b2a;
                border: none;
                padding: 10px 28px;
                border-radius: 50px;
                font-size: 15px;
                font-weight: bold;
                cursor: pointer;
                width: 100%;
            ">🔊 Speak Result</button>
        </div>
        <script>
        function speakNow() {{
            window.speechSynthesis.cancel();
            var msg = new SpeechSynthesisUtterance("{text}");
            msg.rate = 0.85;
            msg.pitch = 1.0;
            msg.volume = 1.0;
            msg.lang = "en-US";
            window.speechSynthesis.speak(msg);
        }}
        </script>
        """, height=60)

# ─── Detection Function ──────────────────────────────────────────────────────
def detect_animal(image, api_key):
    buf = io.BytesIO()
    fmt = image.format if image.format else "JPEG"
    if fmt not in ["JPEG", "PNG", "WEBP"]:
        fmt = "JPEG"
    image.save(buf, format=fmt)
    img_bytes = buf.getvalue()
    img_b64 = base64.standard_b64encode(img_bytes).decode("utf-8")
    media_type_map = {"JPEG": "image/jpeg", "PNG": "image/png", "WEBP": "image/webp"}
    media_type = media_type_map.get(fmt, "image/jpeg")

    animals_list = ", ".join(ANIMALS)
    prompt = f"""You are FaunaSense, an expert wildlife identification AI.
Analyze the uploaded image and identify the animal in it.
The system is trained on these animals: {animals_list}
Respond ONLY in this exact JSON format (no markdown, no backticks):
{{
  "animal": "<animal name>",
  "confidence": "<High | Medium | Low>",
  "in_database": <true | false>,
  "description": "<2-3 sentence description>",
  "habitat": "<where this animal lives>",
  "diet": "<what this animal eats>",
  "fun_fact": "<one interesting fun fact>",
  "conservation_status": "<e.g. Least Concern, Vulnerable, Endangered>"
}}
If no animal is visible, set animal to "No animal detected" and in_database to false."""

    client = Groq(api_key=api_key)
    response = client.chat.completions.create(
        model="meta-llama/llama-4-scout-17b-16e-instruct",
        messages=[{
            "role": "user",
            "content": [
                {"type": "image_url", "image_url": {"url": f"data:{media_type};base64,{img_b64}"}},
                {"type": "text", "text": prompt}
            ]
        }],
        max_tokens=700,
    )
    raw = response.choices[0].message.content.strip()
    raw = raw.replace("```json", "").replace("```", "").strip()
    return json.loads(raw)

# ─── Show Result Function ────────────────────────────────────────────────────
def show_result(result):
    animal_name = result.get("animal", "Unknown")
    confidence = result.get("confidence", "—")
    in_db = result.get("in_database", False)
    description = result.get("description", "")
    habitat = result.get("habitat", "—")
    diet = result.get("diet", "—")
    fun_fact = result.get("fun_fact", "—")
    conservation = result.get("conservation_status", "—")

    badge_color = {"High": "#27ae60", "Medium": "#f39c12", "Low": "#e74c3c"}.get(confidence, "#888")
    db_badge = "✅ In Database" if in_db else "⚠️ Not in training list"

    st.markdown(f"""
    <div class="result-card">
        <div class="result-animal-name">🐾 {animal_name}</div>
        <div class="result-confidence">
            Confidence: <span style="color:{badge_color}">● {confidence}</span>
            &nbsp;&nbsp;|&nbsp;&nbsp; {db_badge}
        </div>
        <div class="result-description">{description}</div>
        <div class="result-facts">
            <div class="fact-item">🌍 <strong>Habitat:</strong> {habitat}</div>
            <div class="fact-item">🍃 <strong>Diet:</strong> {diet}</div>
            <div class="fact-item">💡 <strong>Fun Fact:</strong> {fun_fact}</div>
            <div class="fact-item">♻️ <strong>Conservation Status:</strong> {conservation}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Voice announcement
    speak_animal(animal_name, description)

# ─── Main Tabs ───────────────────────────────────────────────────────────────
st.markdown("---")
tab1, tab2 = st.tabs(["📁 Upload Image", "📷 Live Camera"])

# ── Tab 1: Upload ─────────────────────────────────────────────────────────────
with tab1:
    uploaded_file = st.file_uploader(
        "Upload an animal image",
        type=["jpg", "jpeg", "png", "webp"],
    )

    if uploaded_file:
        image = Image.open(uploaded_file)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.image(image, caption="Uploaded Image", use_container_width=True)

        if st.button("🔍 Identify Animal", use_container_width=True, key="upload_btn"):
            if not api_key:
                st.error("⚠️ Please enter your Groq API key in the sidebar.")
            else:
                with st.spinner("Analysing image with AI..."):
                    try:
                        result = detect_animal(image, api_key)
                        show_result(result)
                    except json.JSONDecodeError:
                        st.warning("Could not parse response.")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")

# ── Tab 2: Live Camera ────────────────────────────────────────────────────────
with tab2:
    st.markdown("### 📷 Take a Photo with Your Camera")
    st.info("Allow camera access when browser asks for permission!")

    camera_image = st.camera_input("Point camera at an animal and take a photo!")

    if camera_image:
        image = Image.open(camera_image)

        if st.button("🔍 Identify Animal", use_container_width=True, key="camera_btn"):
            if not api_key:
                st.error("⚠️ Please enter your Groq API key in the sidebar.")
            else:
                with st.spinner("Analysing image with AI..."):
                    try:
                        result = detect_animal(image, api_key)
                        show_result(result)
                    except json.JSONDecodeError:
                        st.warning("Could not parse response.")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")

# ─── Footer ──────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<div style='text-align:center; color:#4a6a8a; font-size:0.8rem;'>"
    "FaunaSense · Powered by Groq AI (Free) · 90+ Species Database"
    "</div>",
    unsafe_allow_html=True
)
