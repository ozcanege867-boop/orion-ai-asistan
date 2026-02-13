import streamlit as st
from streamlit_mic_recorder import speech_to_text
from googletrans import Translator
import wikipedia
from datetime import datetime
import pytz

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="ORION AI", page_icon="🚀", layout="centered")

# --- BAŞLANGIÇ AYARLARI ---
translator = Translator()
wikipedia.set_lang("tr")
TR_TIMEZONE = pytz.timezone('Europe/Istanbul')

# --- 1. ÇEVRİMDIŞI HAFIZA ---
OFFLINE_KNOWLEDGE = {
    "sen kimsin": "Ben ORION, Bursa Bilim Şenliği için özel olarak geliştirilmiş yapay zeka asistanıyım.",
    "hakkında bilgi ver": "Ben ORION; ismimi avcı takımyıldızından alıyorum. Görevim size yardımcı olmaktır.",
    "kendinden bahset": "Ben bir yapay zeka protokolüyüm. Python diliyle programlandım.",
    "adın ne": "Adım ORION.",
    "nasılsın": "Tüm fonksiyonlarım yüzde yüz kapasiteyle çalışıyor, teşekkür ederim.",
    "merhaba": "Merhaba efendim, sizi dinliyorum.",
    "selam": "Selamlar, emrinizdeyim."
}

# --- 2. DÜNYA SAATLERİ ---
DUNYA_SAATLERI = {
    "londra": "Europe/London", "tokyo": "Asia/Tokyo", "pekin": "Asia/Shanghai",
    "new york": "America/New_York", "berlin": "Europe/Berlin", "moskova": "Europe/Moscow",
    "paris": "Europe/Paris", "baku": "Asia/Baku", "bakü": "Asia/Baku", "sidney": "Australia/Sydney"
}

# --- 3. TIBBİ BİLGİ ---
TIBBI_BILGI = {
    "baş ağrısı": "Bol su için ve karanlık bir ortamda dinlenin.",
    "ateş": "Yüksek ateş enfeksiyon belirtisi olabilir. 38 dereceyi geçerse doktora gidin.",
    "mide bulantısı": "Ağır yiyeceklerden kaçının, zencefil çayı iyi gelebilir.",
    "öksürük": "Bitki çayı içebilirsiniz, uzun sürerse doktora başvurun.",
    "halsizlik": "Vitamin eksikliği olabilir, kan değerlerinize baktırın.",
    "grip": "Bol sıvı tüketin ve dinlenin."
}

# --- YARDIMCI FONKSİYONLAR ---
def calculate(query):
    q = query.replace("artı", "+").replace("eksi", "-").replace("çarpı", "*").replace("bölü", "/")
    q = q.replace("x", "*").replace("kere", "*").replace(",", ".").replace("kaç eder", "").replace("kaçtır", "")
    temiz_islem = "".join([c for c in q if c.isdigit() or c in "+-*/."])
    if len(temiz_islem) >= 3:
        try: return f"İşlemin sonucu: {eval(temiz_islem)}"
        except: return None
    return None

def clean_search_query(query):
    durak_kelimeler = ["nedir", "kimdir", "neredir", "hakkında bilgi", "bana anlat"]
    temiz_sorgu = query.lower()
    for kelime in durak_kelimeler:
        temiz_sorgu = temiz_sorgu.replace(kelime, "")
    return temiz_sorgu.strip()

def get_answer(query):
    q_lower = query.lower().strip()
    math_res = calculate(q_lower)
    if math_res: return math_res

    if "saat" in q_lower:
        for sehir, zaman_dilimi in DUNYA_SAATLERI.items():
            if sehir in q_lower:
                try:
                    tz = pytz.timezone(zaman_dilimi)
                    sehir_saati = datetime.now(tz).strftime("%H:%M")
                    return f"{sehir.capitalize()} şehrinde şu an saat {sehir_saati}"
                except: pass

    for belirti, aciklama in TIBBI_BILGI.items():
        if belirti in q_lower:
            return f"Tespit edilen durum: {belirti}. {aciklama}"

    if q_lower in OFFLINE_KNOWLEDGE:
        return OFFLINE_KNOWLEDGE[q_lower]
    
    if "saat kaç" in q_lower:
        return f"Şu an saat {datetime.now(TR_TIMEZONE).strftime('%H:%M')}"
        
    if "tarih" in q_lower or "günlerden ne" in q_lower:
        return f"Bugün tarih {datetime.now(TR_TIMEZONE).strftime('%d.%m.%Y')}"

    arama_terimi = clean_search_query(q_lower)
    if len(arama_terimi) > 2:
        try: return wikipedia.summary(arama_terimi, sentences=1)
        except: return "Üzgünüm, bu konuda bilgi bulamadım."
            
    return "Sizi tam anlayamadım, tekrar eder misiniz?"

# --- WEB ARAYÜZÜ ---
st.markdown("<h1 style='text-align: center; color: #FF4B4B;'>🚀 ORION AI ASİSTAN</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Bursa Bilim Şenliği 2026</p>", unsafe_allow_html=True)

# Girdiler
col1, col2 = st.columns([1, 5])
with col1:
    ses_girdisi = speech_to_text(start_prompt="🎤", stop_prompt="⏹️", language='tr', key='voice')

with col2:
    yazi_girdisi = st.chat_input("Buraya yazın veya mikrofona basın...")

girdi = ses_girdisi if ses_girdisi else yazi_girdisi

if girdi:
    st.chat_message("user").write(girdi)
    with st.spinner("ORION düşünüyor..."):
        cevap_tr = get_answer(girdi)
        try:
            cevap_en = translator.translate(cevap_tr, src='tr', dest='en').text
        except:
            cevap_en = "System error."

        with st.chat_message("assistant"):
            st.info(f"**TR:** {cevap_tr}")
            st.warning(f"**EN:** {cevap_en}")

        safe_en = cevap_en.replace('"', '').replace("'", "")
        st.components.v1.html(f"""
            <script>
                window.speechSynthesis.cancel();
                var msg = new SpeechSynthesisUtterance("{safe_en}");
                msg.lang = "en-US";
                msg.rate = 1.0;
                window.speechSynthesis.speak(msg);
            </script>
        """, height=0)

# --- İLETİŞİM BÖLÜMÜ ---
st.divider()
with st.expander("📬 İletişim ve Geri Bildirim"):
    st.write("Bir sorunuz mu var veya yeni bir fikir mi paylaşmak istiyorsunuz?")
    st.write("Aşağıdaki e-posta adresinden bize ulaşabilirsiniz:")
    st.code("iletisim.orionai@gmail.com", language="text")
    st.caption("Fikirleriniz projemizin gelişimi için değerlidir!")

st.caption("Geliştirici: Ege - Bursa Bilim Şenliği Protokolü")
