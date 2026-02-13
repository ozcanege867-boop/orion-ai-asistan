import streamlit as st
from streamlit_mic_recorder import speech_to_text
from googletrans import Translator
import google.generativeai as genai
import wikipedia
from datetime import datetime
import pytz

# --- GEMINI AYARI ---
MY_API_KEY = "AIzaSyDooqWcwN-XQt3jKHOCBmw32hEUqmthVTU"

try:
    genai.configure(api_key=MY_API_KEY)
    # 404 hatasını aşmak için en güncel isimlendirmeyi deniyoruz
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
    
    # Bursa ile ilgili çok sorulan sorular için hızlı cevap (API hatası olsa bile çalışır)
    if "en kalabalık ilçesi" in q_lower and "bursa" in q_lower:
        return "Bursa'nın en kalabalık ilçesi Osmangazi'dir. 2023 verilerine göre nüfusu 900 bini aşmıştır."

    if "saat kaç" in q_lower:
        return f"Şu an saat {datetime.now(TR_TIMEZONE).strftime('%H:%M')}"

    # GEMINI SORGUSU
    try:
        # 'models/' ön ekini ekleyerek 404 hatasını zorluyoruz
        response = model.generate_content(f"Sen ORION'sun. Kısa cevap ver: {query}")
        return response.text
    except Exception as e:
        # Eğer yine 404 verirse Wikipedia devreye girsin
        try:
            return wikipedia.summary(query, sentences=1)
        except:
            return f"Şu an teknik bir güncelleme yapıyorum. (Hata: {str(e)})"

# --- ARAYÜZ ---
st.markdown("<h1 style='text-align: center; color: #FF4B4B;'>🚀 ORION AI</h1>", unsafe_allow_html=True)

col1, col2 = st.columns([1, 5])
with col1:
    ses = speech_to_text(start_prompt="🎤", stop_prompt="⏹️", language='tr', key='voice')
with col2:
    yazi = st.chat_input("ORION'a bir soru sor...")

girdi = ses if ses else yazi

if girdi:
    st.chat_message("user").write(girdi)
    with st.spinner("ORION cevaplıyor..."):
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
