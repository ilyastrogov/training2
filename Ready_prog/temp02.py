import sys
import os
import fitz  # PyMuPDF
from pathlib import Path

# PyQt5 импорты
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QTextEdit, QSplitter,
    QVBoxLayout, QWidget, QFileDialog, QMessageBox, QLabel,
    QPushButton, QHBoxLayout, QGroupBox, QSpinBox, QComboBox, QScrollArea,
    QDialog, QDialogButtonBox, QSizePolicy, QFontDialog, QToolBar, QAction
)
from PyQt5.QtGui import QFont, QTextCharFormat, QFontDatabase, QTextCursor, QPixmap
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtPrintSupport import QPrinter

from abc import ABC, abstractmethod


# ==========================================
# Абстрактные базовые классы (заглушки для совместимости)
# ==========================================
class AddLayout(ABC):
    @abstractmethod
    def create_layout(self, arg=None): pass

    @abstractmethod
    def add_layout(self): pass


# class CreateTabWidget(ABC):
#     @abstractmethod
#     def create_tab_widget(self, close_tab): pass


class CreateNewTab(ABC):
    @abstractmethod
    def create_new_tab(self, title): pass

    # @abstractmethod
    # def calculate_pdf_page_size(self, dpi=96): pass


class SavePdf(ABC):
    @abstractmethod
    def save_as_pdf(self): pass


class CloseTab(ABC):
    @abstractmethod
    def close_tab(self, index): pass


class PDFFontMapper(ABC):
    @abstractmethod
    def normalize_font_name(self, pdf_font_name): pass

    @abstractmethod
    def load_font_to_database(self, font_path): pass

    @abstractmethod
    def find_matching_font(self, pdf_font_name): pass

    @abstractmethod
    def create_qt_font_from_pdf_span(self, span_data): pass

    @abstractmethod
    def analyze_and_map_fonts(self, filepath): pass


# ==========================================
# Диалог выбора шрифта из папки
# ==========================================
class FontListDialog(QDialog):
    def __init__(self, folder_path, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Выбор шрифта (папка)")
        self.selected_font = None
        self.folder_path = Path(folder_path)

        self.loaded_families = []
        self.families_with_styles = {}
        self.db = QFontDatabase()

        # Загрузка шрифтов из папки
        if self.folder_path.exists():
            for file in self.folder_path.iterdir():
                if file.suffix.lower() in {'.ttf', '.otf'}:
                    idx = self.db.addApplicationFont(str(file))
                    if idx != -1:
                        families = self.db.applicationFontFamilies(idx)
                        for fam in families:
                            self.families_with_styles[fam] = self.db.styles(fam)
                            if fam not in self.loaded_families:
                                self.loaded_families.append(fam)

        if not self.loaded_families:
            QMessageBox.warning(self, "Шрифты не найдены", "В папке нет .ttf/.otf файлов.")
            self.reject()
            return

        # UI
        main_layout = QVBoxLayout()

        # Семейство
        family_group = QGroupBox("Семейство шрифта")
        family_layout = QVBoxLayout()
        lbl_family = QLabel("Выберите шрифт:")
        self.combo_family = QComboBox()
        self.combo_family.addItems(self.loaded_families)
        family_layout.addWidget(lbl_family)
        family_layout.addWidget(self.combo_family)
        family_group.setLayout(family_layout)
        main_layout.addWidget(family_group)

        # Размер
        size_group = QGroupBox("Размер шрифта")
        size_layout = QHBoxLayout()
        lbl_size = QLabel("Размер:")
        self.spin_size = QSpinBox()
        self.spin_size.setRange(8, 144)
        self.spin_size.setValue(12)
        size_layout.addWidget(lbl_size)
        size_layout.addWidget(self.spin_size)
        size_group.setLayout(size_layout)
        main_layout.addWidget(size_group)

        # Стиль (Bold/Italic и т.д.)
        style_group = QGroupBox("Начертание")
        style_layout = QHBoxLayout()
        style_layout.addSpacing(20)
        style_layout.addWidget(QLabel("Начертание:"))
        self.combo_style = QComboBox()
        first_fam = self.combo_family.currentText()
        if first_fam in self.families_with_styles:
            self.combo_style.addItems(self.families_with_styles[first_fam])
        else:
            self.combo_style.addItem("Normal")
        style_layout.addWidget(self.combo_style)
        style_group.setLayout(style_layout)
        main_layout.addWidget(style_group)

        # Предпросмотр
        preview_group = QGroupBox("Предпросмотр")
        preview_layout = QVBoxLayout()
        self.preview_label = QLabel("AaBbCcDdEe FfGgHhIiJj\n0123456789 !@#$%^&*()")
        self.preview_label.setStyleSheet("border: 1px solid #ccc; padding: 8px; background: white;")
        self.preview_label.setMinimumHeight(60)
        preview_layout.addWidget(self.preview_label)
        preview_group.setLayout(preview_layout)
        main_layout.addWidget(preview_group)

        # Кнопки
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        main_layout.addWidget(buttons)

        self.setLayout(main_layout)

        # Сигналы
        self.combo_family.currentTextChanged.connect(self._update_style_options)
        self.combo_family.currentTextChanged.connect(self._update_preview)
        self.spin_size.valueChanged.connect(self._update_preview)
        self.combo_style.currentTextChanged.connect(self._update_preview)

        self._update_preview()

    def _update_style_options(self, family: str):
        if family in self.families_with_styles:
            self.combo_style.clear()
            self.combo_style.addItems(self.families_with_styles[family])

    def _update_preview(self):
        fam = self.combo_family.currentText()
        size = self.spin_size.value()
        style = self.combo_style.currentText()

        f = QFont(fam, size)
        lower = style.lower()
        if "bold" in lower:
            f.setWeight(QFont.Weight.Bold)
        elif "italic" in lower or "курсив" in lower:
            f.setItalic(True)
        elif "light" in lower:
            f.setWeight(QFont.Weight.Light)
        elif "medium" in lower:
            f.setWeight(QFont.Weight.Medium)
        else:
            f.setWeight(QFont.Weight.Normal)

        self.preview_label.setFont(f)

    def get_selected_font(self) -> QFont:
        fam = self.combo_family.currentText()
        size = self.spin_size.value()
        style = self.combo_style.currentText().lower()

        f = QFont(fam, size)
        if "bold" in style:
            f.setWeight(QFont.Weight.Bold)
        if "italic" in style or "курсив" in style:
            f.setItalic(True)
        if "light" in style:
            f.setWeight(QFont.Weight.Light)
        if "medium" in style:
            f.setWeight(QFont.Weight.Medium)
        return f


# ==========================================
# Основное окно приложения
# ==========================================
class WindowConfigurator(
    AddLayout, CreateNewTab,
    SavePdf, CloseTab, PDFFontMapper
):
    def __init__(self):
        self.central_widget = None
        self.layout = None
        self.text_edit = None  # редактор текста (справа)
        self.pdf_viewer = None  # просмотр PDF (слева)
        self.font_db = QFontDatabase()

        # ✅ ГЛАВНОЕ: Создаём таб-виджет сразу при инициализации
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.tabCloseRequested.connect(self.close_tab)

    # --- Layout ---
    def create_layout(self, arg=None):
        self.layout = QVBoxLayout(arg) if arg else QVBoxLayout()
        return self.layout

    def add_layout(self):
        if not self.layout:
            self.layout = self.create_layout()
        if not self.central_widget:
            self.central_widget = self.create_central_widget()

        self.layout.addWidget(self.tab_widget)
        self.central_widget.setLayout(self.layout)
        return self.central_widget

    # def calculate_pdf_page_size(self, dpi=96):
    #
    #     a4_width_mm = 210
    #     a4_height_mm = 297
    #     a4_width_inches = a4_width_mm / 25.4
    #     a4_height_inches = a4_height_mm / 25.4
    #     return int(a4_width_inches * dpi), int(a4_height_inches * dpi)
    #     def create_tab_widget(self, close_tab):
    #         self.tab_widget = self.create_widget()
    #         self.tab_widget.setTabsClosable(True)
    #         self.tab_widget.tabCloseRequested.connect(close_tab)
    #         return self.tab_widget

    def create_central_widget(self):
        self.central_widget = QWidget()
        return self.central_widget

    # --- Табы ---
    def close_tab(self, index):
        self.tab_widget.removeTab(index)

    # --- Новая вкладка ---
    # def create_new_tab(self, title: str):
    #     # Проверка на случай, если таб виджет всё-таки не создан (защита)
    #     if self.tab_widget is None:
    #         QMessageBox.critical(None, "Ошибка", "QTabWidget не инициализирован!")
    #         return None
    #
    #     tab_container = QWidget()
    #     layout = QVBoxLayout(tab_container)
    #     layout.setContentsMargins(0, 0, 0, 0)
    #
    #     splitter = QSplitter(Qt.Horizontal)
    #     splitter.setStretchFactor(0, 3)  # PDF 75%
    #     splitter.setStretchFactor(1, 1)  # Редактор 25%
    #
    #     # 1. Просмотр PDF
    #     self.pdf_viewer = QWebEngineView()
    #     self.pdf_viewer.setHtml("<h3>Здесь отобразится PDF с картинками и линиями</h3>")
    #     splitter.addWidget(self.pdf_viewer)
    #
    #     # 2. Редактор текста
    #     edit_panel = QWidget()
    #     edit_layout = QVBoxLayout(edit_panel)
    #     edit_layout.setContentsMargins(5, 5, 5, 5)
    #
    #     info_lbl = QLabel(
    #         "1. Откройте PDF — он появится слева.\n"
    #         "2. Выделите текст в левой панели и скопируйте (Ctrl+C).\n"
    #         "3. Вставьте в эту панель, отредактируйте.\n"
    #         "4. Сохраните как новый PDF."
    #     )
    #     info_lbl.setWordWrap(True)
    #     info_lbl.setStyleSheet("color: #555; font-size: 11px; padding: 5px;")
    #
    #     self.text_edit = QTextEdit()
    #     self.text_edit.setPlaceholderText("Отредактированный текст будет здесь...")
    #     self.text_edit.setMinimumWidth(300)
    #
    #     edit_layout.addWidget(info_lbl)
    #     edit_layout.addWidget(self.text_edit)
    #     splitter.addWidget(edit_panel)
    #
    #     splitter.setSizes([800, 400])
    #     layout.addWidget(splitter)
    #     tab_container.setLayout(layout)
    #
    #     index = self.tab_widget.addTab(tab_container, title)
    #     self.tab_widget.setCurrentIndex(index)
    #     return tab_container

    def create_new_tab(self, title: str):
        if self.tab_widget is None:
            QMessageBox.critical(None, "Ошибка", "QTabWidget не инициализирован!")
            return None

        tab_container = QWidget()
        layout = QVBoxLayout(tab_container)
        layout.setContentsMargins(0, 0, 0, 0)

        splitter = QSplitter(Qt.Horizontal)
        splitter.setStretchFactor(0, 3)  # PDF 75%
        splitter.setStretchFactor(1, 1)  # Редактор 25%

        # --- ЛЕВАЯ ПАНЕЛЬ: Просмотр PDF как картинок (вместо QWebEngineView) ---
        self.pdf_viewer_scroll = QScrollArea()
        self.pdf_viewer_scroll.setWidgetResizable(True)
        self.pdf_viewer_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.pdf_viewer_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        self.pdf_pages_container = QWidget()
        pdf_layout = QVBoxLayout(self.pdf_pages_container)
        pdf_layout.setAlignment(Qt.AlignTop)
        pdf_layout.setSpacing(10)
        pdf_layout.setContentsMargins(10, 10, 10, 10)

        placeholder = QLabel("Здесь отобразится PDF (постранично как картинки)")
        placeholder.setAlignment(Qt.AlignCenter)
        placeholder.setStyleSheet("color: #888; font-size: 14px;")
        pdf_layout.addWidget(placeholder)

        self.pdf_viewer_scroll.setWidget(self.pdf_pages_container)
        splitter.addWidget(self.pdf_viewer_scroll)

        # --- ПРАВАЯ ПАНЕЛЬ: Редактор текста ---
        edit_panel = QWidget()
        edit_layout = QVBoxLayout(edit_panel)
        edit_layout.setContentsMargins(5, 5, 5, 5)

        info_lbl = QLabel(
            "1. Откройте PDF — он появится слева.\n"
            "2. Скопируйте текст из PDF (или вставьте сюда).\n"
            "3. Отредактируйте, измените шрифт.\n"
            "4. Сохраните как новый PDF."
        )
        info_lbl.setWordWrap(True)
        info_lbl.setStyleSheet("color: #555; font-size: 11px; padding: 5px;")

        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText("Отредактированный текст будет здесь...")
        self.text_edit.setMinimumWidth(300)

        edit_layout.addWidget(info_lbl)
        edit_layout.addWidget(self.text_edit)
        splitter.addWidget(edit_panel)

        splitter.setSizes([800, 400])
        layout.addWidget(splitter)
        tab_container.setLayout(layout)

        index = self.tab_widget.addTab(tab_container, title)
        self.tab_widget.setCurrentIndex(index)
        return tab_container

    def open_pdf(self):

        filepath, _ = QFileDialog.getOpenFileName(
            self.tab_widget, "Открыть PDF", "", "PDF файлы (*.pdf);;Все файлы (*)"
        )
        if not filepath:
            return

        try:
            doc = fitz.open(filepath)

            # Очищаем старые страницы
            layout = self.pdf_pages_container.layout()
            while layout.count():
                child = layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()

            full_text = []

            # Рендерим каждую страницу в QPixmap
            for page_num in range(len(doc)):
                page = doc[page_num]

                # 1. Получаем pixmap
                pixmap_obj = page.get_pixmap(dpi=150)

                # 2. ВАЖНО: Конвертируем в байты (PNG) без сохранения на диск
                # Это работает на всех версиях PyMuPDF
                img_data = pixmap_obj.tobytes("png")

                # 3. Загружаем байты прямо в QPixmap
                qpixmap = QPixmap()
                qpixmap.loadFromData(img_data)

                lbl = QLabel()
                lbl.setPixmap(qpixmap)
                lbl.setAlignment(Qt.AlignLeft)
                lbl.setScaledContents(False)  # Чтобы не растягивало картинку

                layout.addWidget(lbl)

                # Сбор текста (как и раньше)
                full_text.append(page.get_text())

            doc.close()

            # Объединяем весь текст
            text = "\n".join(full_text)
            self.text_edit.setPlainText(text)

            QMessageBox.information(
                self.tab_widget,
                "Готово",
                f"PDF отображён слева.\nТекст скопирован справа для редактирования."
            )
        except Exception as e:
            QMessageBox.critical(self.tab_widget, "Ошибка", str(e))
    #     filepath, _ = QFileDialog.getOpenFileName(
    #         self.tab_widget, "Открыть PDF", "", "PDF файлы (*.pdf);;Все файлы (*)"
    #     )
    #     if not filepath:
    #         return
    #
    #     try:
    #         doc = fitz.open(filepath)
    #
    #         # Очищаем старые страницы
    #         layout = self.pdf_pages_container.layout()
    #         while layout.count():
    #             child = layout.takeAt(0)
    #             if child.widget():
    #                 child.widget().deleteLater()
    #
    #         # Рендерим каждую страницу в QPixmap
    #         for page_num in range(len(doc)):
    #             page = doc[page_num]
    #             # dpi=150 даёт хорошее качество без огромных картинок
    #             pixmap = page.get_pixmap(dpi=150)
    #
    #             lbl = QLabel()
    #             lbl.setPixmap(QPixmap.fromImage(pixmap.pil_image()))
    #             lbl.setAlignment(Qt.AlignLeft)
    #             layout.addWidget(lbl)
    #
    #         doc.close()
    #
    #         # Теперь вытаскиваем текст для редактора
    #         doc = fitz.open(filepath)
    #         text = fitz.get_text(doc)
    #         t = ''
    #         for i in text:
    #             t += i
    #         doc.close()
    #         self.text_edit.setPlainText(t)
    #
    #         QMessageBox.information(
    #             self.tab_widget,
    #             "Готово",
    #             f"PDF отображён слева (постранично).\nТекст скопирован справа для редактирования."
    #         )
    #     except Exception as e:
    #         QMessageBox.critical(self.tab_widget, "Ошибка", str(e))

    # Остальные методы (save_as_pdf, apply_font_dialog, apply_font_to_text) оставь как были
    # Они не зависят от способа отображения PDF
    # --- Открытие PDF ---
    # def open_pdf(self):
    #     filepath, _ = QFileDialog.getOpenFileName(
    #         self.tab_widget, "Открыть PDF", "", "PDF файлы (*.pdf);;Все файлы (*)"
    #     )
    #     if not filepath:
    #         return
    #
    #     try:
    #         # 1. Показываем оригинал слева (картинки, линии, всё)
    #         url = QUrl.fromLocalFile(os.path.abspath(filepath))
    #
    #         self.pdf_viewer.load(url)
    #         doc = fitz.open(filepath)
    #         text = fitz.get_text(doc)
    #         print(text)
    #         t = ''
    #         for i in text:
    #             t += i
    #         # 2. (Опционально) Сразу вытаскиваем текст для удобства редактирования
    #         # doc = fitz.open(filepath)
    #         # text = doc.get_text("text")
    #         doc.close()
    #         self.text_edit.setPlainText(t)
    #
    #         QMessageBox.information(
    #             self.tab_widget,
    #             "Готово",
    #             f"PDF открыт слева (с картинками и линиями).\nТекст скопирован справа для редактирования."
    #         )
    #     except Exception as e:
    #         QMessageBox.critical(self.tab_widget, "Ошибка", str(e))

    # --- Сохранение отредактированного текста в PDF ---
    def save_as_pdf(self):
        filepath, _ = QFileDialog.getSaveFileName(
            self.tab_widget, "Сохранить как PDF", "", "PDF файлы (*.pdf)"
        )
        if not filepath:
            return

        try:
            if not isinstance(self.text_edit, QTextEdit):
                QMessageBox.warning(self.tab_widget, "Ошибка", "Не найден редактор текста.")
                return

            printer = QPrinter(QPrinter.HighResolution)
            printer.setOutputFormat(QPrinter.PdfFormat)
            printer.setOutputFileName(filepath)
            printer.setPageSize(QPrinter.A4)
            printer.setPageMargins(15, 15, 15, 15, QPrinter.Millimeter)
            printer.setFontEmbeddingEnabled(True)

            self.text_edit.document().print_(printer)

            QMessageBox.information(self.tab_widget, "Успех", f"Отредактированный текст сохранён:\n{filepath}")
        except Exception as e:
            QMessageBox.critical(self.tab_widget, "Ошибка сохранения", str(e))

    # --- Выбор шрифта и применение к тексту ---
    def apply_font_dialog(self):
        # Папка fonts рядом со скриптом
        script_dir = os.path.dirname(os.path.abspath(__file__))
        font_folder = os.path.join(script_dir, "fonts")

        if not os.path.exists(font_folder):
            QMessageBox.warning(
                self.tab_widget,
                "Папка не найдена",
                "Создайте папку 'fonts' рядом со скриптом и положите туда .ttf/.otf файлы."
            )
            return

        dialog = FontListDialog(font_folder, self.tab_widget)
        if dialog.exec() == QDialog.Accepted:
            font = dialog.get_selected_font()
            self.apply_font_to_text(font)

    def apply_font_to_text(self, font: QFont):
        """Применяет выбранный шрифт к выделенному тексту или ко всему документу"""
        if not isinstance(self.text_edit, QTextEdit):
            return

        cursor = self.text_edit.textCursor()

        # Если есть выделение — меняем только его, иначе — весь документ
        if cursor.hasSelection():
            char_format = QTextCharFormat()
            char_format.setFont(font)
            cursor.setCharFormat(char_format)
        else:
            # Применяем ко всему тексту
            doc = self.text_edit.document()
            # cursor = doc.cursorForPosition(QtCore.QPoint(0, 0))
            cursor.select(QTextCursor.Document)
            char_format = QTextCharFormat()
            char_format.setFont(font)
            cursor.setCharFormat(char_format)

        # --- Заглушки для абстрактных методов (чтобы класс корректно наследовался) ---
    def normalize_font_name(self, pdf_font_name):
        return pdf_font_name

    def load_font_to_database(self, font_path):
        idx = self.font_db.addApplicationFont(font_path)
        return idx != -1

    def find_matching_font(self, pdf_font_name):
        families = self.font_db.families()
        # Простая эвристика: ищем по подстроке
        for fam in families:
            if pdf_font_name.lower() in fam.lower():
                return fam
        return None

    def create_qt_font_from_pdf_span(self, span_data):
        # span_data — это dict из fitz.get_text("dict")
        font_name = span_data.get("font", "")
        size = span_data.get("size", 12)
        weight = QFont.Weight.Normal
        italic = False

        if "Bold" in font_name:
            weight = QFont.Weight.Bold
        if "Italic" in font_name or "Oblique" in font_name:
            italic = True

        fam = self.find_matching_font(font_name) or "Arial"
        f = QFont(fam, int(size))
        f.setWeight(weight)
        f.setItalic(italic)
        return f

    def analyze_and_map_fonts(self, filepath):
        doc = fitz.open(filepath)
        fonts_used = set()
        for page in doc:
            blocks = page.get_text("dict")["blocks"]
            for block in blocks:
                if block["type"] == 0:  # текстовый блок
                    for line in block["lines"]:
                        for span in line["spans"]:
                            fonts_used.add(span.get("font", "Unknown"))
        doc.close()
        return list(fonts_used)

    # ==========================================
    # Главное окно приложения (обёртка над WindowConfigurator)
    # ==========================================

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PDF Viewer + Text Editor (с поддержкой шрифтов)")
        self.resize(1200, 800)

        # Инициализируем конфигуратор
        self.config = WindowConfigurator()

        # Создаём центральный виджет и табы
        central = self.config.create_central_widget()
        # self.config.create_tab_widget(self.config.close_tab)
        self.config.add_layout()
        self.setCentralWidget(central)

        # Добавляем панель инструментов
        toolbar = QToolBar("Инструменты")
        self.addToolBar(toolbar)

        btn_open = QAction("Открыть PDF (с картинками)", self)
        btn_open.triggered.connect(self.config.open_pdf)
        toolbar.addAction(btn_open)

        btn_font = QAction("Выбрать шрифт", self)
        btn_font.triggered.connect(self.config.apply_font_dialog)
        toolbar.addAction(btn_font)

        btn_save = QAction("Сохранить текст как PDF", self)
        btn_save.triggered.connect(self.config.save_as_pdf)
        toolbar.addAction(btn_save)

        # ✅ Исправление: создаём первую вкладку сразу при старте
        self.config.create_new_tab("Вкладка 1")
# class MainWindow(QMainWindow):
#     def __init__(self):
#         super().__init__()
#         self.setWindowTitle("PDF Viewer + Text Editor (с поддержкой шрифтов)")
#         self.resize(1200, 800)
#
#         # Инициализируем конфигуратор
#         self.config = WindowConfigurator()
#
#         # Создаём центральный виджет и табы
#         central = self.config.create_central_widget()
#         self.config.create_tab_widget(self.config.close_tab)
#         self.config.add_layout()
#         self.setCentralWidget(central)
#
#         # Добавляем панель инструментов
#         toolbar = QToolBar("Инструменты")
#         self.addToolBar(toolbar)
#
#         btn_open = QAction("Открыть PDF (с картинками)", self)
#         btn_open.triggered.connect(self.config.open_pdf)
#         toolbar.addAction(btn_open)
#
#         btn_font = QAction("Выбрать шрифт", self)
#         btn_font.triggered.connect(self.config.apply_font_dialog)
#         toolbar.addAction(btn_font)
#
#         btn_save = QAction("Сохранить текст как PDF", self)
#         btn_save.triggered.connect(self.config.save_as_pdf)
#         toolbar.addAction(btn_save)
#
#         # Сразу создаём первую вкладку
#         self.config.create_new_tab("Новая вкладка")

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Важно: для QWebEngineView нужен атрибут ApplicationName
    app.setApplicationName("PDF-Editor-App")

    window = MainWindow()
    window.show()
    sys.exit(app.exec())
