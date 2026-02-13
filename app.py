import streamlit as st
from streamlit_mic_recorder import speech_to_text
from googletrans import Translator
import google.generativeai as genai
import wikipedia
from datetime import datetime
import pytz

# --- GEMINI AYARI ---
# LÜTFEN DİKKAT: Anahtarı " " işaretleri arasına yapıştırın.
MY_API_KEY = "AIzaSyDQLCWp_Tq_mg1z9cqT78ABajV6jv5UT7I" 

try:
    genai.configure(api_key=MY_API_KEY)
    model = genai.GenerativeModel('gemini-pro')
except Exception as e:
    st.error(f"Sistem Başlatılamadı: {e}")

# --- AYARLAR ---
st.set_page_config(page_title="ORION AI", page_icon="🚀", layout="centered")
translator = Translator()
wikipedia.set_lang("tr")
TR_TIMEZONE = pytz.timezone('Europe/Istanbul')

def get_answer(query):
    q_lower = query.lower().strip()
    
    # Özel durum: Beşiktaş gibi çok anlamlı kelimeleri spor kulübüne yönlendir
    if "beşiktaş" in q_lower and "ne zaman kuruldu" in q_lower:
        query = "Beşiktaş Jimnastik Kulübü kuruluş tarihi"

    # 1. Gemini API Sorgusu (Öncelikli)
    try:
        response = model.generate_content(f"Sen ORION'sun. Kısa cevap ver: {query}")
        if response.text:
            return response.text
    except Exception as e:
        # Gemini hata verirse Wikipedia'ya düşer
        try:
            return wikipedia.summary(query, sentences=1)
        except:
            return "Şu an bağlantı kuramıyorum, lütfen API anahtarını kontrol et."

# --- WEB ARAYÜZÜ ---
st.markdown("<h1 style='text-align: center; color: #FF4B4B;'>🚀 ORION AI</h1>", unsafe_allow_html=True)

col1, col2 = st.columns([1, 5])
with col1:
    ses = speech_to_text(start_prompt="🎤", stop_prompt="⏹️", language='tr', key='voice')
with col2:
    yazi = st.chat_input("ORION'a bir soru sor...")

girdi = ses if ses else yazi

if girdi:
    st.chat_message("user").write(girdi)
    with st.spinner("ORION düşünüyor..."):
        cevap_tr = get_answer(girdi)
        
        try:
            cevap_en = translator.translate(cevap_tr, src='tr', dest='en').text
        except:
            cevap_en = "Translation error."

        with st.chat_message("assistant"):
            st.info(f"**TR:** {cevap_tr}")
            st.warning(f"**EN:** {cevap_en}")

        # Seslendirme
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
