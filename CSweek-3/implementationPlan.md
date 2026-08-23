1.Technology Stack
Programming Languages & Development Environments:
    Language: Python 3.10+
    IDEs & Notebooks: Visual Studio Code, Google Colab (GPU tabanlı model doğrulaması ve prototipleme için).
    Environment & Package Management: Virtualenv , Git & GitHub .

AI/ML Libraries, Frameworks & Model Platforms:
    Deep Learning Frameworks: TensorFlow / Keras, PyTorch.
    Computer Vision & Emotion Recognition: OpenCV (video işleme, frame yakalama ve çizim), DeepFace / Mediapipe (yüz tespiti ve duygu sınıflandırması) 
    ---eğer bu kütüphaneden istediğim doğruluk değerlerini alamamaya devam edersem kaggle üzerinden Emotion Image Pytorch Lightning CNN başlığı altındaki emotion-recognition-dataset veri setini kullanarak Pytorch ve Sklearn kullanarak çıktı almaya çalışacağım.---
    Machine Learning & Preprocessing: scikit-learn (metrik hesaplamaları ve veri ön işleme), NumPy (matris ve tensör işlemleri).

Data Processing, Storage, Analytics & Dashboard Tools:
    Data Handling & Analytics: Pandas (duygu logları ve zaman serisi analizi), NumPy.
    Visualization: Matplotlib, Seaborn (duygu dağılım grafikleri ve zaman serisi analitiği).
    Data Storage: SQLite / CSV / JSON (kare bazlı duygu skorları, zaman damgası ve metaverilerin kaydı).
    UI / Dashboard: Streamlit veya Gradio (video yükleme, gerçek zamanlı analiz izleme ve pazarlama KPI çıktısı görselleştirmesi için hafif web paneli).

Marketing Platforms, CRM Tools & Deployment Services:
    API & Deployment: FastAPI veya Flask (model servis katmanı).
    Marketing Simulation & Analytics Export: CSV/JSON API entegrasyonu (Google Analytics, HubSpot veya reklam panellerine duygu skorları ve etkileşim korelasyon metrikleri beslemek için analitik dışa aktarma katmanı). Video karelerinden elde edilen duygu dağılımları ve dikkat skorları, zaman damgalı (time-stamped) analitik loglara dönüştürülür. Bu katman, ürün özellikleri bazında katılımcı ilgisini eşleştirerek CSV/JSON formatında yapılandırılmış veri üretir. Üretilen çıktılar, yüksek ilgi gösteren katılımcıları sıcak müşteri adayı (Hot Lead) olarak sınıflandırmak üzere CRM (HubSpot) simülasyonlarına ve sunum optimizasyonu için ürün analitiği platformlarına entegre edilebilir veri akışı sağlar.

2.Timeline and Task Distribution 
Timeline projenin teslim haftasına kadar olan dört haftayı kapsamaktadır.
     WEEK  |          Stage                      | Key Tasks & Technical Focus |           
 -------------------------------------------------------------------------------
  Week 4   | Data Pipeline & Baseline AI Setup   |• OpenCV ile video stream ve dinamik frame yakalama/sampling altyapısının kurulması.
                                                 |• DeepFace / MediaPipe modelleri ile ilk çıkarım (inference) hattının oluşturulması.
                                                 |• Fallback planı: Çıkarım yetersiz kalırsa Kaggle emotion-recognition-dataset üzerinden PyTorch Lightning CNN mimarisinin eğitilip Colab üzerinde doğrulanması.
  Week 5   | Validation, Optimization & Export   |• Model performansının baseline (kural tabanlı/rastgele) ile kıyaslanması (Accuracy, F1-Score, Latency/FPS).
                                                 |• Zaman damgalı (timestamped) duygu ve dikkat verilerini toplayan Pandas/NumPy analitik log mekanizmasının kurulması.
                                                 |• CRM (HubSpot) ve analitik araçlara uygun JSON/CSV dışa aktarım şemasının kodlanması.
  Week 6   | UI Dashboard & Workflow Integration |• Streamlit / Gradio üzerinde interaktif ürün tanıtım panelinin geliştirilmesi.
                                                 |• Sunum zaman çizelgesi üzerindeki özellikler ile dikkat/duygu eğrilerinin eşleştirilmesi (Plotly/Matplotlib/Seaborn).
                                                 |• Model servis katmanının (FastAPI/Flask) UI ve analitik log modülü ile entegrasyonu.,Uçtan uca çalışan etkileşimli analiz paneli (Dashboard) ve görselleştirme modülü.
  Week 7   | Evaluation,Demo,Final Documentation |• Sanal ürün lansmanı senaryosu üzerinden end-end ve pazarlama KPI çıktılarının (Hot Lead, Engagement Index) doğrulanması.
                                                 |• Proje dokümantasyonunun (Concept Note & Implementation Plan) sonlandırılması.
                                                 |• GitHub reposunun düzenlenmesi, demo video kaydının alınması ve final sunumunun tamamlanması.

Task Distribution Matrix
Stage / Module                         | Primary Assignee | Detailed Responsibilities |
Computer Vision & Model Inference      | İrem Ç.          | OpenCV video akışı, kare atlama/örnekleme optimizasyonu, DeepFace entegrasyonu ve gerekirse PyTorch Lightning CNN   yedek modelinin geliştirilmesi.
Model Validation & Baseline Comparison | Meryem M.        | Test video senaryoları üzerinde çıkarım hızı (FPS/gecikme) ve duygu sınıflandırma metriklerinin (Sklearn ile F1/Accuracy) hesaplanıp baseline ile karşılaştırılması.
Marketing Data & Export Layer          | İrem Ç.          | Zaman damgalı logların tutulması, dikkat skoru algoritmaları ve HubSpot/Google Analytics formatına uygun JSON/CSV export katmanının kodlanması.
UI Dashboard & Visualization           |   Meryem & İrem  | Streamlit/Gradio paneli, Plotly/Seaborn zaman serisi duygu grafikleri ve tanıtım aşamalarını gösteren etkileşimli kullanıcı deneyiminin inşası.
Integration & Service Layer            |   Meryem & İrem  | FastAPI/Flask servis katmanı üzerinden AI modeli ile UI/veri tabanının (SQLite/JSON) uçtan uca bağlanması.Documentation, Demo & PresentationJoint|   Meryem & İrem  | Concept Note, Implementation Plan, GitHub reposu yönetimi, demo videosunun çekilmesi ve nihai sunum slaytlarının hazırlanması.

3.Milestones and Deliverables
    ![Açıklama][mileston.png]

4.Risk
![Açıklama](resim.png)

[resim.png]: mileston.png