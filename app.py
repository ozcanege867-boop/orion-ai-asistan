import pyttsx3
import speech_recognition as sr
import wikipedia
from googletrans import Translator
from datetime import datetime
import pytz  
import time

# --- AYARLAR VE BAŞLANGIÇ ---
translator = Translator()
wikipedia.set_lang("tr")

# --- ÇEVRİMDIŞI HAFIZA (KİMLİK VE SOHBET) ---
OFFLINE_KNOWLEDGE = {
    "sen kimsin": "Ben ORION, Bursa Bilim Şenliği için özel olarak geliştirilmiş, Türkçe anlayan ve İngilizce yanıt veren bir yapay zeka asistanıyım.",
    "hakkında bilgi ver": "Ben ORION; ismimi avcı takımyıldızından alıyorum. Görevim, kullanıcılara bilgi sunmak ve dil öğrenimlerine yardımcı olmaktır.",
    "kendinden bahset": "Ben bir yapay zeka protokolüyüm. Python diliyle programlandım ve ansiklopedik bilgilere ulaşabiliyorum.",
    "adın ne": "Adım ORION.",
    "nasılsın": "Tüm fonksiyonlarım yüzde yüz kapasiteyle çalışıyor, sorduğunuz için teşekkür ederim.",
    "merhaba": "Merhaba efendim, sizi dinliyorum.",
    "selam": "Selamlar, emrinizdeyim."
}

# --- DÜNYA SAATLERİ VERİTABANI ---
DUNYA_SAATLERI = {
    "londra": "Europe/London",
    "tokyo": "Asia/Tokyo",
    "pekin": "Asia/Shanghai",
    "new york": "America/New_York",
    "berlin": "Europe/Berlin",
    "moskova": "Europe/Moscow",
    "paris": "Europe/Paris",
    "baku": "Asia/Baku",
    "bakü": "Asia/Baku",
    "sidney": "Australia/Sydney"
}

# ---TIBBİ BELİRTİ VE HASTALIK VERİTABANI ---
TIBBI_BILGI = {
    "baş ağrısı": "Baş ağrısı; stres, migren, susuzluk veya tansiyon kaynaklı olabilir. Bol su için ve karanlık bir ortamda dinlenin.",
    "ateş": "Yüksek ateş enfeksiyon belirtisi olabilir. 38 derecenin üzerindeyse ve düşmüyorsa mutlaka bir doktora görünmelisiniz.",
    "mide bulantısı": "Mide bulantısı; gıda zehirlenmesi, gastrit veya vertigodan kaynaklanabilir. Ağır yiyeceklerden kaçının.",
    "öksürük": "Öksürük; soğuk algınlığı, alerji veya bronşit belirtisi olabilir. Uzun sürerse ciğerlerinizi kontrol ettirmelisiniz.",
    "halsizlik": "Halsizlik; vitamin eksikliği, kansızlık veya depresyon kaynaklı olabilir. Kan değerlerinize baktırmanız önerilir.",
    "grip": "Grip, viral bir enfeksiyondur. Dinlenmek, bol sıvı tüketmek ve C vitamini almak iyileşmeyi hızlandırır."
}

def get_engine():
    """Ses motorunu her seferinde tazeleyerek ERKEK sesini seçer."""
    new_engine = pyttsx3.init()
    voices = new_engine.getProperty('voices')
    
    target_id = None
    for voice in voices:
        # Microsoft David veya 'Male' etiketi ara
        if "David" in voice.name or "Male" in voice.name:
            target_id = voice.id
            break
    
    if not target_id and len(voices) > 0:
        target_id = voices[0].id

    if target_id:
        new_engine.setProperty('voice', target_id)
    
    new_engine.setProperty('rate', 175) # Konuşma hızı
    return new_engine

def speak_orion(tr_text):
    """Ekrana Türkçe yazar, Sesi İngilizce okur."""
    if not tr_text: return
    
    print(f"\n[ORION TR]: {tr_text}")
    
    try:
        # Seslendirme için İngilizceye çevir
        translation = translator.translate(tr_text, src='tr', dest='en')
        eng_text = translation.text
        print(f"[ORION EN - Voice]: {eng_text}")
        
        # İngilizce Seslendir
        temp_engine = get_engine()
        temp_engine.say(eng_text)
        temp_engine.runAndWait()
        temp_engine.stop()
        
    except Exception as e:
        print(f"Seslendirme Hatası: {e}")

def calculate(query):
    """Matematik işlemlerini yakalar."""
    q = query.replace("artı", "+").replace("eksi", "-").replace("çarpı", "*").replace("bölü", "/")
    q = q.replace("x", "*").replace("kere", "*").replace(",", ".").replace("kaç eder", "").replace("kaçtır", "")
    
    # Sadece sayı ve işlem karakterlerini filtrele
    temiz_islem = "".join([c for c in q if c.isdigit() or c in "+-*/."])
    
    if len(temiz_islem) >= 3:
        try:
            sonuc = eval(temiz_islem)
            return f"{temiz_islem} işleminin sonucu: {sonuc}"
        except:
            return None
    return None

def clean_search_query(query):
    """Wikipedia araması için gereksiz kelimeleri temizler."""
    durak_kelimeler = [
        "nedir", "kimdir", "nelerdir", "neredir", "ne zaman", "hangi yıl", 
        "hangi yılda", "kaç yılında", "tarihinde", "hakkında bilgi", 
        "bana anlat", "özellikleri", "yapıldı", "doğdu", "öldü", "ver"
    ]
    temiz_sorgu = query.lower()
    for kelime in durak_kelimeler:
        temiz_sorgu = temiz_sorgu.replace(kelime, "")
    return temiz_sorgu.strip()

def get_answer(query):
    q_lower = query.lower().strip()
    
    # 1. MATEMATİK ÖNCELİĞİ
    math_res = calculate(q_lower)
    if math_res:
        return math_res

    # 2. YENİ EKLENEN: DÜNYA SAATLERİ KONTROLÜ
    if "saat" in q_lower:
        for sehir, zaman_dilimi in DUNYA_SAATLERI.items():
            if sehir in q_lower:
                try:
                    tz = pytz.timezone(zaman_dilimi)
                    sehir_saati = datetime.now(tz).strftime("%H:%M")
                    return f"{sehir.capitalize()} şehrinde şu an saat {sehir_saati}"
                except:
                    pass

    # 3. YENİ EKLENEN: BELİRTİ VE HASTALIK KONTROLÜ (TIP MODÜLÜ)
    for belirti, aciklama in TIBBI_BILGI.items():
        if belirti in q_lower:
            return f"Tespit edilen durum: {belirti}. {aciklama} (Not: Ben bir yapay zekayım, kesin teşhis için doktora gidin.)"

    # 4. ÖZEL KİMLİK SORGUSU
    if q_lower in ["hakkında bilgi ver", "kendinden bahset", "kimsin", "sen kimsin"]:
        return OFFLINE_KNOWLEDGE["hakkında bilgi ver"]

    # 5. SİSTEM FONKSİYONLARI (Yerel Saat)
    if "saat kaç" in q_lower:
        return f"Şu an yerel saat {datetime.now().strftime('%H:%M')}"
    if "günlerden ne" in q_lower or "tarih" in q_lower:
        return datetime.now().strftime("Bugün tarih %d.%m.%Y")

    # 6. ÇEVRİMDIŞI HAFIZA TARAMASI
    for key in OFFLINE_KNOWLEDGE:
        if key == q_lower:
            return OFFLINE_KNOWLEDGE[key]

    # 7. WIKIPEDIA (Dış Dünya Bilgisi)
    arama_terimi = clean_search_query(q_lower)
    
    if len(arama_terimi) < 2:
        return "Sizi tam anlayamadım, lütfen biraz daha detay verir misiniz?"

    try:
        # 2 cümlelik özet getir
        return wikipedia.summary(arama_terimi, sentences=2)
    except wikipedia.exceptions.DisambiguationError as e:
        return f"Bu konu çok genel. {e.options[0]} hakkında mı bilgi istiyorsunuz?"
    except:
        return "Üzgünüm, bu konuyla ilgili net bir bilgiye ulaşamadım."

def start_system():
    recognizer = sr.Recognizer()
    speak_orion("Sistem açık. Tıp ve Dünya Saatleri modülleri eklendi. Emrinizdeyim.")

    while True:
        with sr.Microphone() as source:
            try:
                print("\nDinliyorum...")
                recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = recognizer.listen(source, timeout=10, phrase_time_limit=6)
                
                command = recognizer.recognize_google(audio, language="tr-TR").lower()
                print(f"Siz: {command}")

                if "görüşürüz" in command or "kapat" in command:
                    speak_orion("Sistem kapatılıyor. İyi günler efendim.")
                    break
                elif "orion" in command and len(command) < 8:
                    speak_orion("Buradayım efendim.")
                else:
                    cevap = get_answer(command)
                    speak_orion(cevap)

            except sr.UnknownValueError:
                continue
            except Exception as e:
                print(f"Hata oluştu: {e}")

if __name__ == "__main__":
    start_system()
