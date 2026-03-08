"""
PalCloudy Main Window
Libadwaita (Adw) tabanlı ana pencere ve uygulama yönetimi
✅ Libadwaita 1.8.4 uyumlu
"""

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Gtk, Adw, Gio, GLib
from ui.dashboard import DashboardPage
from core.auth_handler import get_auth_handler


class PalCloudyWindow(Adw.ApplicationWindow):
    """
    PalCloudy ana penceresi.
    Giriş sayfası, dashboard ve navigasyon içerir.
    """

    def __init__(self, app, **kwargs):
        """
        Pencereyi başlat.

        Args:
            app: Adw.Application örneği
            **kwargs: Ek parametreler
        """
        super().__init__(**kwargs)

        self.app = app
        self.set_application(app)
        self.auth_handler = get_auth_handler()

        # Pencere özellikleri
        self.set_title("PalCloudy - OVH Cloud Management")
        self.set_default_size(1200, 700)

        # Header bar
        header_bar = Adw.HeaderBar()

        # Title widget
        title_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        title = Gtk.Label()
        title.set_markup("<b>PalCloudy</b>")
        title.add_css_class("title-1")
        subtitle = Gtk.Label()
        subtitle.set_text("OVH Cloud Management Panel")
        subtitle.add_css_class("dim-label")
        title_box.append(title)
        title_box.append(subtitle)
        header_bar.set_title_widget(title_box)

        # Menu button (hamburger)
        menu_button = Gtk.MenuButton()
        menu_button.set_icon_name("open-menu-symbolic")
        header_bar.pack_end(menu_button)

        # Main layout (NavigationSplitView)
        split_view = Adw.NavigationSplitView()

        # Sol sidebar (navigation)
        sidebar_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        sidebar_box.set_spacing(12)
        sidebar_box.set_margin_top(12)
        sidebar_box.set_margin_bottom(12)
        sidebar_box.set_margin_start(12)
        sidebar_box.set_margin_end(12)
        sidebar_box.set_vexpand(True)  # ← Tüm pencereyi kapla

        # Header/Title
        header_container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        header_container.set_spacing(8)

        # Logo/başlık
        logo_label = Gtk.Label()
        logo_label.set_markup("<b>Hesaplar</b>")
        header_container.append(logo_label)

        # Scrollable list area (kaydedilmiş hesaplarla doldur)
        self.accounts_list = Gtk.ListBox()
        self.accounts_list.set_selection_mode(Gtk.SelectionMode.SINGLE)
        self.accounts_list.add_css_class("navigation-sidebar")
        self.accounts_list.set_vexpand(True)  # ← Kalan alanı kapla

        # Kaydedilmiş hesapları sidebar'a ekle
        accounts = self.auth_handler.list_credentials()
        for account in accounts:
            account_button = Gtk.Button()
            account_button.set_label(f"👤 {account['nickname']}")
            account_button.set_halign(Gtk.Align.FILL)
            account_button.connect("clicked", self.on_sidebar_account_clicked, account['id'])
            self.accounts_list.append(account_button)

        scrolled = Gtk.ScrolledWindow()
        scrolled.set_child(self.accounts_list)
        scrolled.set_vexpand(True)  # ← ScrolledWindow da expand et
        header_container.append(scrolled)

        sidebar_box.append(header_container)
        header_container.set_vexpand(True)  # ← Header container expand et

        # Footer butonları (aşağıya sabitlenmeli)
        footer_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        footer_box.set_spacing(8)

        add_button = Gtk.Button()
        add_button.set_label("➕ Hesap Ekle")
        add_button.set_halign(Gtk.Align.FILL)
        add_button.connect("clicked", self.on_add_account_clicked)
        footer_box.append(add_button)

        settings_button = Gtk.Button()
        settings_button.set_label("⚙️ Ayarlar")
        settings_button.set_halign(Gtk.Align.FILL)
        settings_button.connect("clicked", self.on_settings_clicked)
        footer_box.append(settings_button)

        sidebar_box.append(footer_box)

        # Sidebar'ı split view'a ekle
        sidebar_scrolled = Gtk.ScrolledWindow()
        sidebar_scrolled.set_child(sidebar_box)
        sidebar_scrolled.set_size_request(280, -1)

        # NavigationPage ile sarmalayıp set_sidebar'a pass et
        sidebar_page = Adw.NavigationPage(child=sidebar_scrolled, title="Hesaplar")
        split_view.set_sidebar(sidebar_page)

        # Ana content area (placeholder)
        self.content_stack = Gtk.Stack()
        self.content_stack.set_transition_type(
            Gtk.StackTransitionType.SLIDE_LEFT_RIGHT
        )

        # Placeholder: Hesap seçin
        placeholder = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        placeholder.set_spacing(12)
        placeholder.set_halign(Gtk.Align.CENTER)
        placeholder.set_valign(Gtk.Align.CENTER)

        icon = Gtk.Image.new_from_icon_name("dialog-information-symbolic")
        icon.set_pixel_size(96)
        placeholder.append(icon)

        placeholder_label = Gtk.Label()
        placeholder_label.set_markup(
            "<b>Hesap Seçin</b>\n"
            "Sol taraftan bir hesap seçin veya yeni hesap ekleyin"
        )
        placeholder_label.set_justify(Gtk.Justification.CENTER)
        placeholder.append(placeholder_label)

        self.content_stack.add_named(placeholder, "placeholder")

        # Dashboard sayfası
        dashboard = DashboardPage(on_account_selected=self.on_account_selected)
        dashboard_page = Adw.NavigationPage(child=dashboard, title="Dashboard")
        self.content_stack.add_named(dashboard, "dashboard")
        self.content_stack.set_visible_child_name("dashboard")

        # Content page'i oluştur
        content_page = Adw.NavigationPage(child=self.content_stack, title="Dashboard")
        split_view.set_content(content_page)

        # Layout oluştur
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        main_box.append(header_bar)
        main_box.append(split_view)

        self.set_content(main_box)

        # CSS styling
        self._apply_css()

    def _apply_css(self):
        """Uygulanacak CSS styling."""
        css_provider = Gtk.CssProvider()
        css_data = b"""
            .navigation-sidebar {
                background-color: @window_bg_color;
            }

            .title-1 {
                font-size: 18px;
                font-weight: 600;
            }

            button {
                padding: 8px 12px;
                border-radius: 6px;
            }
        """
        css_provider.load_from_data(css_data)

        Gtk.StyleContext.add_provider_for_display(
            self.get_display(),
            css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

    def on_add_account_clicked(self, button):
        """Hesap ekleme dialogu açı."""
        print("📝 Hesap ekleme penceresi açılacak...")
        try:
            # Login sayfasını göster
            if hasattr(self.app, '_show_login_window'):
                self.app._show_login_window()
            else:
                print("❌ _show_login_window metodu bulunamadı")
        except Exception as e:
            print(f"❌ Hesap ekle hatası: {e}")
            import traceback
            traceback.print_exc()

    def on_settings_clicked(self, button):
        """Ayarlar penceresini aç."""
        print("⚙️ Ayarlar penceresini açıyor...")

        # Settings dialog oluştur
        settings_dialog = Adw.Window()
        settings_dialog.set_title("Ayarlar")
        settings_dialog.set_modal(True)
        settings_dialog.set_transient_for(self)
        settings_dialog.set_default_size(400, 300)

        # İçerik
        settings_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        settings_box.set_spacing(12)
        settings_box.set_margin_top(12)
        settings_box.set_margin_bottom(12)
        settings_box.set_margin_start(12)
        settings_box.set_margin_end(12)

        # Header
        header = Adw.HeaderBar()
        settings_box.append(header)

        # Placeholder
        placeholder = Gtk.Label()
        placeholder.set_markup("<b>Ayarlar</b>\n\nFaz 3'te eklenecek:\n• Tema seçimi\n• Dil ayarları\n• Credential yönetimi")
        placeholder.set_justify(Gtk.Justification.CENTER)
        settings_box.append(placeholder)

        # Close button
        close_button = Gtk.Button()
        close_button.set_label("Kapat")
        close_button.set_halign(Gtk.Align.CENTER)
        close_button.connect("clicked", lambda x: settings_dialog.close())
        settings_box.append(close_button)

        settings_dialog.set_content(settings_box)
        settings_dialog.present()

    def on_account_selected(self, account_id):
        """Hesap seçildi."""
        credential = self.auth_handler.get_credential(account_id)
        if credential:
            print(f"💫 Hesap değiştirildi: {credential['nickname']}")

    def on_sidebar_account_clicked(self, button, account_id):
        """Sidebar'da hesap tıklandı."""
        credential = self.auth_handler.get_credential(account_id)
        if credential:
            print(f"👤 Sidebar'dan hesap seçildi: {credential['nickname']}")
            self.on_account_selected(account_id)


class PalCloudyApp(Adw.Application):
    """
    PalCloudy ana uygulaması (Adw.Application).
    """

    def __init__(self, **kwargs):
        """
        Uygulamayı başlat.

        Args:
            **kwargs: Ek parametreler
        """
        super().__init__(**kwargs)

        # Uygulama ID (benzersiz tanımlayıcı)
        self.set_application_id("io.github.palcloudy")

        # Sinyal bağlantıları
        self.connect("activate", self.on_activate)
        self.connect("startup", self.on_startup)

    def on_startup(self, app):
        """Uygulama başlangıcında çalışır."""
        pass

    def on_activate(self, app):
        """
        Uygulama etkinleştirildiğinde çalışır.
        Pencereyi göster/ön plana al.
        """
        window = self.get_active_window()

        if window is None:
            window = PalCloudyWindow(self)

        window.present()


def launch_app():
    """Uygulamayı başlat."""
    app = PalCloudyApp()
    return app.run()
