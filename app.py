import streamlit as st
from streamlit_mic_recorder import speech_to_text
from googletrans import Translator
import google.generativeai as genai
import wikipedia
from datetime import datetime
import pytz

# --- GEMINI AYARI ---
# Kendi API anahtarını buraya tırnak içine yapıştır
GOOGLE_API_KEY = "AIzaSyATCzTcixZk2AJ8OzmvRAMaXvnvZ2t69vk"
genai.configure(api_key=GOOGLE_API_KE)
model = genai.GenerativeModel('gemini-pro')

# --- SAYFA VE DİL AYARLARI ---
st.set_page_config(page_title="ORION AI", page_icon="🚀", layout="centered")
translator = Translator()
wikipedia.set_lang("tr")
TR_TIMEZONE = pytz.timezone('Europe/Istanbul')

# --- SABİT VERİLER (YEDEK) ---
OFFLINE_KNOWLEDGE = {
    "sen kimsin": "Ben ORION, Bursa Bilim Şenliği için Gemini Pro altyapısıyla geliştirilmiş yapay zekayım.",
    "adın ne": "Adım ORION."
}

def get_gemini_response(prompt):
    """Sorguyu Gemini API'ye gönderir."""
    try:
        response = model.generate_content(f"Senin adın ORION. Bursa Bilim Şenliği asistanısın. Kısa ve net cevap ver: {prompt}")
        return response.text
    except:
        return None

def get_answer(query):
    q_lower = query.lower().strip()
    
    # 1. Özel Saat Sorgusu (Hata payı olmaması için sabit tutuyoruz)
    if "saat kaç" in q_lower:
        return f"Şu an Türkiye saati ile {datetime.now(TR_TIMEZONE).strftime('%H:%M')}."

    # 2. Gemini API Sorgusu (Ana Zeka)
    gemini_cevap = get_gemini_response(query)
    if gemini_cevap:
        return gemini_cevap

    # 3. Yedek Sistem (Eğer API hata verirse)
    if q_lower in OFFLINE_KNOWLEDGE:
        return OFFLINE_KNOWLEDGE[q_lower]
    
    try:
        return wikipedia.summary(q_lower, sentences=1)
    except:
        return "Şu an bağlantı kuramıyorum ama üzerinde çalışıyorum."

# --- WEB ARAYÜZÜ ---
st.markdown("<h1 style='text-align: center; color: #FF4B4B;'>🚀 ORION AI (Gemini Pro)</h1>", unsafe_allow_html=True)

col1, col2 = st.columns([1, 5])
with col1:
    ses_girdisi = speech_to_text(start_prompt="🎤", stop_prompt="⏹️", language='tr', key='voice')
with col2:
    yazi_girdisi = st.chat_input("Gemini'ye bir şey sor...")

girdi = ses_girdisi if ses_girdisi else yazi_girdisi

if girdi:
    st.chat_message("user").write(girdi)
    with st.spinner("Gemini Pro düşünerek cevaplıyor..."):
        cevap_tr = get_answer(girdi)
        try:
            cevap_en = translator.translate(cevap_tr, src='tr', dest='en').text
        except:
            cevap_en = "Translation error."

        with st.chat_message("assistant"):
            st.info(f"**TR:** {cevap_tr}")
            st.warning(f"**EN:** {cevap_en}")

        safe_en = cevap_en.replace('"', '').replace("'", "")
        st.components.v1.html(f"""
            <script>
                window.speechSynthesis.cancel();
                var msg = new SpeechSynthesisUtterance("{safe_en}");
                msg.lang = "en-US";
                window.speechSynthesis.speak(msg);
            </script>
        """, height=0)

# --- İLETİŞİM ---
st.divider()
with st.expander("📬 İletişim"):
    st.code("iletisim.orionai@gmail.com", language="text")
