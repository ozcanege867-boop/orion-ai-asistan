import streamlit as st
from streamlit_mic_recorder import speech_to_text
from googletrans import Translator
import wikipedia
from datetime import datetime
import pytz

# --- GENEL AYARLAR ---
st.set_page_config(page_title="ORION AI", page_icon="🚀", layout="centered")
translator = Translator()
wikipedia.set_lang("tr")

# --- VERİTABANLARI ---
OFFLINE_KNOWLEDGE = {
    "sen kimsin": "Ben ORION, Bursa Bilim Şenliği için özel olarak geliştirilmiş yapay zekayım.",
    "adın ne": "Adım ORION.",
    "merhaba": "Merhaba efendim, sizi dinliyorum.",
    "selam": "Selamlar, emrinizdeyim.",
    "nasılsın": "Tüm fonksiyonlarım yüzde yüz kapasiteyle çalışıyor, teşekkür ederim."
}

DUNYA_SAATLERI = {
    "londra": "Europe/London", "tokyo": "Asia/Tokyo", "pekin": "Asia/Shanghai",
    "new york": "America/New_York", "berlin": "Europe/Berlin", "baku": "Asia/Baku",
    "paris": "Europe/Paris", "sidney": "Australia/Sydney"
}

TIBBI_BILGI = {
    "baş ağrısı": "Bol su için ve karanlık bir ortamda dinlenin.",
    "ateş": "Yüksek ateş enfeksiyon belirtisi olabilir. 38 dereceyi geçerse doktora görünmelisiniz.",
    "grip": "Dinlenmek ve bol sıvı tüketmek iyileşmeyi hızlandırır.",
    "öksürük": "Bitki çayı içebilirsiniz, ancak uzun sürerse doktora başvurun."
}

# --- YARDIMCI FONKSİYONLAR ---
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
    if res: return f"Matematiksel işlemin sonucu: {res}"

    # 2. Dünya Saatleri
    for sehir, dilim in DUNYA_SAATLERI.items():
        if sehir in q_lower:
            saat = datetime.now(pytz.timezone(dilim)).strftime("%H:%M")
            return f"{sehir.capitalize()} şehrinde şu an saat: {saat}"

    # 3. Tıp Modülü
    for belirti, aciklama in TIBBI_BILGI.items():
        if belirti in q_lower:
            return f"{aciklama} (Not: Ben bir yapay zekayım, kesin teşhis için doktora gidin.)"

    # 4. Çevrimdışı Hafıza
    if q_lower in OFFLINE_KNOWLEDGE:
        return OFFLINE_KNOWLEDGE[q_lower]
    
    if "saat kaç" in q_lower:
        return f"Şu an yerel saat: {datetime.now().strftime('%H:%M')}"

    # 5. Wikipedia (En son çare)
    try:
        return wikipedia.summary(q_lower, sentences=1)
    except:
        return "Üzgünüm, bu konuda detaylı bilgi bulamadım ama kendimi geliştiriyorum!"

# --- TASARIM VE ARAYÜZ ---
st.markdown("<h1 style='text-align: center; color: #FF4B4B;'>🚀 ORION AI ASİSTAN</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Bursa Bilim Şenliği 2026 Özel Versiyonu</p>", unsafe_allow_html=True)

st.divider()

# Ses Giriş Bileşeni
text = speech_to_text(start_prompt="🎤 Konuşmak için Dokun", stop_prompt="⏹️ Durdur ve Analiz Et", language='tr')

if text:
    with st.spinner('ORION düşünüyor...'):
        cevap_tr = get_answer(text)
        
        # İngilizceye Çeviri
        try:
            cevap_en = translator.translate(cevap_tr, src='tr', dest='en').text
        except:
            cevap_en = "I encountered a translation error."

        # Ekranda Gösterim
        st.chat_message("user").write(text)
        
        col1, col2 = st.columns(2)
        with col1:
            st.info(f"**TR:** {cevap_tr}")
        with col2:
            st.warning(f"**EN:** {cevap_en}")
        
        # Web Seslendirme (JavaScript - Tırnak hataları düzeltildi)
        safe_en_text = cevap_en.replace('"', '').replace("'", "")
        st.components.v1.html(f"""
            <script>
            var msg = new SpeechSynthesisUtterance("{safe_en_text}");
            msg.lang = 'en-US';
            msg.rate = 0.9;
            window.speechSynthesis.speak(msg);
            </script>
        """, height=0)

st.divider()
st.caption("Geliştirici: Ege / Bursa Bilim Şenliği 2026")
