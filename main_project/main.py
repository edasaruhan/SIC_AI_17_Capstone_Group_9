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
    "GEMINI_API_KEY", "your api key"  
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

CLICKS_JSON_PATH = os.path.join(RESULTS_FOLDER, "click_events.json")
CLICKS_CSV_PATH = os.path.join(RESULTS_FOLDER, "click_events.csv")

os.makedirs(FRAMES_FOLDER, exist_ok=True)
os.makedirs(RESULTS_FOLDER, exist_ok=True)

app = Flask(__name__, template_folder=BASE_DIR)

session_results = []
click_events = []

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
    global session_results, click_events

    session_results = []
    click_events = []
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

@app.route("/upload_click", methods=["POST"])
def upload_click():
    global click_events

    try:
        data = request.get_json(force=True)

        video_time = float(data.get("video_time", 0))
        x = float(data.get("x", 0))
        y = float(data.get("y", 0))
        x_norm = float(data.get("x_norm", 0))
        y_norm = float(data.get("y_norm", 0))

        click = {
            "video_time": round(video_time, 3),
            "x": round(x, 1),
            "y": round(y, 1),
            "x_norm": round(x_norm, 4),
            "y_norm": round(y_norm, 4)
        }

        click_events.append(click)

        # JSON olarak kaydet
        with open(CLICKS_JSON_PATH, "w", encoding="utf-8") as f:
            json.dump(click_events, f, ensure_ascii=False, indent=2)

        # CSV olarak da kaydet
        pd.DataFrame(click_events).to_csv(
            CLICKS_CSV_PATH,
            index=False,
            encoding="utf-8"
        )

        print(
            f"✓ Tıklama kaydedildi | "
            f"Video: {video_time:.2f}s | "
            f"X: {x:.1f} | Y: {y:.1f}"
        )

        return jsonify({
            "status": "saved",
            "click": click
        })

    except Exception as e:
        print(f"✗ Tıklama kaydetme hatası: {e}")
        return jsonify({"error": str(e)}), 500

def merge_clicks_with_emotions(results, clicks):
    """
    Click verilerini emotion sonuçlarıyla zaman aralığına göre eşleştirir.

    0-2 saniye  -> 2. saniye emotion
    2-4 saniye  -> 4. saniye emotion
    4-6 saniye  -> 6. saniye emotion
    6-8 saniye  -> 8. saniye emotion
    8-10 saniye -> 10. saniye emotion
    """

    for result in results:
        emotion_second = float(result.get("second", 0))

        matching_clicks = []

        for click in clicks:
            click_time = float(click.get("video_time", 0))

            if (emotion_second - 2) < click_time <= emotion_second:
                matching_clicks.append(click)

        result["interaction"] = {
            "click_count": len(matching_clicks),
            "clicks": matching_clicks
        }

    return results

# Test bittiğinde TÜM KARELERİ TEK İSTEKTE GEMINI'A GÖNDERİR
@app.route("/finalize_and_analyze", methods=["POST"])
def finalize_and_analyze():
    global session_results
    session_results = []

    saved_frames = sorted(
        glob.glob(os.path.join(FRAMES_FOLDER, "frame_*.jpg"))
    )

    if not saved_frames:
        return jsonify({"error": "Hiçbir kare yakalanamadı"}), 400

    print(
        f"\n--> {len(saved_frames)} adet kare tek istekte "
        f"Gemini multimodal API'ye gönderiliyor..."
    )

    images_payload = []

    for f_path in saved_frames:
        with Image.open(f_path) as pil_img:
            images_payload.append(pil_img.copy())

    try:
        # Gemini analizi
        response = model.generate_content(
            [*images_payload, BATCH_UX_PROMPT],
            generation_config={
                "response_mime_type": "application/json"
            },
        )
        print("\n===== GEMINI RAW RESPONSE =====")
        print(response.text)
        print("===== END GEMINI RAW RESPONSE =====\n")


        session_results = json.loads(response.text)

        # Gemini tek obje döndürürse listeye çevir
        if isinstance(session_results, dict):
            session_results = [session_results]

        # Click verilerini emotion sonuçlarıyla birleştir
        session_results = merge_clicks_with_emotions(
            session_results,
            click_events
        )

        print(
            f"✓ Gemini toplu çıkarımı başarılı! "
            f"Toplam {len(session_results)} an analiz edildi."
        )

    except Exception as e:
        print(f"✗ Toplu analiz hatası: {e}")

        return jsonify({
            "error": str(e),
            "clicks": click_events
        }), 500

    # ==========================================
    # JSON KAYDI
    # ==========================================

    json_path = os.path.join(
        RESULTS_FOLDER,
        "product_ux_results.json"
    )

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(
            session_results,
            f,
            ensure_ascii=False,
            indent=2
        )

    # ==========================================
    # EMOTION + CLICK CSV
    # ==========================================

    flattened = []

    for r in session_results:

        interaction = r.get("interaction", {})
        clicks = interaction.get("clicks", [])

        # Click koordinatlarını tek hücrede sakla
        click_coordinates = "; ".join(
            [
                f"({c.get('x')}, {c.get('y')})"
                for c in clicks
            ]
        )

        flattened.append({
            # Zaman
            "second": r.get("second"),

            # Emotion
            "dominant_emotion": r.get(
                "affective_core", {}
            ).get("dominant_emotion"),

            "valence": r.get(
                "affective_core", {}
            ).get("valence_score"),

            "arousal": r.get(
                "affective_core", {}
            ).get("arousal_score"),

            # Marketing
            "aida_stage": r.get(
                "marketing_funnel", {}
            ).get("aida_stage"),

            "brand_receptivity": r.get(
                "marketing_funnel", {}
            ).get("brand_receptivity"),

            "purchase_intent": r.get(
                "commercial_signals", {}
            ).get("purchase_intent"),

            "friction": r.get(
                "commercial_signals", {}
            ).get("perceived_value_friction"),

            "cta_readiness": r.get(
                "marketing_funnel", {}
            ).get("cta_readiness"),

            # Insight
            "scene_verdict": r.get(
                "marketing_actionable_insight", {}
            ).get("scene_verdict"),

            "cro_recommendation": r.get(
                "marketing_actionable_insight", {}
            ).get("cro_recommendation"),

            # Click / Interaction
            "click_count": interaction.get(
                "click_count", 0
            ),

            "click_coordinates": click_coordinates
        })

    # CSV dosyasını oluştur
    csv_path = os.path.join(
        RESULTS_FOLDER,
        "product_ux_results.csv"
    )

    pd.DataFrame(flattened).to_csv(
        csv_path,
        index=False,
        encoding="utf-8"
    )

    print(
        f"✓ Raporlar kaydedildi: {csv_path}"
    )

    return jsonify({
        "status": "completed",
        "results": session_results,
        "clicks": click_events
    })

if __name__ == "__main__":
    Timer(1.2, lambda: webbrowser.open("http://127.0.0.1:5000")).start()
    app.run(debug=False, port=5000)