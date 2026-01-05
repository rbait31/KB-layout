import sys
import ctypes
from ctypes import wintypes
from threading import Thread
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QObject
from PyQt5.QtGui import QFont
from pynput import keyboard


class KeyboardSignal(QObject):
    key_pressed = pyqtSignal()


class LanguageIndicator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(
            Qt.WindowStaysOnTopHint |
            Qt.FramelessWindowHint |
            Qt.Tool |
            Qt.WindowTransparentForInput
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setStyleSheet("background-color: transparent;")
        
        # Получаем размер экрана
        screen = QApplication.primaryScreen().geometry()
        window_width = 60
        window_height = 60
        x = screen.width() - window_width - 20
        y = 20
        
        self.setGeometry(x, y, window_width, window_height)
        
        # Создаем метку для отображения языка
        self.label = QLabel("", self)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("color: white; background-color: rgba(100, 100, 100, 200); border-radius: 5px;")
        font = QFont("Arial", 24, QFont.Bold)
        self.label.setFont(font)
        self.label.setGeometry(0, 0, window_width, window_height)
        
        # Таймер для скрытия индикатора
        self.hide_timer = QTimer()
        self.hide_timer.setSingleShot(True)
        self.hide_timer.timeout.connect(self.hide_indicator)
        
        # Сигнал для обработки нажатий клавиш из другого потока
        self.keyboard_signal = KeyboardSignal()
        self.keyboard_signal.key_pressed.connect(self.update_language)
        
        # Запускаем хук клавиатуры в отдельном потоке
        self.start_keyboard_listener()
        
        # Изначально скрыто
        self.hide()
    
    def get_keyboard_language(self):
        """Получает текущий язык клавиатуры через Win32 API"""
        try:
            # Получаем handle активного окна
            hwnd = ctypes.windll.user32.GetForegroundWindow()
            if hwnd == 0:
                return "??"
            
            # Получаем thread ID
            thread_id = ctypes.windll.user32.GetWindowThreadProcessId(hwnd, None)
            
            # Получаем keyboard layout
            layout = ctypes.windll.user32.GetKeyboardLayout(thread_id)
            
            # Извлекаем language ID (младшие 16 бит)
            lang_id = layout & 0xFFFF
            
            # Маппинг language ID на названия языков
            lang_map = {
                0x0409: "EN",  # English (United States)
                0x0419: "RU",  # Russian
                0x0407: "DE",  # German
                0x040C: "FR",  # French
                0x0410: "IT",  # Italian
                0x0405: "CZ",  # Czech
                0x0415: "PL",  # Polish
                0x0416: "PT",  # Portuguese (Brazil)
                0x0412: "KO",  # Korean
                0x0411: "JA",  # Japanese
                0x0804: "ZH",  # Chinese (Simplified)
                0x0404: "ZH",  # Chinese (Traditional)
                0x0413: "NL",  # Dutch
                0x0406: "DA",  # Danish
                0x040B: "FI",  # Finnish
                0x040E: "HU",  # Hungarian
                0x0414: "NO",  # Norwegian
                0x041D: "SV",  # Swedish
                0x0418: "RO",  # Romanian
                0x041F: "TR",  # Turkish
                0x0422: "UK",  # Ukrainian
                0x0427: "LT",  # Lithuanian
                0x0426: "LV",  # Latvian
                0x0425: "ET",  # Estonian
            }
            
            return lang_map.get(lang_id, f"{hex(lang_id)}")
        except Exception as e:
            print(f"Ошибка получения языка: {e}")
            return "??"
    
    def update_language(self):
        """Обновляет отображаемый язык клавиатуры"""
        lang = self.get_keyboard_language()
        self.label.setText(lang)
        
        # Устанавливаем цветной квадратик в зависимости от языка
        if lang == "RU":
            # Зеленый для русского
            self.label.setStyleSheet("color: white; background-color: rgba(76, 175, 80, 230); border-radius: 5px;")
        elif lang == "EN":
            # Синий для английского
            self.label.setStyleSheet("color: white; background-color: rgba(33, 150, 243, 230); border-radius: 5px;")
        else:
            # Серый для других языков
            self.label.setStyleSheet("color: white; background-color: rgba(100, 100, 100, 200); border-radius: 5px;")
        
        self.show()
        self.raise_()
        self.activateWindow()
        
        # Перезапускаем таймер скрытия
        self.hide_timer.stop()
        self.hide_timer.start(1500)  # Скрываем через 1.5 секунды
    
    def hide_indicator(self):
        """Скрывает индикатор"""
        self.hide()
    
    def on_press(self, key):
        """Обработчик нажатия клавиши"""
        try:
            # Игнорируем только служебные клавиши (Ctrl, Alt, Shift, Windows, etc.)
            ignore_keys = {
                keyboard.Key.ctrl_l, keyboard.Key.ctrl_r,
                keyboard.Key.alt_l, keyboard.Key.alt_r,
                keyboard.Key.shift_l, keyboard.Key.shift_r,
                keyboard.Key.cmd, keyboard.Key.cmd_l, keyboard.Key.cmd_r,
                keyboard.Key.menu,
                keyboard.Key.caps_lock, keyboard.Key.num_lock, keyboard.Key.scroll_lock
            }
            
            if key not in ignore_keys:
                # Любая другая клавиша - обновляем язык
                self.keyboard_signal.key_pressed.emit()
        except Exception:
            pass
    
    def start_keyboard_listener(self):
        """Запускает глобальный хук клавиатуры в отдельном потоке"""
        def listener_thread():
            with keyboard.Listener(on_press=self.on_press) as listener:
                listener.join()
        
        thread = Thread(target=listener_thread, daemon=True)
        thread.start()


def main():
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    
    window = LanguageIndicator()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
