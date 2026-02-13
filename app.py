import streamlit as st
from streamlit_mic_recorder import speech_to_text
from googletrans import Translator
import google.generativeai as genai
from datetime import datetime
import pytz

# --- AYARLAR ---
st.set_page_config(page_title="ORION AI", page_icon="🚀")
translator = Translator()

# Sayfa Tasarımı
st.markdown("""
    <style>
    .main { background-color: #0f0c29; color: white; }
    .stButton>button { background-color: #ff0033; color: white; border-radius: 20px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🚀 ORION: Akıllı Asistan")
st.write("Bursa Bilim Şenliği 2026 - Mobil Versiyon")

# --- ORION ZEKA MANTIĞI ---
def get_orion_response(text):
    q = text.lower()
    # Hafıza Modülü
    if "sen kimsin" in q:
        return "Ben ORION, Bursa Bilim Şenliği için geliştirilmiş bir yapay zekayım."
    if "saat kaç" in q:
        return f"Şu an saat {datetime.now().strftime('%H:%M')}"
    
    # Buraya senin tıbbi ve matematik modüllerini ekleyebiliriz.
    return "Seni anladım, bu konuda çalışıyorum!"

# --- MİKROFON VE KONUŞMA ---
st.subheader("Konuşmak için mikrofona bas:")
text = speech_to_text(start_prompt="🎤 Dinliyorum...", stop_prompt="⏹️ İşleniyor...", language='tr')

if text:
    st.success(f"Siz: {text}")
    cevap = get_orion_response(text)
    
    # İngilizceye Çeviri
    translation = translator.translate(cevap, src='tr', dest='en')
    st.info(f"ORION (TR): {cevap}")
    st.warning(f"ORION (EN): {translation.text}")
    
    # Telefonun sesli okuması için basit HTML/JS
    st.components.v1.html(f"""
        <script>
        var msg = new SpeechSynthesisUtterance('{translation.text}');
        msg.lang = 'en-US';
        window.speechSynthesis.speak(msg);
        </script>
    """, height=0)
