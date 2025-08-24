#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ağırlıklı Ortalama Fiyat Hesaplayıcı (GUI)
- Fiyat ve Miktar girerek pozisyon ekleyin
- Toplam maliyet, toplam miktar ve ortalama fiyat otomatik hesaplanır
- Geri al, sil, sıfırla, CSV dışa aktar
- Türkçe arayüz
"""

import sys
import csv
import os
import locale
try:
    # Türkçe format desteği (virgül/nokta)
    locale.setlocale(locale.LC_ALL, 'tr_TR.UTF-8')
except Exception:
    pass

import tkinter as tk
from tkinter import ttk, messagebox, filedialog

APP_TITLE = "modtrader - İşlem Fiyat Hesaplayıcı"
APP_GEOMETRY = "700x520"

def parse_number(s: str) -> float:
    """
    Kullanıcı girdisindeki virgül/nokta durumlarını düzelterek float'a çevirir.
    Boş veya hatalı girişte ValueError yükseltir.
    """
    s = s.strip()
    if not s:
        raise ValueError("Boş değer")
    # Binlik ayırıcıları temizle
    s = s.replace(" ", "").replace("_", "")
    # Türkçe ondalık virgülü destekle
    if s.count(",") > 0 and s.count(".") == 0:
        s = s.replace(",", ".")
    # Eğer hem virgül hem nokta varsa, son ondalık ayıraç kabulü
    if s.count(",") > 0 and s.count(".") > 0:
        # Son görünen ayıracı ondalık say, diğerlerini kaldır
        last_comma = s.rfind(",")
        last_dot = s.rfind(".")
        if last_comma > last_dot:
            s = s.replace(".", "")
            s = s.replace(",", ".")
        else:
            s = s.replace(",", "")
    return float(s)

class AvgCalculatorApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry(APP_GEOMETRY)
        self.minsize(640, 480)
        self._build_ui()
        self.rows = []  # (price, qty, cost)
        self.update_totals()

    def _build_ui(self):
        # Üst giriş çerçevesi
        top = ttk.LabelFrame(self, text="Pozisyon Ekle")
        top.pack(fill="x", padx=12, pady=10)

        ttk.Label(top, text="Fiyat:").grid(row=0, column=0, padx=(10,6), pady=8, sticky="e")
        self.price_var = tk.StringVar()
        self.price_entry = ttk.Entry(top, textvariable=self.price_var, width=16)
        self.price_entry.grid(row=0, column=1, padx=(0,10), pady=8, sticky="w")
        self.price_entry.focus_set()

        ttk.Label(top, text="Miktar:").grid(row=0, column=2, padx=(10,6), pady=8, sticky="e")
        self.qty_var = tk.StringVar()
        self.qty_entry = ttk.Entry(top, textvariable=self.qty_var, width=16)
        self.qty_entry.grid(row=0, column=3, padx=(0,10), pady=8, sticky="w")

        self.add_btn = ttk.Button(top, text="Ekle (Enter)", command=self.add_row)
        self.add_btn.grid(row=0, column=4, padx=10, pady=8)

        # Tuş kısayolları
        self.bind("<Return>", lambda e: self.add_row())
        self.bind("<KP_Enter>", lambda e: self.add_row())

        # Tablo
        table_frame = ttk.LabelFrame(self, text="İşlemler")
        table_frame.pack(fill="both", expand=True, padx=12, pady=(0,10))

        cols = ("#","Fiyat","Miktar","Maliyet (Fiyat×Miktar)")
        self.tree = ttk.Treeview(table_frame, columns=cols, show="headings", height=10)
        for c in cols:
            self.tree.heading(c, text=c, anchor="center")
            self.tree.column(c, anchor="e", stretch=True, width=140)
        self.tree.column("#", width=60, anchor="center")

        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        table_frame.rowconfigure(0, weight=1)
        table_frame.columnconfigure(0, weight=1)

        # Alt butonlar
        btns = ttk.Frame(self)
        btns.pack(fill="x", padx=12, pady=(0,6))

        ttk.Button(btns, text="Geri Al (⌘/Ctrl+Z)", command=self.undo).pack(side="left", padx=4)
        ttk.Button(btns, text="Seçileni Sil", command=self.delete_selected).pack(side="left", padx=4)
        ttk.Button(btns, text="Sıfırla", command=self.reset_all).pack(side="left", padx=4)
        ttk.Button(btns, text="CSV Dışa Aktar", command=self.export_csv).pack(side="left", padx=4)

        # Kısayol
        self.bind_all("<Control-z>", lambda e: self.undo())
        self.bind_all("<Command-z>", lambda e: self.undo())

        # Sonuç paneli
        result = ttk.LabelFrame(self, text="Sonuçlar")
        result.pack(fill="x", padx=12, pady=(0,12))

        self.total_cost_var = tk.StringVar(value="0")
        self.total_qty_var = tk.StringVar(value="0")
        self.avg_price_var = tk.StringVar(value="0")

        def make_row(r, label, var):
            ttk.Label(result, text=label).grid(row=r, column=0, sticky="w", padx=10, pady=6)
            ttk.Label(result, textvariable=var, font=("TkDefaultFont", 12, "bold")).grid(row=r, column=1, sticky="e", padx=10, pady=6)

        make_row(0, "Toplam Maliyet:", self.total_cost_var)
        make_row(1, "Toplam Miktar:", self.total_qty_var)
        make_row(2, "Ortalama Fiyat:", self.avg_price_var)

        # Bilgilendirme
        hint = ttk.Label(self, text="İpucu: Hisse Fiyat: 16 USD'dan 50 USD ekle, 13 USD'dan 50 USD ekleyin, maliyet hesaplanır.\n" 
                                    "Ortalama = Σ(Fiyat×Miktar) / Σ(Miktar)",
                         foreground="#050")
        hint.pack(padx=3, pady=(0,3))

    def add_row(self):
        try:
            price = parse_number(self.price_var.get())
            qty = parse_number(self.qty_var.get())

            if qty == 0:
                raise ValueError("Miktar 0 olamaz")
            cost = price * qty
            self.rows.append((price, qty, cost))
            self._append_tree_item(price, qty, cost)

            # Temizle ve fiyat alanına odaklan
            self.qty_var.set("")
            self.price_var.set("")
            self.price_entry.focus_set()

            self.update_totals()
        except ValueError as e:
            messagebox.showerror("Hata", f"Lütfen geçerli bir sayı girin.\n\nDetay: {e}")
        except Exception as e:
            messagebox.showerror("Hata", f"Beklenmeyen bir hata oluştu:\n{e}")

    def _append_tree_item(self, price, qty, cost):
        idx = len(self.rows)
        self.tree.insert("", "end", values=(idx, self._fmt(price), self._fmt(qty), self._fmt(cost)))

    def update_totals(self):
        total_qty = sum(q for _, q, _ in self.rows)
        total_cost = sum(c for _, _, c in self.rows)
        avg = (total_cost / total_qty) if total_qty != 0 else 0.0
        self.total_qty_var.set(self._fmt(total_qty))
        self.total_cost_var.set(self._fmt(total_cost))
        self.avg_price_var.set(self._fmt(avg))

    def undo(self):
        if not self.rows:
            return
        self.rows.pop()
        # son satırı sil
        children = self.tree.get_children()
        if children:
            self.tree.delete(children[-1])
        self.update_totals()

    def delete_selected(self):
        sel = self.tree.selection()
        if not sel:
            return
        # Seçilen indexleri sıraya koyup tersten sil
        indices = []
        for item in sel:
            vals = self.tree.item(item, "values")
            if not vals:
                continue
            try:
                idx = int(vals[0]) - 1
                indices.append(idx)
            except Exception:
                continue
        for i in sorted(set(indices), reverse=True):
            if 0 <= i < len(self.rows):
                self.rows.pop(i)
        # tabloyu yeniden çiz
        for item in self.tree.get_children():
            self.tree.delete(item)
        for i, (p, q, c) in enumerate(self.rows, start=1):
            self.tree.insert("", "end", values=(i, self._fmt(p), self._fmt(q), self._fmt(c)))
        self.update_totals()

    def reset_all(self):
        if messagebox.askyesno("Onay", "Tüm girdileri sıfırlamak istediğinize emin misiniz?"):
            self.rows.clear()
            for item in self.tree.get_children():
                self.tree.delete(item)
            self.update_totals()

    def export_csv(self):
        if not self.rows:
            messagebox.showinfo("Bilgi", "Dışa aktarılacak veri yok.")
            return
        initial = os.path.expanduser("~/avg_calc.csv")
        path = filedialog.asksaveasfilename(
            title="CSV olarak kaydet",
            defaultextension=".csv",
            initialfile=os.path.basename(initial),
            filetypes=[("CSV dosyası", "*.csv"), ("Tüm Dosyalar", "*.*")],
        )
        if not path:
            return
        try:
            with open(path, "w", newline="", encoding="utf-8") as f:
                w = csv.writer(f)
                w.writerow(["#", "Fiyat", "Miktar", "Maliyet"])
                for i, (p, q, c) in enumerate(self.rows, start=1):
                    w.writerow([i, p, q, c])
                # özet
                total_qty = sum(q for _, q, _ in self.rows)
                total_cost = sum(c for _, _, c in self.rows)
                avg = (total_cost / total_qty) if total_qty != 0 else 0.0
                w.writerow([])
                w.writerow(["Toplam Maliyet", total_cost])
                w.writerow(["Toplam Miktar", total_qty])
                w.writerow(["Ortalama Fiyat", avg])
            messagebox.showinfo("Başarılı", f"CSV olarak kaydedildi:\n{path}")
        except Exception as e:
            messagebox.showerror("Hata", f"Kaydetme başarısız:\n{e}")

    @staticmethod
    def _fmt(x: float) -> str:
        # Nokta ile gösterim; istenirse burada format özelleştirilebilir
        try:
            return f"{x:,.6f}".replace(",", "_").replace(".", ",").replace("_", ".")
        except Exception:
            return str(x)

def main():
    try:
        app = AvgCalculatorApp()
        app.mainloop()
    except tk.TclError as e:
        # GUI açılamazsa (ör. sunucu/SSH), CLI yedek mod
        print("GUI başlatılamadı, komut satırı moduna geçiliyor...")
        print("Sebep:", e)
        print("\nKomut satırı modu:\nHer satırda 'fiyat miktar' girin (ör: 4870 90). Boş satır ile bitiriniz.\n")
        rows = []
        while True:
            try:
                line = input("> ").strip()
            except EOFError:
                break
            if not line:
                break
            parts = line.split()
            if len(parts) != 2:
                print("Lütfen 'fiyat miktar' şeklinde giriş yapın.")
                continue
            try:
                price = parse_number(parts[0])
                qty = parse_number(parts[1])
            except Exception as ex:
                print("Hatalı giriş:", ex)
                continue
            rows.append((price, qty, price*qty))
        total_qty = sum(q for _, q, _ in rows)
        total_cost = sum(c for _, _, c in rows)
        avg = (total_cost / total_qty) if total_qty else 0.0
        print(f"\nToplam Maliyet: {total_cost:.6f}")
        print(f"Toplam Miktar:  {total_qty:.6f}")
        print(f"Ortalama Fiyat: {avg:.6f}")

if __name__ == "__main__":
    main()
