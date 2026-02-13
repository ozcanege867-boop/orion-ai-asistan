import streamlit as st
from streamlit_mic_recorder import speech_to_text
from googletrans import Translator
import google.generativeai as genai
import wikipedia
from datetime import datetime
import pytz

# --- GEMINI AYARI ---
# Lütfen yeni bir API anahtarı alıp buraya yapıştırın.
MY_API_KEY = "AIzaSyDooqWcwN-XQt3jKHOCBmw32hEUqmthVTU" 

try:
    genai.configure(api_key=MY_API_KEY)
    # 404 hatasını çözmek için en güncel model ismini kullanıyoruz
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error(f"Sistem Başlatılamadı: {e}")

# --- AYARLAR ---
st.set_page_config(page_title="ORION AI", page_icon="🚀", layout="centered")
translator = Translator()
wikipedia.set_lang("tr")
TR_TIMEZONE = pytz.timezone('Europe/Istanbul')

def get_answer(query):
    q_lower = query.lower().strip()
    
    # 1. Saat ve Tarih Sorgusu (Her zaman çalışır)
    if "saat kaç" in q_lower:
        tr_saat = datetime.now(TR_TIMEZONE).strftime("%H:%M")
        return f"Şu an Türkiye'de saat {tr_saat}."

    # 2. Gemini API Sorgusu
    try:
        # Sorguyu doğrudan modele gönderiyoruz
        response = model.generate_content(f"Sen ORION'sun. Kısa cevap ver: {query}")
        return response.text
    except Exception as e:
        # Eğer Gemini yine hata verirse Wikipedia yedeği devreye girer
        try:
            return wikipedia.summary(query, sentences=1)
        except:
            return f"Üzgünüm, şu an bağlantı kuramıyorum. (Detay: {str(e)})"

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

        # Web Seslendirme
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
