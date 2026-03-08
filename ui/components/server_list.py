"""
PalCloudy - UI: Server List View
Gtk4 TreeView tabanlı sunucu listesi gösterimi
"""

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Gtk, Adw, GLib
from typing import List, Dict, Any, Optional, Callable
import logging

logger = logging.getLogger(__name__)


class ServerListView(Gtk.Box):
    """
    Sunucuların listesini TreeView'da göster.
    
    Özellikleri:
    - Sortable columns
    - Searchable/Filterable
    - Right-click context menu
    - Status color coding
    
    Örnek Kullanım:
        >>> list_view = ServerListView(on_server_selected=self.on_server_selected)
        >>> list_view.load_servers(servers_data)
        >>> window.add_child(list_view)
    """
    
    def __init__(self, on_server_selected: Optional[Callable] = None, **kwargs):
        """
        Server List View'ı başlat.
        
        Args:
            on_server_selected: Sunucu seçilince çağrılacak callback
            **kwargs: Ek parametreler
        """
        super().__init__(orientation=Gtk.Orientation.VERTICAL, **kwargs)
        
        self.on_server_selected = on_server_selected
        self.servers: List[Dict[str, Any]] = []
        self.set_spacing(12)
        self.set_margin_top(12)
        self.set_margin_bottom(12)
        self.set_margin_start(12)
        self.set_margin_end(12)
        
        logger.info("✅ ServerListView başlatıldı")
        
        # Header: Başlık ve arama
        self._build_header()
        
        # TreeView
        self._build_treeview()
        
        # Footer: Bilgi
        self._build_footer()
    
    def _build_header(self):
        """Başlık ve arama çubuğu oluştur"""
        header_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        header_box.set_spacing(12)
        
        # Başlık
        title_label = Gtk.Label()
        title_label.set_markup("<b>Sunucularım</b>")
        title_label.set_hexpand(True)
        header_box.append(title_label)
        
        # Arama
        self.search_entry = Gtk.SearchEntry()
        self.search_entry.set_placeholder_text("Ara...")
        self.search_entry.set_width_chars(20)
        self.search_entry.connect("search-changed", self._on_search_changed)
        header_box.append(self.search_entry)
        
        self.append(header_box)
    
    def _build_treeview(self):
        """TreeView oluştur"""
        # TreeStore: name, ip, state, os, cpu%, ram%, disk%, state_color
        self.store = Gtk.ListStore(
            str,  # 0: Name
            str,  # 1: IP
            str,  # 2: State
            str,  # 3: OS
            str,  # 4: CPU%
            str,  # 5: RAM%
            str,  # 6: Disk%
            str,  # 7: State Color
        )
        
        # TreeView
        self.treeview = Gtk.TreeView(model=self.store)
        self.treeview.set_vexpand(True)
        self.treeview.set_hexpand(True)
        self.treeview.set_enable_search(False)
        self.treeview.connect("row-activated", self._on_row_activated)
        
        # Columns
        self._add_columns()
        
        # Scrolled Window
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_child(self.treeview)
        scrolled.set_vexpand(True)
        
        self.append(scrolled)
    
    def _add_columns(self):
        """TreeView sütunlarını ekle"""
        columns = [
            ("Name", 0, 150),
            ("IP", 1, 120),
            ("State", 2, 80),
            ("OS", 3, 150),
            ("CPU%", 4, 60),
            ("RAM%", 5, 60),
            ("Disk%", 6, 60),
        ]
        
        for title, idx, width in columns:
            # Cell Renderer
            renderer = Gtk.CellRendererText()
            
            # Column
            column = Gtk.TreeViewColumn(title, renderer, text=idx)
            column.set_resizable(True)
            column.set_fixed_width(width)
            column.set_sizing(Gtk.TreeViewColumnSizing.FIXED)
            
            # State column için renk desteği
            if title == "State":
                renderer.set_property("background-set", True)
                column.set_cell_data_func(renderer, self._set_state_color)
            
            # Sortable
            column.set_sort_column_id(idx)
            
            self.treeview.append_column(column)
    
    def _set_state_color(self, column, renderer, store, iter, data=None):
        """State column'unda renk ayarla"""
        state = store.get_value(iter, 2)
        
        if state == "ok":
            renderer.set_property("background", "#4CAF50")  # Green
            renderer.set_property("foreground", "white")
        elif state == "maintenance":
            renderer.set_property("background", "#FFC107")  # Yellow
            renderer.set_property("foreground", "black")
        elif state == "error":
            renderer.set_property("background", "#F44336")  # Red
            renderer.set_property("foreground", "white")
        else:
            renderer.set_property("background-set", False)
    
    def _build_footer(self):
        """Footer: İstatistikler"""
        footer_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        footer_box.set_spacing(12)
        
        # İstatistikler
        self.stats_label = Gtk.Label()
        self.stats_label.set_text("0 sunucu")
        self.stats_label.add_css_class("dim-label")
        footer_box.append(self.stats_label)
        
        self.append(footer_box)
    
    def load_servers(self, servers: List[Dict[str, Any]]):
        """
        Sunucuları yükle.
        
        Args:
            servers: Sunucu listesi
            [
                {
                    'name': 'ns123456.ip-1-2-3.eu',
                    'ip': '1.2.3.4',
                    'state': 'ok',
                    'os': 'Debian 11',
                    'cpu': 45,
                    'ram': 75,
                    'disk': 60,
                },
                ...
            ]
        """
        self.servers = servers
        self.store.clear()
        
        for server in servers:
            self.store.append([
                server.get('name', 'Unknown'),
                server.get('ip', 'N/A'),
                server.get('state', 'unknown'),
                server.get('os', 'Unknown'),
                f"{server.get('cpu', 0):.0f}%",
                f"{server.get('ram', 0):.0f}%",
                f"{server.get('disk', 0):.0f}%",
                server.get('state', 'unknown'),
            ])
        
        self._update_stats()
        logger.info(f"✅ {len(servers)} sunucu yüklendi")
    
    def _update_stats(self):
        """İstatistikleri güncelle"""
        count = len(self.servers)
        self.stats_label.set_text(f"{count} sunucu")
    
    def _on_row_activated(self, treeview, path, column):
        """Sunucu satırına tıklandı"""
        iter = self.store.get_iter(path)
        if iter:
            server_name = self.store.get_value(iter, 0)
            logger.info(f"👤 Sunucu seçildi: {server_name}")
            
            if self.on_server_selected:
                self.on_server_selected(server_name)
    
    def _on_search_changed(self, entry):
        """Arama metni değişti"""
        search_text = entry.get_text().lower()
        
        # Filtreleme yapılabilir - şimdilik tüm sunucuları göster
        # TODO: Implement filtering
        logger.debug(f"🔍 Arama: {search_text}")
    
    def get_selected_server(self) -> Optional[Dict[str, Any]]:
        """Seçilen sunucuyu al"""
        selection = self.treeview.get_selection()
        if selection:
            model, iter = selection.get_selected()
            if iter:
                name = model.get_value(iter, 0)
                # Servers listesinde bul
                for server in self.servers:
                    if server['name'] == name:
                        return server
        return None
    
    def refresh(self):
        """Listesini yenile"""
        self.load_servers(self.servers)


# Örnek veri
EXAMPLE_SERVERS = [
    {
        'name': 'ns123456.ip-1-2-3.eu',
        'ip': '1.2.3.4',
        'state': 'ok',
        'os': 'Debian 11 (64)',
        'cpu': 25.5,
        'ram': 65.3,
        'disk': 48.7,
    },
    {
        'name': 'ns654321.ip-5-6-7.eu',
        'ip': '5.6.7.8',
        'state': 'ok',
        'os': 'CentOS 7',
        'cpu': 45.2,
        'ram': 82.1,
        'disk': 71.3,
    },
    {
        'name': 'ns999999.ip-9-10-11.eu',
        'ip': '9.10.11.12',
        'state': 'maintenance',
        'os': 'Ubuntu 20.04',
        'cpu': 0,
        'ram': 0,
        'disk': 0,
    },
]
