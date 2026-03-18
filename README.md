# 🏫 DDK - Dijital Dilek Kutusu

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white)
![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white)
![CSS3](https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=css3&logoColor=white)

**18. Uluslararası MEB Robot Yarışması - Serbest Proje Kategorisi**

DDK (Dijital Dilek Kutusu), okullardaki fiziksel dilek ve şikayet kutularının işlevsizliğini ortadan kaldırmak amacıyla geliştirilmiş, web tabanlı ve otonom bir iletişim ağıdır. Sistem, öğrencilerin taleplerini anonim olarak toplayıp oylamaya sunarken; içerdiği algoritmik filtreler ve disiplin motoru sayesinde okul idaresinin iş yükünü minimize eder.

## ✨ Öne Çıkan Özellikler

* **🤖 Algoritmik Spam ve Küfür Filtresi:** Python Regex (Düzenli İfadeler) kullanılarak geliştirilen filtre, anlamsız tuşlamaları (spam) ve uygunsuz kelimeleri saniyeler içinde tespit edip "Denetim" havuzuna gönderir.
* **⏳ Otonom Hafta Döngüsü:** Sistem zamanın farkındadır. Cumartesi günleri en çok beğenilen 3 istek ile bir anket oluşturur. Pazar günleri veri girişini otonom olarak durdurur, anketin kazananını "Haftanın Kazananı" ilan eder ve yeni hafta için akışı otomatik sıfırlar.
* **🛡️ Gelişmiş Disiplin Modülü:** Şifreli yetkili paneli üzerinden idareciler, kuralları ihlal eden öğrencilere "Uyarı" (haftalık susturma ve mevcut iletileri silme) verebilir veya "Ban" (sistemden kalıcı uzaklaştırma) uygulayabilir.
* **⚡ Şemasız (Schema-less) Veritabanı:** Yüksek sistem kaynağı tüketen SQL mimarileri yerine, hızlı G/Ç (I/O) imkanı sunan ve yerel ağlarda (Intranet) kusursuz çalışan **JSON** dosya mimarisi kullanılmıştır.
* **📱 Modern ve Duyarlı Arayüz:** Saf HTML5 ve CSS3 ile geliştirilmiş, Karanlık Tema (Dark Mode) ağırlıklı, sosyal medya dinamiklerine sahip Z kuşağı dostu kullanıcı deneyimi.

## 🚀 Kurulum ve Çalıştırma

Projeyi yerel makinenizde (localhost) çalıştırmak için aşağıdaki adımları izleyebilirsiniz:

1. Bu depoyu bilgisayarınıza klonlayın:
   ```bash
   git clone https://github.com/burkyahyuzn/ddk-dijital-dilek-kutusu.git
   ```
2. Gerekli kütüphaneyi (Flask) kurun:
   ```bash
   pip install flask
   ```
3. Uygulamayı başlatın:
   ```bash
   python app.py
   ```
4. Tarayıcınızda `http://127.0.0.1:5000` adresine giderek sistemi kullanmaya başlayabilirsiniz.

## 🔐 Varsayılan Giriş Bilgileri

Sistemi test etmek için ön tanımlı JSON veritabanında bulunan şu bilgileri kullanabilirsiniz:

* **Öğrenci Girişi:** TC: `111` | Okul No: `200`
* **Yetkili Girişi:** TC: `11` | Erişim Şifresi: `1234`

## 📁 Proje Klasör Yapısı

```text
DDK/
│
├── data/                  # JSON Veritabanı Dosyaları
│   ├── gonderiler.json    # Tüm iletilerin tutulduğu tablo
│   ├── kazanan.json       # Otonom seçilen şampiyonlar
│   ├── ogrenciler.json    # Öğrenci listesi, ban ve uyarı durumları
│   ├── uygunsuz.json      # Dinamik kara liste kelime havuzu
│   └── yetkililer.json    # İdari personel listesi
│
├── static/                # Statik Dosyalar
│   └── style.css          # Genel tasarım kodları
│
├── templates/             # HTML Şablonları (Jinja2)
│   ├── akis.html          # Ana sayfa ve dilek akışı
│   ├── anket.html         # Oylama ekranı
│   ├── base.html          # Sistem ana iskeleti
│   ├── denetimler.html    # Filtreye takılanların düştüğü havuz
│   ├── giris.html         # Login ekranı
│   ├── ogrenciler.html    # Disiplin paneli (Uyarı/Ban)
│   ├── profil.html        # Kullanıcı geçmişi
│   └── trendler.html      # En çok beğeni alanlar
│
└── app.py                 # Backend & Rota (Route) Yöneticisi
```

## 👥 Proje Ekibi

* **Burak Yahya UZUN** - Yazılım ve Algoritma Mimarı
* **Yusuf Kaan YAVUZ** - Sistem Analisti ve Test Uzmanı

*Keşap Fen Lisesi adına 18. Uluslararası MEB Robot Yarışması için geliştirilmiştir.*
