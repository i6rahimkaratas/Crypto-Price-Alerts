import tkinter as tk
from tkinter import ttk, messagebox
import customtkinter as ctk
import requests
import json
import threading
import time
import subprocess
import platform
from datetime import datetime
from PIL import Image, ImageTk
import io
from typing import Dict, List, Optional
import webbrowser


ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class ModernCryptoApp:
    def __init__(self):
        
        self.root = ctk.CTk()
        self.root.title("🚀 Kripto Takip Pro")
        self.root.geometry("1400x900")
        self.root.minsize(1000, 700)
        
        
        self.watchlist = self.load_watchlist()
        self.alarms = self.load_alarms()
        self.crypto_images = {}
        self.search_results_data = []
        
        
        self.monitoring_active = True
        self.search_after_id = None
        
        
        self.current_prices = {}
        
        self.setup_ui()
        self.start_price_monitoring()
        
        
        self.refresh_watchlist()
        self.refresh_alarms()
        
    def setup_ui(self):
       
        main_container = ctk.CTkFrame(self.root, fg_color="transparent")
        main_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        
        self.create_header(main_container)
        
        
        content_frame = ctk.CTkFrame(main_container, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, pady=(20, 0))
        
       
        left_panel = ctk.CTkFrame(content_frame, width=800)
        left_panel.pack(side="left", fill="both", expand=True, padx=(0, 10))
        left_panel.pack_propagate(False)
        
      
        right_panel = ctk.CTkFrame(content_frame, width=350)
        right_panel.pack(side="right", fill="both", padx=(10, 0))
        right_panel.pack_propagate(False)
        
        
        self.setup_left_panel(left_panel)
        
        
        self.setup_right_panel(right_panel)
        
    def create_header(self, parent):
        
        header_frame = ctk.CTkFrame(parent, height=120, fg_color=("gray90", "gray15"))
        header_frame.pack(fill="x", pady=(0, 20))
        header_frame.pack_propagate(False)
        
        
        title_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        title_frame.pack(side="left", fill="y", padx=30, pady=20)
        
        title_label = ctk.CTkLabel(
            title_frame,
            text="🚀 Kripto Takip Pro",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=("gray10", "white")
        )
        title_label.pack(anchor="w")
        
        subtitle_label = ctk.CTkLabel(
            title_frame,
            text="Profesyonel kripto para takip ve alarm sistemi",
            font=ctk.CTkFont(size=14),
            text_color=("gray40", "gray60")
        )
        subtitle_label.pack(anchor="w", pady=(5, 0))
        
        
        stats_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        stats_frame.pack(side="right", fill="y", padx=30, pady=20)
        
        
        self.create_stat_cards(stats_frame)
        
    def create_stat_cards(self, parent):
        
        cards_frame = ctk.CTkFrame(parent, fg_color="transparent")
        cards_frame.pack(fill="both", expand=True)
        
       
        watchlist_card = ctk.CTkFrame(cards_frame, width=120, height=80)
        watchlist_card.pack(side="left", padx=10)
        watchlist_card.pack_propagate(False)
        
        ctk.CTkLabel(
            watchlist_card,
            text=str(len(self.watchlist)),
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="cyan"
        ).pack(pady=(15, 0))
        
        ctk.CTkLabel(
            watchlist_card,
            text="İzlenen",
            font=ctk.CTkFont(size=12)
        ).pack()
        
        
        active_alarms = len([a for a in self.alarms if not a.get('triggered', False)])
        alarms_card = ctk.CTkFrame(cards_frame, width=120, height=80)
        alarms_card.pack(side="left", padx=10)
        alarms_card.pack_propagate(False)
        
        ctk.CTkLabel(
            alarms_card,
            text=str(active_alarms),
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="orange"
        ).pack(pady=(15, 0))
        
        ctk.CTkLabel(
            alarms_card,
            text="Aktif Alarm",
            font=ctk.CTkFont(size=12)
        ).pack()
        
       
        triggered_alarms = len([a for a in self.alarms if a.get('triggered', False)])
        triggered_card = ctk.CTkFrame(cards_frame, width=120, height=80)
        triggered_card.pack(side="left", padx=10)
        triggered_card.pack_propagate(False)
        
        ctk.CTkLabel(
            triggered_card,
            text=str(triggered_alarms),
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="green"
        ).pack(pady=(15, 0))
        
        ctk.CTkLabel(
            triggered_card,
            text="Tetiklenen",
            font=ctk.CTkFont(size=12)
        ).pack()
        
    def setup_left_panel(self, parent):
        
        search_frame = ctk.CTkFrame(parent, height=200)
        search_frame.pack(fill="x", padx=20, pady=20)
        search_frame.pack_propagate(False)
        
        search_title = ctk.CTkLabel(
            search_frame,
            text="🔍 Kripto Para Arama",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        search_title.pack(pady=(20, 15))
        
        
        search_container = ctk.CTkFrame(search_frame, fg_color="transparent")
        search_container.pack(fill="x", padx=20)
        
        self.search_entry = ctk.CTkEntry(
            search_container,
            placeholder_text="Bitcoin, Ethereum, BTC, ETH...",
            font=ctk.CTkFont(size=14),
            height=40
        )
        self.search_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.search_entry.bind("<KeyRelease>", self.on_search_change)
        
        search_btn = ctk.CTkButton(
            search_container,
            text="Ara",
            width=100,
            height=40,
            command=self.manual_search
        )
        search_btn.pack(side="right")
        
       
        self.search_results_frame = ctk.CTkScrollableFrame(
            search_frame,
            height=100,
            label_text="Arama Sonuçları"
        )
        self.search_results_frame.pack(fill="both", expand=True, padx=20, pady=(15, 20))
        
       
        watchlist_frame = ctk.CTkFrame(parent)
        watchlist_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        
        watchlist_header = ctk.CTkFrame(watchlist_frame, height=60)
        watchlist_header.pack(fill="x", padx=20, pady=(20, 0))
        watchlist_header.pack_propagate(False)
        
        watchlist_title = ctk.CTkLabel(
            watchlist_header,
            text="📊 İzleme Listesi",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        watchlist_title.pack(side="left", pady=20)
        
        refresh_btn = ctk.CTkButton(
            watchlist_header,
            text="🔄 Yenile",
            width=100,
            command=self.refresh_watchlist
        )
        refresh_btn.pack(side="right", pady=15, padx=(0, 20))
        
       
        self.watchlist_container = ctk.CTkScrollableFrame(watchlist_frame)
        self.watchlist_container.pack(fill="both", expand=True, padx=20, pady=20)
        
    def setup_right_panel(self, parent):
      
        alarms_header = ctk.CTkFrame(parent, height=60)
        alarms_header.pack(fill="x", padx=20, pady=20)
        alarms_header.pack_propagate(False)
        
        alarms_title = ctk.CTkLabel(
            alarms_header,
            text="🔔 Alarmlar",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        alarms_title.pack(side="left", pady=20)
        
        
        new_alarm_btn = ctk.CTkButton(
            alarms_header,
            text="➕ Yeni",
            width=80,
            command=self.show_new_alarm_dialog
        )
        new_alarm_btn.pack(side="right", pady=15, padx=(0, 20))
        
        
        self.alarms_container = ctk.CTkScrollableFrame(parent)
        self.alarms_container.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
    def on_search_change(self, event):
        
        if self.search_after_id:
            self.root.after_cancel(self.search_after_id)
        
        query = self.search_entry.get().strip()
        if len(query) >= 2:
            self.search_after_id = self.root.after(500, lambda: self.search_crypto(query))
        else:
            self.clear_search_results()
    
    def manual_search(self):
       
        query = self.search_entry.get().strip()
        if len(query) >= 2:
            self.search_crypto(query)
        else:
            messagebox.showwarning("Uyarı", "En az 2 karakter giriniz!")
    
    def search_crypto(self, query):
        
        def search_thread():
            try:
                
                self.root.after(0, self.show_search_loading)
                
                url = f"https://api.coingecko.com/api/v3/search?query={query}"
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                data = response.json()
                
                self.search_results_data = data.get('coins', [])[:10]
                self.root.after(0, self.display_search_results)
                
            except requests.RequestException as e:
                self.root.after(0, lambda: self.show_error(f"Arama hatası: {str(e)}"))
        
        threading.Thread(target=search_thread, daemon=True).start()
    
    def show_search_loading(self):
        
        self.clear_search_results()
        loading_frame = ctk.CTkFrame(self.search_results_frame, height=60)
        loading_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(
            loading_frame,
            text="🔄 Aranıyor...",
            font=ctk.CTkFont(size=14)
        ).pack(pady=20)
    
    def display_search_results(self):
        
        self.clear_search_results()
        
        if not self.search_results_data:
            no_result_frame = ctk.CTkFrame(self.search_results_frame, height=60)
            no_result_frame.pack(fill="x", pady=10)
            
            ctk.CTkLabel(
                no_result_frame,
                text="❌ Sonuç bulunamadı",
                font=ctk.CTkFont(size=14)
            ).pack(pady=20)
            return
        
        for crypto in self.search_results_data:
            self.create_search_result_item(crypto)
    
    def create_search_result_item(self, crypto):
        
        item_frame = ctk.CTkFrame(self.search_results_frame, height=70)
        item_frame.pack(fill="x", pady=5)
        item_frame.pack_propagate(False)
        
       
        logo_frame = ctk.CTkFrame(item_frame, width=50, height=50, corner_radius=25)
        logo_frame.pack(side="left", padx=15, pady=10)
        logo_frame.pack_propagate(False)
        
        logo_label = ctk.CTkLabel(logo_frame, text="📈", font=ctk.CTkFont(size=20))
        logo_label.pack(expand=True)
        
        
        info_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
        info_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        
        name_label = ctk.CTkLabel(
            info_frame,
            text=crypto['name'],
            font=ctk.CTkFont(size=14, weight="bold")
        )
        name_label.pack(anchor="w")
        
        symbol_label = ctk.CTkLabel(
            info_frame,
            text=f"{crypto['symbol'].upper()} • Market Cap: #{crypto.get('market_cap_rank', 'N/A')}",
            font=ctk.CTkFont(size=11),
            text_color=("gray50", "gray50")
        )
        symbol_label.pack(anchor="w")
        
        
        is_in_watchlist = any(item['id'] == crypto['id'] for item in self.watchlist)
        
        
        if is_in_watchlist:
            status_btn = ctk.CTkButton(
                item_frame,
                text="✓ Eklendi",
                width=80,
                height=30,
                fg_color="green",
                state="disabled"
            )
        else:
            status_btn = ctk.CTkButton(
                item_frame,
                text="➕ Ekle",
                width=80,
                height=30,
                command=lambda c=crypto: self.add_to_watchlist(c)
            )
        
        status_btn.pack(side="right", padx=15, pady=20)
        
        
        self.load_crypto_image_async(crypto['id'], crypto.get('large', ''), logo_label)
    
    def load_crypto_image_async(self, crypto_id, image_url, label):
       
        if not image_url or crypto_id in self.crypto_images:
            return
            
        def load_image():
            try:
                response = requests.get(image_url, timeout=5)
                response.raise_for_status()
                
                image = Image.open(io.BytesIO(response.content))
                image = image.resize((30, 30), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(image)
                
                self.crypto_images[crypto_id] = photo
                self.root.after(0, lambda: self.update_image_label(label, photo))
            except:
                pass
        
        threading.Thread(target=load_image, daemon=True).start()
    
    def update_image_label(self, label, photo):
        
        try:
            label.configure(image=photo, text="")
        except:
            pass
    
    def add_to_watchlist(self, crypto):
        
        crypto_data = {
            'id': crypto['id'],
            'name': crypto['name'],
            'symbol': crypto['symbol'].upper(),
            'image': crypto.get('large', ''),
            'market_cap_rank': crypto.get('market_cap_rank'),
            'added_at': datetime.now().isoformat()
        }
        
        self.watchlist.append(crypto_data)
        self.save_watchlist()
        
        
        self.display_search_results()  
        self.refresh_watchlist()
        self.update_stats()
        
        messagebox.showinfo("Başarılı", f"✅ {crypto['name']} izleme listesine eklendi!")
    
    def refresh_watchlist(self):
        """İzleme listesini yenile"""
        if not self.watchlist:
            self.show_empty_watchlist()
            return
        
        # Loading göster
        self.clear_watchlist()
        loading_frame = ctk.CTkFrame(self.watchlist_container, height=60)
        loading_frame.pack(fill="x", pady=20)
        
        ctk.CTkLabel(
            loading_frame,
            text="📊 Fiyatlar yükleniyor...",
            font=ctk.CTkFont(size=14)
        ).pack(pady=20)
        
        def load_watchlist_data():
            try:
                ids = ','.join([item['id'] for item in self.watchlist])
                url = f"https://api.coingecko.com/api/v3/simple/price?ids={ids}&vs_currencies=usd&include_24hr_change=true&include_market_cap=true"
                
                response = requests.get(url, timeout=15)
                response.raise_for_status()
                price_data = response.json()
                
                self.current_prices = price_data
                self.root.after(0, lambda: self.display_watchlist(price_data))
                
            except requests.RequestException as e:
                self.root.after(0, lambda: self.show_watchlist_error(str(e)))
        
        threading.Thread(target=load_watchlist_data, daemon=True).start()
    
    def display_watchlist(self, price_data):
        """İzleme listesini göster"""
        self.clear_watchlist()
        
        for crypto in self.watchlist:
            if crypto['id'] in price_data:
                self.create_watchlist_item(crypto, price_data[crypto['id']])
    
    def create_watchlist_item(self, crypto, price_info):
        """Geliştirilmiş izleme listesi öğesi"""
        price = price_info.get('usd', 0)
        change_24h = price_info.get('usd_24h_change', 0)
        market_cap = price_info.get('usd_market_cap', 0)
        
        item_frame = ctk.CTkFrame(self.watchlist_container, height=90)
        item_frame.pack(fill="x", pady=5)
        item_frame.pack_propagate(False)
        
        # Logo
        logo_frame = ctk.CTkFrame(item_frame, width=60, height=60, corner_radius=30)
        logo_frame.pack(side="left", padx=20, pady=15)
        logo_frame.pack_propagate(False)
        
        if crypto['id'] in self.crypto_images:
            logo_label = ctk.CTkLabel(logo_frame, image=self.crypto_images[crypto['id']], text="")
        else:
            logo_label = ctk.CTkLabel(logo_frame, text="📈", font=ctk.CTkFont(size=24))
            self.load_crypto_image_async(crypto['id'], crypto['image'], logo_label)
        logo_label.pack(expand=True)
        
        # Bilgiler
        info_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
        info_frame.pack(side="left", fill="both", expand=True, padx=15, pady=15)
        
        name_symbol_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
        name_symbol_frame.pack(fill="x")
        
        name_label = ctk.CTkLabel(
            name_symbol_frame,
            text=crypto['name'],
            font=ctk.CTkFont(size=16, weight="bold")
        )
        name_label.pack(side="left")
        
        symbol_label = ctk.CTkLabel(
            name_symbol_frame,
            text=f"({crypto['symbol']})",
            font=ctk.CTkFont(size=12),
            text_color=("gray50", "gray50")
        )
        symbol_label.pack(side="left", padx=(10, 0))
        
        if crypto.get('market_cap_rank'):
            rank_label = ctk.CTkLabel(
                name_symbol_frame,
                text=f"#{crypto['market_cap_rank']}",
                font=ctk.CTkFont(size=10, weight="bold"),
                text_color="orange"
            )
            rank_label.pack(side="right")
        
        # Alt bilgiler
        details_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
        details_frame.pack(fill="x", pady=(10, 0))
        
        if market_cap > 0:
            mc_text = self.format_market_cap(market_cap)
            mc_label = ctk.CTkLabel(
                details_frame,
                text=f"Market Cap: {mc_text}",
                font=ctk.CTkFont(size=10),
                text_color=("gray60", "gray40")
            )
            mc_label.pack(side="left")
        
        # Fiyat bilgileri (sağ taraf)
        price_frame = ctk.CTkFrame(item_frame, fg_color="transparent", width=200)
        price_frame.pack(side="right", padx=20, pady=15)
        price_frame.pack_propagate(False)
        
        price_label = ctk.CTkLabel(
            price_frame,
            text=f"${self.format_price(price)}",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        price_label.pack(anchor="e")
        
        # Değişim oranı
        change_color = "green" if change_24h >= 0 else "red"
        change_symbol = "↗" if change_24h >= 0 else "↘"
        change_label = ctk.CTkLabel(
            price_frame,
            text=f"{change_symbol} {abs(change_24h):.2f}%",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=change_color
        )
        change_label.pack(anchor="e", pady=(5, 0))
        
        # Butonlar
        buttons_frame = ctk.CTkFrame(price_frame, fg_color="transparent")
        buttons_frame.pack(anchor="e", pady=(10, 0))
        
        # Alarm butonu
        has_alarm = self.has_active_alarm(crypto['id'])
        alarm_btn = ctk.CTkButton(
            buttons_frame,
            text="🔔",
            width=40,
            height=30,
            fg_color="orange" if has_alarm else ("gray50", "gray30"),
            hover_color="darkorange" if has_alarm else ("gray40", "gray40"),
            command=lambda: self.create_alarm_for_crypto(crypto, price)
        )
        alarm_btn.pack(side="left", padx=2)
        
        # Silme butonu
        delete_btn = ctk.CTkButton(
            buttons_frame,
            text="🗑️",
            width=40,
            height=30,
            fg_color="red",
            hover_color="darkred",
            command=lambda: self.remove_from_watchlist(crypto)
        )
        delete_btn.pack(side="left", padx=2)
    
    def format_price(self, price):
        """Fiyat formatlama"""
        if price >= 1:
            return f"{price:,.2f}"
        else:
            return f"{price:.6f}".rstrip('0').rstrip('.')
    
    def format_market_cap(self, market_cap):
        """Market cap formatlama"""
        if market_cap >= 1e12:
            return f"${market_cap/1e12:.2f}T"
        elif market_cap >= 1e9:
            return f"${market_cap/1e9:.2f}B"
        elif market_cap >= 1e6:
            return f"${market_cap/1e6:.2f}M"
        else:
            return f"${market_cap:,.0f}"
    
    def remove_from_watchlist(self, crypto):
        """İzleme listesinden kaldır"""
        if messagebox.askyesno("Onay", f"{crypto['name']} izleme listesinden kaldırılsın mı?"):
            self.watchlist = [item for item in self.watchlist if item['id'] != crypto['id']]
            self.save_watchlist()
            self.refresh_watchlist()
            self.update_stats()
    
    def create_alarm_for_crypto(self, crypto, current_price):
        """Kripto için alarm oluştur"""
        self.show_alarm_dialog(crypto, current_price)
    
    def show_new_alarm_dialog(self):
        """Yeni alarm dialog'u (kripto seçimi ile)"""
        if not self.watchlist:
            messagebox.showwarning("Uyarı", "Önce izleme listesine kripto para ekleyin!")
            return
        
        # Kripto seçim penceresi
        selection_dialog = ctk.CTkToplevel(self.root)
        selection_dialog.title("Kripto Para Seçin")
        selection_dialog.geometry("400x300")
        selection_dialog.transient(self.root)
        selection_dialog.grab_set()
        
        # Merkezi konumlandır
        selection_dialog.geometry("+%d+%d" % (
            self.root.winfo_rootx() + 500,
            self.root.winfo_rooty() + 200
        ))
        
        ctk.CTkLabel(
            selection_dialog,
            text="Alarm kurmak istediğiniz kripto parayı seçin:",
            font=ctk.CTkFont(size=14)
        ).pack(pady=20)
        
        # Kripto listesi
        crypto_frame = ctk.CTkScrollableFrame(selection_dialog)
        crypto_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        for crypto in self.watchlist:
            current_price = self.current_prices.get(crypto['id'], {}).get('usd', 0)
            
            item_frame = ctk.CTkFrame(crypto_frame)
            item_frame.pack(fill="x", pady=5)
            
            # Logo ve bilgi
            info_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
            info_frame.pack(side="left", fill="both", expand=True, padx=15, pady=10)
            
            ctk.CTkLabel(
                info_frame,
                text=f"{crypto['name']} ({crypto['symbol']})",
                font=ctk.CTkFont(size=14, weight="bold")
            ).pack(anchor="w")
            
            if current_price > 0:
                ctk.CTkLabel(
                    info_frame,
                    text=f"Güncel: ${self.format_price(current_price)}",
                    font=ctk.CTkFont(size=12),
                    text_color=("gray50", "gray50")
                ).pack(anchor="w")
            
            # Seç butonu
            select_btn = ctk.CTkButton(
                item_frame,
                text="Seç",
                width=60,
                command=lambda c=crypto, p=current_price: self.select_crypto_for_alarm(c, p, selection_dialog)
            )
            select_btn.pack(side="right", padx=15, pady=10)
    
    def select_crypto_for_alarm(self, crypto, current_price, dialog):
        """Kripto seçildikten sonra alarm dialog'unu aç"""
        dialog.destroy()
        self.show_alarm_dialog(crypto, current_price)
    
    def show_alarm_dialog(self, crypto, current_price):
        """Alarm oluşturma dialog'u"""
        dialog = ctk.CTkToplevel(self.root)
        dialog.title(f"🔔 {crypto['name']} Alarm Kur")
        dialog.geometry("450x400")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Merkezi konumlandır
        dialog.geometry("+%d+%d" % (
            self.root.winfo_rootx() + 475,
            self.root.winfo_rooty() + 250
        ))
        
        # Ana container
        main_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Başlık
        title_label = ctk.CTkLabel(
            main_frame,
            text=f"🔔 {crypto['name']} için Alarm Kur",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.pack(pady=(0, 20))
        
        # Güncel fiyat bilgisi
        current_frame = ctk.CTkFrame(main_frame)
        current_frame.pack(fill="x", pady=(0, 20))
        
        ctk.CTkLabel(
            current_frame,
            text="Güncel Fiyat",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=(15, 5))
        
        ctk.CTkLabel(
            current_frame,
            text=f"${self.format_price(current_price) if current_price > 0 else 'Yüklenemedi'}",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="cyan"
        ).pack(pady=(0, 15))
        
        # Form alanları
        form_frame = ctk.CTkFrame(main_frame)
        form_frame.pack(fill="x", pady=(0, 20))
        
        # Hedef fiyat
        ctk.CTkLabel(
            form_frame,
            text="Hedef Fiyat ($)",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=(20, 5))
        
        price_entry = ctk.CTkEntry(
            form_frame,
            placeholder_text="0.00",
            font=ctk.CTkFont(size=16),
            height=40
        )
        price_entry.pack(pady=(0, 15), padx=20, fill="x")
        
        # Koşul seçimi
        ctk.CTkLabel(
            form_frame,
            text="Alarm Koşulu",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=(10, 5))
        
        condition_var = ctk.StringVar(value="above")
        
        condition_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        condition_frame.pack(pady=(0, 20))
        
        above_radio = ctk.CTkRadioButton(
            condition_frame,
            text="🔺 Fiyat hedefin üstüne çıktığında",
            variable=condition_var,
            value="above",
            font=ctk.CTkFont(size=12)
        )
        above_radio.pack(pady=5)
        
        below_radio = ctk.CTkRadioButton(
            condition_frame,
            text="🔻 Fiyat hedefin altına indiğinde",
            variable=condition_var,
            value="below",
            font=ctk.CTkFont(size=12)
        )
        below_radio.pack(pady=5)
        
        # Butonlar
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(fill="x", pady=(10, 0))
        
        def create_alarm():
            try:
                target_price = float(price_entry.get().replace(',', ''))
                if target_price <= 0:
                    raise ValueError("Fiyat 0'dan büyük olmalı")
                
                # Aynı kripto için aynı fiyat ve koşulda alarm var mı kontrol et
                existing_alarm = any(
                    alarm['crypto_id'] == crypto['id'] and 
                    alarm['target_price'] == target_price and 
                    alarm['condition'] == condition_var.get() and
                    not alarm.get('triggered', False)
                    for alarm in self.alarms
                )
                
                if existing_alarm:
                    messagebox.showwarning("Uyarı", "Bu kripto para için aynı fiyat ve koşulda zaten bir alarm mevcut!")
                    return
                
                alarm = {
                    'id': str(int(time.time() * 1000)),  # Unique ID
                    'crypto_id': crypto['id'],
                    'crypto_name': crypto['name'],
                    'crypto_symbol': crypto['symbol'],
                    'target_price': target_price,
                    'condition': condition_var.get(),
                    'created_at': datetime.now().isoformat(),
                    'triggered': False
                }
                
                self.alarms.append(alarm)
                self.save_alarms()
                
                dialog.destroy()
                messagebox.showinfo("Başarılı", f"✅ {crypto['name']} için alarm kuruldu!")
                
                # UI'yi güncelle
                self.refresh_alarms()
                self.refresh_watchlist()  # Alarm butonunu güncelle
                self.update_stats()
                
            except ValueError:
                messagebox.showerror("Hata", "Lütfen geçerli bir fiyat değeri girin!")
            except Exception as e:
                messagebox.showerror("Hata", f"Alarm oluşturulurken hata: {str(e)}")
        
        cancel_btn = ctk.CTkButton(
            button_frame,
            text="❌ İptal",
            width=120,
            fg_color=("gray50", "gray30"),
            hover_color=("gray40", "gray40"),
            command=dialog.destroy
        )
        cancel_btn.pack(side="left", padx=(0, 10))
        
        create_btn = ctk.CTkButton(
            button_frame,
            text="🔔 Alarm Kur",
            width=120,
            command=create_alarm
        )
        create_btn.pack(side="right")
        
        # Focus'u price entry'ye ver
        price_entry.focus()
    
    def has_active_alarm(self, crypto_id):
        """Aktif alarm kontrolü"""
        return any(
            alarm['crypto_id'] == crypto_id and not alarm.get('triggered', False) 
            for alarm in self.alarms
        )
    
    def refresh_alarms(self):
        """Alarmları yenile"""
        self.clear_alarms()
        
        if not self.alarms:
            self.show_empty_alarms()
            return
        
        # Aktif alarmları önce göster
        active_alarms = [a for a in self.alarms if not a.get('triggered', False)]
        triggered_alarms = [a for a in self.alarms if a.get('triggered', False)]
        
        if active_alarms:
            active_title = ctk.CTkLabel(
                self.alarms_container,
                text="🟢 Aktif Alarmlar",
                font=ctk.CTkFont(size=16, weight="bold"),
                text_color="green"
            )
            active_title.pack(pady=(10, 15))
            
            for alarm in active_alarms:
                self.create_alarm_item(alarm, is_active=True)
        
        if triggered_alarms:
            triggered_title = ctk.CTkLabel(
                self.alarms_container,
                text="🔴 Tetiklenen Alarmlar",
                font=ctk.CTkFont(size=16, weight="bold"),
                text_color="red"
            )
            triggered_title.pack(pady=(20, 15))
            
            for alarm in triggered_alarms:
                self.create_alarm_item(alarm, is_active=False)
    
    def create_alarm_item(self, alarm, is_active=True):
        """Alarm öğesi oluştur"""
        item_frame = ctk.CTkFrame(self.alarms_container, height=100)
        item_frame.pack(fill="x", pady=5)
        item_frame.pack_propagate(False)
        
        # Sol kısım - Bilgiler
        info_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
        info_frame.pack(side="left", fill="both", expand=True, padx=15, pady=15)
        
        # Kripto adı ve sembol
        name_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
        name_frame.pack(fill="x")
        
        name_label = ctk.CTkLabel(
            name_frame,
            text=f"{alarm['crypto_name']} ({alarm['crypto_symbol']})",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        name_label.pack(side="left")
        
        status_emoji = "🟢" if is_active else "🔴"
        status_label = ctk.CTkLabel(
            name_frame,
            text=status_emoji,
            font=ctk.CTkFont(size=16)
        )
        status_label.pack(side="right")
        
        # Alarm detayları
        condition_text = "üstüne çık" if alarm['condition'] == 'above' else "altına in"
        detail_text = f"Hedef: ${self.format_price(alarm['target_price'])} ({condition_text})"
        
        detail_label = ctk.CTkLabel(
            info_frame,
            text=detail_text,
            font=ctk.CTkFont(size=12),
            text_color=("gray60", "gray40")
        )
        detail_label.pack(anchor="w", pady=(5, 0))
        
        # Oluşturma tarihi
        created_date = datetime.fromisoformat(alarm['created_at']).strftime("%d.%m.%Y %H:%M")
        date_label = ctk.CTkLabel(
            info_frame,
            text=f"Oluşturulma: {created_date}",
            font=ctk.CTkFont(size=10),
            text_color=("gray50", "gray50")
        )
        date_label.pack(anchor="w", pady=(5, 0))
        
        # Sağ kısım - Butonlar
        buttons_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
        buttons_frame.pack(side="right", padx=15, pady=15)
        
        if is_active:
            # Düzenleme butonu
            edit_btn = ctk.CTkButton(
                buttons_frame,
                text="✏️",
                width=40,
                height=30,
                fg_color=("gray50", "gray30"),
                command=lambda: self.edit_alarm(alarm)
            )
            edit_btn.pack(pady=2)
        
        # Silme butonu
        delete_btn = ctk.CTkButton(
            buttons_frame,
            text="🗑️",
            width=40,
            height=30,
            fg_color="red",
            hover_color="darkred",
            command=lambda: self.delete_alarm(alarm['id'])
        )
        delete_btn.pack(pady=2)
    
    def edit_alarm(self, alarm):
        """Alarm düzenle"""
        # Mevcut alarmı bul
        crypto_data = {
            'id': alarm['crypto_id'],
            'name': alarm['crypto_name'], 
            'symbol': alarm['crypto_symbol']
        }
        
        current_price = self.current_prices.get(alarm['crypto_id'], {}).get('usd', 0)
        
        # Önce eski alarmı sil
        self.alarms = [a for a in self.alarms if a['id'] != alarm['id']]
        self.save_alarms()
        
        # Yeni alarm dialog'unu aç
        self.show_alarm_dialog(crypto_data, current_price)
    
    def delete_alarm(self, alarm_id):
        """Alarm sil"""
        alarm = next((a for a in self.alarms if a['id'] == alarm_id), None)
        if not alarm:
            return
            
        if messagebox.askyesno("Onay", f"'{alarm['crypto_name']}' alarmını silmek istediğinizden emin misiniz?"):
            self.alarms = [a for a in self.alarms if a['id'] != alarm_id]
            self.save_alarms()
            self.refresh_alarms()
            self.refresh_watchlist()  # Alarm butonlarını güncelle
            self.update_stats()
            messagebox.showinfo("Başarılı", "Alarm silindi!")
    
    def start_price_monitoring(self):
        """Fiyat takibini başlat"""
        def monitor_prices():
            while self.monitoring_active:
                try:
                    self.check_alarms()
                    time.sleep(30)  # 30 saniyede bir kontrol
                except Exception as e:
                    print(f"Monitoring error: {e}")
                    time.sleep(60)
        
        threading.Thread(target=monitor_prices, daemon=True).start()
    
    def check_alarms(self):
        """Alarmları kontrol et"""
        active_alarms = [a for a in self.alarms if not a.get('triggered', False)]
        if not active_alarms:
            return
        
        try:
            crypto_ids = list(set(alarm['crypto_id'] for alarm in active_alarms))
            ids_str = ','.join(crypto_ids)
            
            url = f"https://api.coingecko.com/api/v3/simple/price?ids={ids_str}&vs_currencies=usd"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            price_data = response.json()
            
            for alarm in active_alarms:
                crypto_price = price_data.get(alarm['crypto_id'], {}).get('usd')
                if not crypto_price:
                    continue
                
                should_trigger = False
                if alarm['condition'] == 'above' and crypto_price >= alarm['target_price']:
                    should_trigger = True
                elif alarm['condition'] == 'below' and crypto_price <= alarm['target_price']:
                    should_trigger = True
                
                if should_trigger:
                    alarm['triggered'] = True
                    alarm['triggered_at'] = datetime.now().isoformat()
                    alarm['triggered_price'] = crypto_price
                    self.save_alarms()
                    
                    # Bildirimler
                    self.play_notification_sound(alarm['condition'] == 'above')
                    
                    condition_text = "hedefin üstüne çıktı" if alarm['condition'] == 'above' else "hedefin altına indi"
                    message = (f"🔔 ALARM TETİKLENDİ!\n\n"
                              f"{alarm['crypto_name']} {condition_text}!\n\n"
                              f"Hedef Fiyat: ${self.format_price(alarm['target_price'])}\n"
                              f"Güncel Fiyat: ${self.format_price(crypto_price)}")
                    
                    self.root.after(0, lambda m=message: messagebox.showinfo("🔔 Alarm Tetiklendi", m))
                    self.root.after(0, self.refresh_alarms)
                    self.root.after(0, self.update_stats)
                    
        except Exception as e:
            print(f"Alarm check error: {e}")
    
    def play_notification_sound(self, is_positive=True):
        """Cross-platform bildirim sesi"""
        try:
            system = platform.system()
            
            if system == "Darwin":  # macOS
                sound_file = "/System/Library/Sounds/Glass.aiff" if is_positive else "/System/Library/Sounds/Basso.aiff"
                subprocess.run(["afplay", sound_file], check=False)
                
            elif system == "Windows":
                import winsound
                if is_positive:
                    winsound.Beep(1000, 300)
                else:
                    winsound.Beep(500, 300)
                    
            elif system == "Linux":
                subprocess.run(["paplay", "/usr/share/sounds/alsa/Front_Left.wav"], check=False)
                
        except Exception as e:
            print(f"Ses çalma hatası: {e}")
            try:
                print("\a")  # Terminal bell
            except:
                pass
    
    def update_stats(self):
        """İstatistikleri güncelle"""
        self.root.after(0, self.setup_ui)  # Header'ı yenile
    
    # Yardımcı metodlar
    def clear_search_results(self):
        for widget in self.search_results_frame.winfo_children():
            widget.destroy()
    
    def clear_watchlist(self):
        for widget in self.watchlist_container.winfo_children():
            widget.destroy()
    
    def clear_alarms(self):
        for widget in self.alarms_container.winfo_children():
            widget.destroy()
    
    def show_empty_watchlist(self):
        self.clear_watchlist()
        empty_frame = ctk.CTkFrame(self.watchlist_container, height=200)
        empty_frame.pack(fill="both", expand=True, pady=50)
        
        ctk.CTkLabel(
            empty_frame,
            text="📊",
            font=ctk.CTkFont(size=48)
        ).pack(pady=(50, 20))
        
        ctk.CTkLabel(
            empty_frame,
            text="İzleme listeniz boş",
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(pady=(0, 10))
        
        ctk.CTkLabel(
            empty_frame,
            text="Yukarıdaki arama bölümünden kripto para arayarak\nizleme listesine ekleyebilirsiniz",
            font=ctk.CTkFont(size=14),
            text_color=("gray50", "gray50")
        ).pack()
    
    def show_empty_alarms(self):
        self.clear_alarms()
        empty_frame = ctk.CTkFrame(self.alarms_container, height=200)
        empty_frame.pack(fill="both", expand=True, pady=50)
        
        ctk.CTkLabel(
            empty_frame,
            text="🔔",
            font=ctk.CTkFont(size=48)
        ).pack(pady=(50, 20))
        
        ctk.CTkLabel(
            empty_frame,
            text="Henüz alarm kurulmamış",
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(pady=(0, 10))
        
        ctk.CTkLabel(
            empty_frame,
            text="İzleme listesindeki kripto paralar için alarm kurabilir\nveya '+ Yeni' butonuna tıklayabilirsiniz",
            font=ctk.CTkFont(size=14),
            text_color=("gray50", "gray50")
        ).pack()
    
    def show_error(self, message):
        messagebox.showerror("Hata", message)
    
    def show_watchlist_error(self, error_msg):
        self.clear_watchlist()
        error_frame = ctk.CTkFrame(self.watchlist_container, height=100)
        error_frame.pack(fill="x", pady=20)
        
        ctk.CTkLabel(
            error_frame,
            text="❌ Fiyat verisi yüklenemedi",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="red"
        ).pack(pady=(20, 5))
        
        ctk.CTkLabel(
            error_frame,
            text=f"Hata: {error_msg}",
            font=ctk.CTkFont(size=12),
            text_color=("gray50", "gray50")
        ).pack(pady=(0, 20))
    
    # Veri saklama metodları
    def load_watchlist(self):
        try:
            with open('crypto_watchlist.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    
    def save_watchlist(self):
        try:
            with open('crypto_watchlist.json', 'w', encoding='utf-8') as f:
                json.dump(self.watchlist, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Watchlist save error: {e}")
    
    def load_alarms(self):
        try:
            with open('crypto_alarms.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    
    def save_alarms(self):
        try:
            with open('crypto_alarms.json', 'w', encoding='utf-8') as f:
                json.dump(self.alarms, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Alarms save error: {e}")
    
    def run(self):
        """Uygulamayı başlat"""
        def on_closing():
            self.monitoring_active = False
            self.root.destroy()
        
        self.root.protocol("WM_DELETE_WINDOW", on_closing)
        
        # Pencere icon'u (isteğe bağlı)
        try:
            self.root.iconname("🚀")
        except:
            pass
        
        self.root.mainloop()

if __name__ == "__main__":
    app = ModernCryptoApp()
    app.run()
