from flask import Flask, render_template, request, redirect, url_for, session, flash
import json
import os
import re
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'ddk_proje_gizli_anahtar_mebrobot_2026'
YETKILI_SIFRESI = "1234"

def veri_oku(dosya_adi):
    yol = os.path.join("data", dosya_adi)
    if not os.path.exists(yol):
        return []
    try:
        with open(yol, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return []

def veri_yaz(dosya_adi, veri):
    if not os.path.exists("data"):
        os.makedirs("data")
    yol = os.path.join("data", dosya_adi)
    with open(yol, 'w', encoding='utf-8') as f:
        json.dump(veri, f, ensure_ascii=False, indent=4)

def bu_haftanin_numarasi():
    return datetime.now().isocalendar()[1]

def bugun_gunlerden_ne():
    return datetime.now().weekday()

def spam_mi(metin):
    metin = metin.lower()
    sesliler = r'[aeıioöuü]{4,}'
    sessizler = r'[bcçdfgğhjklmnprsştvyzqwx]{4,}'
    if re.search(sesliler, metin) or re.search(sessizler, metin):
        return True
    return False

@app.before_request
def pazar_temizligi():
    if bugun_gunlerden_ne() == 6:
        gonderiler = veri_oku('gonderiler.json')
        if len(gonderiler) > 0:
            onaylilar = [p for p in gonderiler if p.get('tur') == 'ogrenci' and p.get('durum') == 'yayinda']
            if onaylilar:
                kazanan = max(onaylilar, key=lambda x: len(x.get('begenenler', [])))
                veri_yaz('kazanan.json', [kazanan])
            veri_yaz('gonderiler.json', [])

@app.context_processor
def inject_globals():
    kazananlar = veri_oku('kazanan.json')
    kzn = kazananlar[0] if len(kazananlar) > 0 else None
    return dict(global_kazanan=kzn, bugun=bugun_gunlerden_ne())

@app.route('/', methods=['GET', 'POST'])
def giris():
    if 'kullanici' in session:
        return redirect(url_for('akis'))

    if request.method == 'POST':
        tip = request.form.get('tip')
        tc = request.form.get('tc')

        if tip == 'ogrenci':
            numara = request.form.get('numara')
            ogrenciler = veri_oku('ogrenciler.json')
            for ogr in ogrenciler:
                if str(ogr.get('tc')) == str(tc) and str(ogr.get('numara')) == str(numara):
                    if ogr.get('banned') == True:
                        flash("Hesabınız yetkililer tarafından kalıcı olarak banlanmıştır!", "hata")
                        return redirect(url_for('giris'))
                    
                    session['kullanici'] = ogr.get('isim')
                    session['rol'] = 'ogrenci'
                    session['tc'] = tc
                    return redirect(url_for('akis'))
            flash("Hatalı Okul Numarası veya T.C. Kimlik No!", "hata")

        elif tip == 'yetkili':
            sifre = request.form.get('sifre')
            if sifre == YETKILI_SIFRESI:
                yetkililer = veri_oku('yetkililer.json')
                for ytk in yetkililer:
                    if str(ytk.get('tc')) == str(tc):
                        session['kullanici'] = ytk.get('isim')
                        session['rol'] = 'yetkili'
                        session['tc'] = tc
                        return redirect(url_for('akis'))
                flash("Yetkili bulunamadı!", "hata")
            else:
                flash("Erişim şifresi yanlış!", "hata")

    return render_template('giris.html')

@app.route('/akis')
def akis():
    if 'kullanici' not in session:
        return redirect(url_for('giris'))
    
    aktif_mod = request.args.get('mod', 'ogrenci')
    tum = veri_oku('gonderiler.json')
    filtrelenmis = [p for p in tum if p.get('tur') == aktif_mod and p.get('durum') == 'yayinda']
    filtrelenmis.reverse()

    uyarili_mi = False
    if session.get('rol') == 'ogrenci':
        ogrenciler = veri_oku('ogrenciler.json')
        aktif_hafta = bu_haftanin_numarasi()
        for ogr in ogrenciler:
            if str(ogr.get('tc')) == str(session.get('tc')):
                if ogr.get('uyari_haftasi') == aktif_hafta:
                    uyarili_mi = True
                    break
    
    return render_template('akis.html', gonderiler=filtrelenmis, aktif_mod=aktif_mod, uyarili_mi=uyarili_mi)

@app.route('/gonder', methods=['POST'])
def gonder():
    if 'kullanici' not in session:
        return redirect(url_for('giris'))
    
    if bugun_gunlerden_ne() == 6:
        flash("Pazar günleri gönderi yapılamaz. Akış sıfırlanmıştır.", "hata")
        return redirect(url_for('akis'))

    icerik = request.form.get('icerik', '').strip()
    if not icerik:
        return redirect(url_for('akis'))

    gonderiler = veri_oku('gonderiler.json')
    aktif_hafta = bu_haftanin_numarasi()

    if session.get('rol') == 'ogrenci':
        ogrenciler = veri_oku('ogrenciler.json')
        for ogr in ogrenciler:
            if str(ogr.get('tc')) == str(session.get('tc')):
                if ogr.get('uyari_haftasi') == aktif_hafta:
                    flash("Yetkililerden uyarı aldınız! Bu hafta boyunca gönderi yapamazsınız.", "hata")
                    return redirect(url_for('akis'))

        attiklari = [p for p in gonderiler if p.get('tc') == session.get('tc') and p.get('hafta_no') == aktif_hafta]
        if len(attiklari) >= 2:
            flash("Haftalık 2 gönderi limitinizi doldurdunuz!", "hata")
            return redirect(url_for('akis'))

    durum = "yayinda"
    
    if session.get('rol') == 'ogrenci':
        uygunsuz_kelimeler = [k.lower() for k in veri_oku('uygunsuz.json')]
        
        if spam_mi(icerik):
            durum = "beklemede"
        else:
            temiz_metin = re.sub(r'[^\w\s]', '', icerik.lower())
            kelimeler = temiz_metin.split()
            
            for k in uygunsuz_kelimeler:
                if k in kelimeler:
                    durum = "beklemede"
                    break
        
        if durum == "beklemede":
            flash("Gönderiniz bir sebepten dolayı denetime gönderildi.", "hata")

    yeni_id = int(datetime.now().timestamp())
    gonderiler.append({
        "id": yeni_id,
        "yazar": session.get('kullanici'),
        "tc": session.get('tc'),
        "tur": session.get('rol'),
        "icerik": icerik,
        "tarih": datetime.now().strftime("%d.%m.%Y %H:%M"),
        "hafta_no": aktif_hafta,
        "begenenler": [],
        "yorumlar": [],
        "durum": durum
    })
    
    veri_yaz('gonderiler.json', gonderiler)
    
    if durum == "yayinda":
        flash("Paylaşımınız başarıyla yayınlandı!", "bilgi")
        
    return redirect(url_for('akis', mod=session.get('rol')))

@app.route('/ogrenci_sil/<int:post_id>')
def ogrenci_sil(post_id):
    if 'kullanici' not in session or session.get('rol') != 'ogrenci':
        return redirect(url_for('akis'))
        
    gonderiler = veri_oku('gonderiler.json')
    yeni_liste = [p for p in gonderiler if not (str(p.get('id')) == str(post_id) and str(p.get('tc')) == str(session.get('tc')))]
    
    if len(yeni_liste) < len(gonderiler):
        veri_yaz('gonderiler.json', yeni_liste)
        flash("Gönderiniz başarıyla silindi.", "bilgi")
        
    return redirect(request.referrer)

@app.route('/yetkili_islem', methods=['POST'])
def yetkili_islem():
    if 'kullanici' not in session or session.get('rol') != 'yetkili':
        return redirect(url_for('akis'))
    
    islem = request.form.get('islem_turu')
    hedef = request.form.get('hedef_id')
    sifre = request.form.get('sifre')
    
    if sifre != YETKILI_SIFRESI:
        flash("Hatalı yetkili şifresi. İşlem reddedildi!", "hata")
        return redirect(request.referrer)
        
    if islem == 'sil':
        gonderiler = [p for p in veri_oku('gonderiler.json') if str(p.get('id')) != str(hedef)]
        veri_yaz('gonderiler.json', gonderiler)
        flash("Gönderi başarıyla silindi.", "bilgi")
        
    elif islem == 'banla':
        ogrenciler = veri_oku('ogrenciler.json')
        for ogr in ogrenciler:
            if str(ogr.get('tc')) == str(hedef):
                ogr['banned'] = True
        veri_yaz('ogrenciler.json', ogrenciler)
        
        gonderiler = [p for p in veri_oku('gonderiler.json') if str(p.get('tc')) != str(hedef)]
        veri_yaz('gonderiler.json', gonderiler)
        
        flash("Öğrenci banlandı ve tüm gönderileri sistemden temizlendi!", "bilgi")
        
    elif islem == 'ban_kaldir':
        ogrenciler = veri_oku('ogrenciler.json')
        for ogr in ogrenciler:
            if str(ogr.get('tc')) == str(hedef):
                ogr['banned'] = False
        veri_yaz('ogrenciler.json', ogrenciler)
        flash("Öğrencinin banı kaldırıldı ve sisteme erişimi açıldı.", "bilgi")

    elif islem == 'uyari':
        ogrenciler = veri_oku('ogrenciler.json')
        for ogr in ogrenciler:
            if str(ogr.get('tc')) == str(hedef):
                ogr['uyari_haftasi'] = bu_haftanin_numarasi()
        veri_yaz('ogrenciler.json', ogrenciler)
        
        gonderiler = [p for p in veri_oku('gonderiler.json') if str(p.get('tc')) != str(hedef)]
        veri_yaz('gonderiler.json', gonderiler)
        
        flash("Öğrenciye uyarı verildi! Mevcut tüm gönderileri silindi ve bu hafta paylaşım yapması engellendi.", "bilgi")

    elif islem == 'uyari_kaldir':
        ogrenciler = veri_oku('ogrenciler.json')
        for ogr in ogrenciler:
            if str(ogr.get('tc')) == str(hedef):
                ogr['uyari_haftasi'] = 0
        veri_yaz('ogrenciler.json', ogrenciler)
        flash("Öğrencinin uyarısı kaldırıldı. Artık paylaşım yapabilir.", "bilgi")
        
    elif islem == 'onayla':
        gonderiler = veri_oku('gonderiler.json')
        for p in gonderiler:
            if str(p.get('id')) == str(hedef):
                p['durum'] = 'yayinda'
        veri_yaz('gonderiler.json', gonderiler)
        flash("Gönderi onaylanarak akışa alındı.", "bilgi")

    return redirect(request.referrer)

@app.route('/begen/<int:post_id>')
def begen(post_id):
    if 'kullanici' not in session:
        return redirect(url_for('giris'))
        
    gonderiler = veri_oku('gonderiler.json')
    for p in gonderiler:
        if str(p.get('id')) == str(post_id):
            if 'begenenler' not in p:
                p['begenenler'] = []
            if session.get('tc') in p['begenenler']:
                p['begenenler'].remove(session.get('tc'))
            else:
                p['begenenler'].append(session.get('tc'))
            break
            
    veri_yaz('gonderiler.json', gonderiler)
    return redirect(request.referrer)

@app.route('/yorum/<int:post_id>', methods=['POST'])
def yorum_yap(post_id):
    if 'kullanici' not in session:
        return redirect(url_for('giris'))
        
    icerik = request.form.get('yorum_icerik', '').strip()
    if not icerik:
        return redirect(request.referrer)
        
    gonderiler = veri_oku('gonderiler.json')
    for p in gonderiler:
        if str(p.get('id')) == str(post_id):
            if 'yorumlar' not in p:
                p['yorumlar'] = []
            p['yorumlar'].append({
                "yazan": session.get('kullanici'), 
                "rol": session.get('rol'),
                "icerik": icerik, 
                "tarih": datetime.now().strftime("%H:%M")
            })
            break
            
    veri_yaz('gonderiler.json', gonderiler)
    return redirect(request.referrer)

@app.route('/profil')
def profil():
    if 'kullanici' not in session:
        return redirect(url_for('giris'))
        
    gonderiler = [p for p in veri_oku('gonderiler.json') if str(p.get('tc')) == str(session.get('tc'))]
    gonderiler.reverse()
    
    return render_template('profil.html', gonderiler=gonderiler)

@app.route('/trendler')
def trendler():
    if 'kullanici' not in session:
        return redirect(url_for('giris'))
        
    ogrenci_yayinda = [p for p in veri_oku('gonderiler.json') if p.get('tur') == 'ogrenci' and p.get('durum') == 'yayinda']
    sirali = sorted(ogrenci_yayinda, key=lambda x: len(x.get('begenenler', [])), reverse=True)
    
    return render_template('trendler.html', gonderiler=sirali)

@app.route('/denetimler')
def denetimler():
    if 'kullanici' not in session or session.get('rol') != 'yetkili':
        return redirect(url_for('akis'))
        
    bekleyenler = [p for p in veri_oku('gonderiler.json') if p.get('durum') == 'beklemede']
    
    return render_template('denetimler.html', gonderiler=bekleyenler)

@app.route('/ogrenciler')
def ogrenciler():
    if 'kullanici' not in session or session.get('rol') != 'yetkili':
        return redirect(url_for('akis'))
        
    liste = veri_oku('ogrenciler.json')
    hafta = bu_haftanin_numarasi()
    
    return render_template('ogrenciler.html', ogrenciler=liste, aktif_hafta=hafta)

@app.route('/anket')
def anket():
    if 'kullanici' not in session:
        return redirect(url_for('giris'))
        
    top_3 = []
    # Eğer günlerden Cumartesi (5) ise, en çok beğeni alan 3 gönderiyi bul
    if bugun_gunlerden_ne() == 5:
        ogrenci_yayinda = [p for p in veri_oku('gonderiler.json') if p.get('tur') == 'ogrenci' and p.get('durum') == 'yayinda']
        sirali = sorted(ogrenci_yayinda, key=lambda x: len(x.get('begenenler', [])), reverse=True)
        top_3 = sirali[:3] # Sadece ilk 3'ü al
        
    return render_template('anket.html', top_3=top_3)

@app.route('/cikis')
def cikis():
    session.clear()
    return redirect(url_for('giris'))

if __name__ == '__main__':
    if not os.path.exists("data"):
        os.makedirs("data")
        
    for dosya in ["ogrenciler.json", "yetkililer.json", "gonderiler.json", "kazanan.json", "uygunsuz.json"]:
        if not os.path.exists(f"data/{dosya}"):
            if dosya == "uygunsuz.json":
                veri_yaz(dosya, ["kötü", "küfür", "argo", "aptal", "salak", "çirkin", "saçma"])
            else:
                veri_yaz(dosya, [])
                
    app.run(debug=True)