import base64
import glob
import json
import os
import webbrowser
from threading import Timer
import google.generativeai as genai
import pandas as pd
from flask import (
    Flask,
    jsonify,
    render_template,
    request,
    send_from_directory,
)
from PIL import Image

# ==========================================
# GEMINI API AYARI
# ==========================================
API_KEY = os.getenv(
    "GEMINI_API_KEY", "your_api_key_here"  # Ortam değişkeni yoksa buraya kendi API anahtarınızı yazın
)
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-3.6-flash")

# ==========================================
# GÜVENLİ KLASÖR AYARLARI
# ==========================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

FRAMES_FOLDER = os.path.join(BASE_DIR, "product_frames")
RESULTS_FOLDER = os.path.join(BASE_DIR, "product_results")
SAMPLE_VIDEO_PATH = os.path.join(BASE_DIR, "sample_ad.mp4")

os.makedirs(FRAMES_FOLDER, exist_ok=True)
os.makedirs(RESULTS_FOLDER, exist_ok=True)

app = Flask(__name__, template_folder=BASE_DIR)

session_results = []

# TOPLU (BATCH) ÇIKARIM PROMPT'U
BATCH_UX_PROMPT = """
Sen kıdemli bir Tüketici Nöromarketing Araştırmacısı ve Büyüme Odaklı Pazarlama (Growth & Brand Marketing) Stratejistisisin.
Sana tüketicinin 10 saniyelik bir reklam/ürün videosunu izlerken 2 saniyede bir çekilmiş kamera kareleri sırasıyla verildi.
(Görseller sırasıyla: 2., 4., 6., 8. ve 10. saniyelerdir).

Kullanıcının yüz kaslarını (FACS), göz fiksasyonunu ve zaman içindeki mikro mimik değişim trendini Russell'ın Çevresel Duygu Modeli ile Tüketici Davranışı & Reklam Dönüşüm Hunisi (AIDA) prensiplerini harmanlayarak analiz et.

SADECE ve SADECE her bir kareye karşılık gelen nesneleri içeren, aşağıdaki şemaya uygun bir JSON DİZİSİ (Array) üret:

[
  {
    "second": 2,
    "affective_core": {
      "dominant_emotion": "hayranlik | merak_ilgi | noetral | kafa_karisikligi | suphe | can_sikintisi | hayal_kirikligi | hosnutsuzluk",
      "valence_score": -1.0 ile 1.0 arasında ondalıklı sayı,
      "arousal_score": -1.0 ile 1.0 arasında ondalıklı sayı
    },
    "marketing_funnel": {
      "aida_stage": "farkindalik | ilgi | arzu | eyleme_gecis | terk_etme",
      "brand_receptivity": "pozitif_baglanti | supheli_yaklasim | ilgisiz | tepkisel_reddetme",
      "cta_readiness": "hazir | kararsiz | erken | direncli"
    },
    "commercial_signals": {
      "purchase_intent": "cok_yuksek | yuksek | orta | dusuk | negatif",
      "perceived_value_friction": "Fiyat şüphesi | Güven sorunu | Karmaşık teklif | Yok",
      "micro_expressions": ["mimik1", "mimik2"]
    },
    "marketing_actionable_insight": {
      "scene_verdict": "Sahnenin kullanıcı zihninde yarattığı etki",
      "cro_recommendation": "Dönüşümü artırmak için 1 cümlelik pazarlama aksiyonu"
    }
  }
]
"""


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/video/<path:filename>")
def serve_video(filename):
    return send_from_directory(BASE_DIR, filename)


@app.route("/reset", methods=["POST"])
def reset():
    global session_results
    session_results = []
    for folder in [FRAMES_FOLDER, RESULTS_FOLDER]:
        os.makedirs(folder, exist_ok=True)
        for file in os.listdir(folder):
            path = os.path.join(folder, file)
            if os.path.isfile(path):
                try:
                    os.remove(path)
                except PermissionError:
                    pass
    print("✓ Oturum ve önceki test kareleri temizlendi.")
    return jsonify({"status": "cleared"})


# 2 saniyede bir gelen kareyi kaydeder
@app.route("/upload_frame", methods=["POST"])
def upload_frame():
    try:
        data = request.get_json(force=True)
        second = int(data.get("second", 0))
        image_raw = data.get("image", "")

        if not image_raw or "," not in image_raw:
            return jsonify({"error": "Geçersiz görsel formatı"}), 400

        image_bytes = base64.b64decode(image_raw.split(",")[1])
        frame_path = os.path.join(FRAMES_FOLDER, f"frame_{second:02d}.jpg")
        with open(frame_path, "wb") as f:
            f.write(image_bytes)

        print(f"✓ [{second}. sn] Kare diske yazıldı -> {frame_path}")
        return jsonify({"status": "saved", "second": second})
    except Exception as e:
        print(f"✗ Kare kaydetme hatası: {e}")
        return jsonify({"error": str(e)}), 500


# Test bittiğinde TÜM KARELERİ TEK İSTEKTE GEMINI'A GÖNDERİR
@app.route("/finalize_and_analyze", methods=["POST"])
def finalize_and_analyze():
    global session_results
    session_results = []

    saved_frames = sorted(glob.glob(os.path.join(FRAMES_FOLDER, "frame_*.jpg")))

    if not saved_frames:
        return jsonify({"error": "Hiçbir kare yakalanamadı"}), 400

    print(f"\n--> {len(saved_frames)} adet kare tek istekte Gemini multimodal API'ye gönderiliyor...")

    images_payload = []
    for f_path in saved_frames:
        with Image.open(f_path) as pil_img:
            images_payload.append(pil_img.copy())

    try:
        # Tek seferde tüm görseller + prompt
        response = model.generate_content(
            [*images_payload, BATCH_UX_PROMPT],
            generation_config={"response_mime_type": "application/json"},
        )

        session_results = json.loads(response.text)

        # Eğer model dizi yerine tek bir nesne dönerse listeye sar
        if isinstance(session_results, dict):
            session_results = [session_results]

        print(f"✓ Gemini toplu çıkarımı başarılı! Toplam {len(session_results)} an analiz edildi.")

    except Exception as e:
        print(f"✗ Toplu analiz hatası: {e}")
        return jsonify({"error": str(e)}), 500

    # Toplu JSON ve CSV kaydı
    json_path = os.path.join(RESULTS_FOLDER, "product_ux_results.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(session_results, f, ensure_ascii=False, indent=2)

    flattened = []
    for r in session_results:
        flattened.append({
            "second": r.get("second"),
            "dominant_emotion": r.get("affective_core", {}).get("dominant_emotion"),
            "valence": r.get("affective_core", {}).get("valence_score"),
            "arousal": r.get("affective_core", {}).get("arousal_score"),
            "aida_stage": r.get("marketing_funnel", {}).get("aida_stage"),
            "brand_receptivity": r.get("marketing_funnel", {}).get("brand_receptivity"),
            "purchase_intent": r.get("commercial_signals", {}).get("purchase_intent"),
            "friction": r.get("commercial_signals", {}).get("perceived_value_friction"),
            "cta_readiness": r.get("marketing_funnel", {}).get("cta_readiness"),
            "scene_verdict": r.get("marketing_actionable_insight", {}).get("scene_verdict"),
            "cro_recommendation": r.get("marketing_actionable_insight", {}).get("cro_recommendation"),
        })

    csv_path = os.path.join(RESULTS_FOLDER, "product_ux_results.csv")
    pd.DataFrame(flattened).to_csv(csv_path, index=False, encoding="utf-8")

    print(f"✓ Raporlar kaydedildi: {csv_path}")

    return jsonify({"status": "completed", "results": session_results})


if __name__ == "__main__":
    Timer(1.2, lambda: webbrowser.open("http://127.0.0.1:5000")).start()
    app.run(debug=False, port=5000)