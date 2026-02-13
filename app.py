import streamlit as st
from streamlit_mic_recorder import speech_to_text
from googletrans import Translator
import wikipedia
from datetime import datetime
import pytz

# --- AYARLAR ---
st.set_page_config(page_title="ORION AI", page_icon="🚀")
translator = Translator()
wikipedia.set_lang("tr")

# --- VERİTABANLARI (Senin Kodundan Alındı) ---
OFFLINE_KNOWLEDGE = {
    "sen kimsin": "Ben ORION, Bursa Bilim Şenliği için özel olarak geliştirilmiş yapay zekayım.",
    "adın ne": "Adım ORION.",
    "merhaba": "Merhaba efendim, sizi dinliyorum.",
    "selam": "Selamlar, emrinizdeyim."
}

DUNYA_SAATLERI = {
    "londra": "Europe/London", "tokyo": "Asia/Tokyo", "pekin": "Asia/Shanghai",
    "new york": "America/New_York", "berlin": "Europe/Berlin", "baku": "Asia/Baku"
}

TIBBI_BILGI = {
    "baş ağrısı": "Bol su için ve karanlık bir ortamda dinlenin.",
    "ateş": "Yüksek ateş enfeksiyon belirtisi olabilir. Doktora görünmelisiniz.",
    "grip": "Dinlenmek ve bol sıvı tüketmek iyileşmeyi hızlandırır."
}

# --- FONKSİYONLAR ---
def calculate(query):
    q = query.replace("artı", "+").replace("eksi", "-").replace("çarpı", "*").replace("bölü", "/")
    temiz_islem = "".join([c for c in q if c.isdigit() or c in "+-*/."])
    if len(temiz_islem) >= 3:
        try: return eval(temiz_islem)
        except: return None
    return None

def get_answer(query):
    q_lower = query.lower().strip()
    
    # 1. Matematik
    res = calculate(q_lower)
    if res: return f"İşlemin sonucu: {res}"

    # 2. Dünya Saatleri
    for sehir, dilim in DUNYA_SAATLERI.items():
        if sehir in q_lower:
            saat = datetime.now(pytz.timezone(dilim)).strftime("%H:%M")
            return f"{sehir.capitalize()} şehrinde saat: {saat}"

    # 3. Tıp Modülü
    for belirti, aciklama in TIBBI_BILGI.items():
        if belirti in q_lower:
            return f"{aciklama} (Not: Kesin teşhis için doktora gidin.)"

    # 4. Çevrimdışı Hafıza
    if q_lower in OFFLINE_KNOWLEDGE:
        return OFFLINE_KNOWLEDGE[q_lower]

    # 5. Wikipedia
    try:
        return wikipedia.summary(q_lower, sentences=1)
    except:
        return "Üzgünüm, bu konuda net bir bilgi bulamadım."

# --- WEB ARAYÜZÜ ---
st.title("🚀 ORION: Çok Fonksiyonlu Asistan")
st.write("Bursa Bilim Şenliği 2026 - Mobil Protokol")

# Web uyumlu ses girişi
text = speech_to_text(start_prompt="🎤 Konuşmak için basın", stop_prompt="⏹️ İşleniyor...", language='tr')

if text:
    cevap_tr = get_answer(text)
    cevap_en = translator.translate(cevap_tr, src='tr', dest='en').text

    st.chat_message("user").write(text)
    st.chat_message("assistant").write(f"**TR:** {cevap_tr}")
    st.chat_message("assistant").write(f"**EN:** {cevap_en}")
    
    # Web uyumlu seslendirme (İngilizce okur)
    st.components.v1.html(f"""
        <script>
        var msg = new SpeechSynthesisUtterance('{cevap_en.replace("'", "")}');
        msg.lang = 'en-US';
        window.speechSynthesis.speak(msg);
        </script>
    """, height=0)
