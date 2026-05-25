# Otonom İHA-İKA Operasyon, Haritalandırma ve Taktiksel Navigasyon Sistemi

Bu proje; İnsansız Hava Araçları (UAV) ve İnsansız Kara Araçlarının (UGV) senkronize çalışmasını sağlayan uçtan uca otonom bir taktiksel operasyon sistemidir. Sistem; derin öğrenme tabanlı nesne segmentasyonu , panoramik haritalandırma , Gazebo SITL uçuş kontrolü , uzun menzilli LoRa M2M haberleşmesi , koordinat tabanlı robotik navigasyon ve klasik bilgisayarlı görü ile şerit takibi  algoritmalarını tek bir çatı altında birleştirir.


## 📂 Proje Dosya Yapısı (Directory Tree)

```text
├── 📁 AutonomousTaskCodes
│   ├── 📁 images                       # Video akışından yakalanan ham fotoğraflar
│   ├── 📄 Autonomous_task_codes.ipynb  # Algoritma prototip ve AR-GE defteri
│   ├── 📄 Frame_capture.py             # İHA videosundan dinamik kare yakalama scripti
│   ├── 📄 Images_merge.py              # Çoklu ardışık görüntü birleştirme (Panorama)
│   ├── 📄 best.pt                      # Eğitilmiş YOLOv8 Segmentasyon model ağırlığı
│   ├── 📄 image1.jpg / image2.jpg      # Test amaçlı girdi fotoğrafları
│   ├── 📄 map.png                      # YOLO modeline girecek birleştirilmiş ana harita
│   ├── 📄 merged_image.jpg             # İşlem sonu üretilen panoramik çıktı haritası
│   └── 📄 video.mp4                    # İHA alt kamera uçuş videosu
│
├── 📁 LoRa
│   ├── 📄 Receiver_UGV.py              # Kara aracında bulunan LoRa dinleyici ve komut yürütücü
│   └── 📄 Sender_UAV.py                # İHA tarafındaki LoRa sürücüsü ve komut gönderici
│
├── 📁 UAVCodes
│   ├── 📁 standard_vtol                # Gazebo simülatörü için VTOL hava aracı fiziksel modeli
│   └── 📄 Autonomous_flying.py         # MAVSDK tabanlı asenkron otonom uçuş kontrol kodu
│
└── 📁 UGVCodes
    ├── 📄 Lane_Detection_and_Tracking.py # OpenCV tabanlı gerçek zamanlı şerit takip sistemi
    ├── 📄 Road1.mp4                    # Şerit takip algoritması test videosu
    ├── 📄 received_data.txt            # LoRa üzerinden İHA'dan gelen anlık koordinat kayıtları
    └── 📄 ugv_commands_code.py         # Koordinat tabanlı otonom sürüş ve motor kontrol sistemi
```
  
🛠️ ## Modüler Teknik Mimari
### 1.Hava Analizi & Taktiksel Haritalandırma (AutonomousTaskCodes)
**Frame_capture.py:** İHA alt kamera videosundan (video.mp4) seconds_between_frames = 3 parametresiyle kareleri yakalar. Hızlı ileri sarma (CAP_PROP_POS_FRAMES) özelliğiyle büyük video dosyalarında performansı artırır, görüntüleri işlem optimizasyonu için 640x480 çözünürlüğünde standartlaştırır.

**Images_merge.py:** Sıralı kareleri ORB öznitelik algılayıcı ve RANSAC tabanlı Homografi matrisi kullanarak zincirleme şekilde birleştirir. Katmanlı bindirme ve otomatik kırpma uygulayarak geniş araziler için kayıpsız bir panoramik harita (merged_image.jpg) üretir.

**Autonomous_task_codes.ipynb - YOLO Segmentasyon & Akıllı Rota (A Star):** Üretilen haritayı Yol (0), Engel (1), Dost (2), Düşman (3) olarak sınıflandırır. 50 piksel yarıçapında dostların etrafına güvenli koridor, düşmanların etrafına risk bariyerleri tanımlar. Haritayı 4 kat küçülterek dinamik maliyet fonksiyonlu A* algoritmasıyla en güvenli taktiksel rotayı çizer.

### 2.Havadan Karaya Kablosuz Komut Linki (LoRa)
**Sender_UAV.py:** İHA üzerindeki Raspberry Pi 4B ve SX126X LoRa donanımını kontrol eder. GPIO 22 (M0) ve GPIO 27 (M1) pinleriyle mod yönetimini gerçekleştirerek taktiksel rotayı ve otonom tetikleme komutunu 22dBm (160 mW) yüksek güçle 868 MHz bandından yayınlar. get_channel_rssi ile ortam gürültü tabanını (Noise RSSI) anlık ölçer.

**Receiver_UGV.py:** Kara aracında (UGV) konumlanan alıcı modüldür. İHA'dan gelen RUN_UGV_COMMANDS_CODE_PY tetiğini yakaladığı an alt süreç (subprocess.run) başlatarak yerdeki otonom navigasyon kodunu tetikler ve telemetri durumunu LoRa üzerinden geri raporlar.

### 3. Simülasyon & Hava Seyrüseferi (UAVCodes)
**Autonomous_flying.py:** MAVSDK kütüphanesi kullanarak asyncio (asenkron) mimaride Gazebo SITL simülasyonundaki İHA'yı kontrol eder. GPS sağlığı, otomatik kalkış, 10 metrelik irtifa takibi, çoklu görev kontrol noktası (waypoint) yönetimi ve dikey kalkıştan sabit kanat (Fixed-Wing) moduna dinamik geçiş testlerini yürütür.

**standard_vtol:** Hava aracının kanat açıklığı, kaldırma ve sürüklenmesi gibi aerodinamik katsayılarını ve motor eklentilerinin otopilot (PX4) ile eşleşmesini içeren fiziksel simülasyon gövde modelidir.

### 4. Kara Aracı Navigasyon & Kontrol (UGVCodes)
**Lane_Detection_and_Tracking.py:** Klasik görüntü işleme teknikleriyle (Gaussian Blur, Canny Edge, ROI maskeleme ve Hough Transform) yol şeritlerini gerçek zamanlı filtreler, algılar ve robotik navigasyon için temel şerit takip altyapısını oluşturur.

**ugv_commands_code.py:** LoRa üzerinden received_data.txt dosyasına gelen rota koordinatlarını sırasıyla okur. Dinamik yön analiziyle (Kuzey, Güney, Doğu, Batı) robotun hareket kararlarını (İleri, Geri, Sola Dönüş, Sağa Dönüş, Dur) üretir. 4 adet DC motoru kararlı şekilde sürmek için PWM (Sinyal Genişlik Modülasyonu) hız kontrolünü kullanır.

## ⚙️ Donanım / Motor Sürücü Pin Şeması (UGV)
Kara aracı üzerinde yer alan 4 adet DC motorun fiziksel konumları ve kontrol pin yapısı modüler olarak tasarlanmıştır:

| Motor | Konum | Kullanılan Pin Hatları |
| :--- | :--- | :--- |
| **M1** | Ön Sol | IN1, IN2, EN (PWM) |
| **M2** | Ön Sağ | IN1, IN2, EN (PWM) |
| **M3** | Arka Sol | IN1, IN2, EN (PWM) |
| **M4** | Arka Sağ | IN1, IN2, EN (PWM) |

## 🛡️ Güvenlik ve Hata Yönetimi
Sistem, gömülü donanım süreçlerinin ve veri akışlarının kararlılığı için şu koruma mekanizmalarını barındırır:

**Güvenli GPIO Temizliği:** Program herhangi bir sebeple sonlandığında, motorların kontrolsüz dönmesini engellemek için Raspberry Pi GPIO pinleri otomatik olarak temizlenir ve güvenli moda alınır.

**Haberleşme Zaman Aşımı (Timeout):** Kara aracında 70 saniye boyunca (TIMEOUT_SECONDS = 70) LoRa veri akışı kesilirse, sistem batarya ve donanım sağlığını korumak için kendini otomatik olarak kapatır.

**İstisna ve Dosya Denetimi:** Gelişmiş runtime exception, dosya okuma ve PWM hata yönetimi mimarisi ile donanım çökmelerinin önüne geçilir.

## 💻 Kurulum ve Çalıştırma
### 1. Gereksinimlerin Yüklenmesi
Sistem için gerekli olan Python 3.8+ bağımlılıklarını yükleyin:

```bash
pip install opencv-python numpy ultralytics cvzone mavsdk
```
### 2. Simülasyon Çevre Değişkeni
Gazebo simülatörünün hibrit VTOL modelini tanıyabilmesi için terminale ilgili yolu tanımlayın:

```bash
export GAZEBO_MODEL_PATH=$GAZEBO_MODEL_PATH:/path/to/your/repo/UAVCodes/standard_vtol
```

### 3. Operasyon Adımları
**Haritalandırma:** AutonomousTaskCodes içindeki kodlarla video akışından kare yakalayıp panoramik haritanızı oluşturun.

**Hava Simülasyonu:** Gazebo SITL/PX4 simülasyonunu başlatarak UAVCodes/Autonomous_flying.py uçuş görevini tetikleyin.

**Kara Sürüşü:** Kara aracında Receiver_UGV.py dinlemedeyken, İHA'dan gelen rota koordinatları ve otonom tetikleme komutuyla ugv_commands_code.py üzerinden aracı otonom olarak sürün.
