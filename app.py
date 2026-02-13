import streamlit as st
from streamlit_mic_recorder import speech_to_text
from googletrans import Translator
import google.generativeai as genai
import wikipedia
from datetime import datetime
import pytz

# --- GEMINI AYARI ---
# Kendi API anahtarını buraya tırnak içine yapıştır
MY_API_KEY = "AIzaSyDQLCWp_Tq_mg1z9cqT78ABajV6jv5UT7I"

try:
    genai.configure(api_key=MY_API_KEY)
    # En stabil ve uyumlu model olan gemini-pro kullanılıyor
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
    
    # 1. Özel Saat ve Tarih Sorgusu
    if "saat kaç" in q_lower:
        tr_saat = datetime.now(TR_TIMEZONE).strftime("%H:%M")
        return f"Şu an Türkiye'de saat {tr_saat}."
    
    if "tarih" in q_lower or "günlerden ne" in q_lower:
        tr_tarih = datetime.now(TR_TIMEZONE).strftime("%d.%m.%Y")
        return f"Bugün tarih {tr_tarih}."

    # 2. Gemini Pro Sorgusu
    try:
        # Gemini'ye soruyu gönderiyoruz
        response = model.generate_content(f"Senin adın ORION. Bursa Bilim Şenliği asistanısın. Kısa ve öz cevap ver: {query}")
        if response.text:
            return response.text
    except Exception as e:
        # Hata durumunda Wikipedia yedeği
        try:
            return wikipedia.summary(query, sentences=1)
        except:
            return f"Üzgünüm, şu an bilgiye erişemiyorum. (Hata: {str(e)})"

# --- WEB ARAYÜZÜ ---
st.markdown("<h1 style='text-align: center; color: #FF4B4B;'>🚀 ORION AI (Gemini Pro)</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Bursa Bilim Şenliği 2026</p>", unsafe_allow_html=True)

# Girdi Alanları
col1, col2 = st.columns([1, 5])
with col1:
    ses_girdisi = speech_to_text(start_prompt="🎤", stop_prompt="⏹️", language='tr', key='voice')

with col2:
    yazi_girdisi = st.chat_input("ORION'a bir soru sor...")

# Hangi girdi geldiyse onu kullan
girdi = ses_girdisi if ses_girdisi else yazi_girdisi

if girdi:
    st.chat_message("user").write(girdi)
    with st.spinner("ORION düşünüyor..."):
        cevap_tr = get_answer(girdi)
        
        # İngilizce Çeviri (Seslendirme için)
        try:
            cevap_en = translator.translate(cevap_tr, src='tr', dest='en').text
        except:
            cevap_en = "System translation error."

        # Mesajları Göster
        with st.chat_message("assistant"):
            st.info(f"**TR:** {cevap_tr}")
            st.warning(f"**EN:** {cevap_en}")

        # Tarayıcı Tabanlı Seslendirme (JavaScript)
        safe_en = cevap_en.replace('"', '').replace("'", "")
        st.components.v1.html(f"""
            <script>
                window.speechSynthesis.cancel();
                var msg = new SpeechSynthesisUtterance("{safe_en}");
                msg.lang = "en-US";
                window.speechSynthesis.speak(msg);
            </script>
        """, height=0)

# --- İLETİŞİM BÖLÜMÜ ---
st.divider()
with st.expander("📬 İletişim ve Geri Bildirim"):
    st.write("Sorularınız veya yeni fikirleriniz için bize ulaşın:")
    st.code("iletisim.orionai@gmail.com", language="text")

st.caption("Geliştirici: Ege - Bursa Bilim Şenliği Protokolü")
