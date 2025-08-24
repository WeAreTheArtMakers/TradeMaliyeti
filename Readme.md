# modCalc – İşlem Fiyat Hesaplayıcı

Ağırlıklı Ortalama Fiyat Hesaplayıcı (GUI)  
📊 Fiyat ve miktar girerek ortalama maliyetini kolayca hesapla.  

---

## 🚀 Özellikler
- Fiyat ve Miktar girerek pozisyon ekleme
- Toplam **Maliyet**, **Miktar** ve **Ortalama Fiyat** otomatik hesaplama
- **Geri al (Ctrl/⌘+Z)**, **Seçiliyi sil**, **Sıfırla**
- CSV dışa aktarma
- Türkçe arayüz desteği
- CLI (komut satırı) yedek modu – GUI açılamazsa otomatik devreye girer

---

## 📦 Kurulum

1. Python 3 kurulu olduğundan emin olun:
   ```bash
   python3 --version

2.Depoyu klonlayın veya dosyayı indirin:

git clone https://github.com/WeAreTheArtMakers/TradeMaliyeti.git


Programı çalıştırın:

python3 modcalc.py


💻 Kullanım
GUI Modu

Fiyat ve Miktar girin → Ekle (Enter)

Tabloya eklenen her satır için Maliyet otomatik hesaplanır

Alt kısımda Toplam Maliyet, Toplam Miktar, Ortalama Fiyat gösterilir

CLI Modu

Eğer GUI açılamazsa (ör. SSH bağlantısı) otomatik olarak CLI moduna geçer:

> 4870 90
> 4830 50

Toplam Maliyet: 746700.000000
Toplam Miktar:  140.000000
Ortalama Fiyat: 5333.571429

📁 CSV Dışa Aktarma

Tablodaki verileri CSV dosyasına aktarabilirsiniz.
Çıktı dosyası örneği:

#,Fiyat,Miktar,Maliyet
1,4870,90,438300
2,4830,50,241500

Toplam Maliyet,679800
Toplam Miktar,140
Ortalama Fiyat,4855.714286

⌨️ Kısayollar

Enter / Numpad Enter → Yeni satır ekle

Ctrl+Z / ⌘+Z → Geri al

Delete → Seçili satırı sil

📌 Gereksinimler

Python 3.8+

Tkinter (çoğu sistemde Python ile birlikte gelir)
