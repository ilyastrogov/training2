from PyQt5.QtWidgets import (QApplication, QMainWindow, QTabWidget, QTextEdit, QGraphicsScene,
                             QPushButton, QVBoxLayout, QWidget, QFontDialog, QFileDialog,
                             QComboBox, QToolBar, QMessageBox, QLabel, QListWidget,
                             QFontComboBox, QGraphicsView, QListWidgetItem, QDialogButtonBox,
                             QGroupBox, QHBoxLayout, QSpinBox)
from PyQt5.QtGui import (QTextCharFormat, QFont, QTextDocument, QPdfWriter, QTextCursor,
                         QPainter, QFontDatabase, QPen)
from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtWidgets import QSizePolicy, QDialog
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtPrintSupport import QPrinter
import sys
import fitz  # PyMuPDF для работы с PDF
import re
from abc import ABC, abstractmethod
from tkinter import messagebox, filedialog
import tkinter as tk

import requests
from bs4 import BeautifulSoup

import os
import glob

from pathlib import Path

import urllib.parse
from urllib.parse import urljoin


# Основной контейнер
class AddLayout(ABC):

    @abstractmethod
    def create_layout(self, arg=None):
        pass

    @abstractmethod
    def add_layout(self):
        pass


# Вкладки с редакторами
class CreateTabWidget(ABC):
    @abstractmethod
    def create_tab_widget(self, close_tab):
        pass


# Создание новой вкладки
class CreateNewTab(ABC):
    @abstractmethod
    def create_new_tab(self, title):
        """Создаёт новую вкладку с QTextEdit."""
        pass

    """ Рассчитывает размер страницы A4 """

    @abstractmethod
    def calculate_pdf_page_size(self, dpi=96):
        pass


# Создание кнопок
class CreateElem(ABC):
    @abstractmethod
    def create_elem(self, toolbar, btn, functions):
        pass


"""Смена шрифта через диалоговое окно."""


class ChangeFont(ABC):
    @abstractmethod
    def change_font(self):
        pass

    @abstractmethod
    def set_active_font(self, font):
        pass


""" Открытие файла """


class OpenPdf(ABC):
    @abstractmethod
    def open_pdf(self):
        pass


""" Отрисовка текста """


class RenderingText(ABC):
    @abstractmethod
    def rendering_text(self, filepath):
        pass


""" Сохранение файла """


class SavePdf(ABC):
    @abstractmethod
    def save_as_pdf(self):
        pass


class CloseTab(ABC):
    @abstractmethod
    def close_tab(self, index):
        pass


class PDFFontMapper(ABC):
    @abstractmethod
    def normalize_font_name(self, pdf_font_name):
        pass

    @abstractmethod
    def load_font_to_database(self, font_path):
        pass

    @abstractmethod
    def find_matching_font(self, pdf_font_name):
        pass

    @abstractmethod
    def create_qt_font_from_pdf_span(self, span_data):
        pass

    @abstractmethod
    def analyze_and_map_fonts(self, filepath):
        pass


# --- Диалог выбора шрифта из папки ---
class FontListDialog(QDialog):
    def __init__(self, font_paths, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Выбор шрифта (папка)")
        self.selected_font = None

        # 1. Загружаем шрифты только из этой папки
        self.loaded_families = []
        self.db = QFontDatabase()
        path = Path(font_paths)
        self.styles = None
        # --- Структура для хранения: семейство -> есть ли Bold ---
        self.families_with_bold = {}

        for file in path.iterdir():
            if file.suffix.lower() in {'.ttf', '.otf'}:
                idx = self.db.addApplicationFont(str(file))
                if idx != -1:
                    families = self.db.applicationFontFamilies(idx)
                    print('families', families)
                    for fam in families:
                        self.families_with_bold[fam] = self.db.styles(fam)
                    self.loaded_families.extend(families)
                    # family_name = families[0]
                    # # ОПРЕДЕЛЕНИЕ НАЧЕРТАНИЯ ПО ИМЕНИ ФАЙЛА ИЛИ ЛОГИКЕ
                    # # Простая эвристика: если в имени файла есть 'Bold', считаем его жирным
                    # is_bold_file = "bold" in os.path.basename(file).lower()
                    # weight_key = "Bold" if is_bold_file else "Normal"
                    #
                    # # Сохраняем связь: (Семейство, Начертание) -> Путь к файлу
                    # self.font_map[(family_name, weight_key)] = file
                    #
                    # print(f"[Font Loader] Сохранено: {family_name} ({weight_key}) -> {file}")
        # Убираем дубликаты, сохраняя порядок
        # seen = set()
        # unique_families = []
        # for fam in self.loaded_families:
        #     if fam not in seen:
        #         seen.add(fam)
        #         unique_families.append(fam)
        # self.loaded_families = unique_families

        if not self.loaded_families:
            # Если шрифтов нет — сразу выходим
            self.reject()
            return

        # 2. Создаем UI
        main_layout = QVBoxLayout()

        # --- Блок выбора семейства ---
        family_group = QGroupBox("Семейство шрифта")
        family_layout = QVBoxLayout()
        lbl_family = QLabel("Выберите шрифт:")
        self.combo = QComboBox()
        self.combo.addItems(self.loaded_families)
        family_layout.addWidget(lbl_family)
        family_layout.addWidget(self.combo)
        family_group.setLayout(family_layout)
        main_layout.addWidget(family_group)

        # --- Блок размера ---
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

        # Жирность
        style_group = QGroupBox("Начертание шрифта")
        style_layout = QHBoxLayout()
        style_layout.addSpacing(20)
        style_layout.addWidget(QLabel("Начертание:"))
        self.combo_style = QComboBox()
        print('bliNNN')
        first_family = self.combo.currentText()
        print('bliNNNn')
        self._update_style_options(first_family)
        print('bliNNNnn')
        style_layout.addWidget(self.combo_style)
        style_group.setLayout(style_layout)
        main_layout.addWidget(style_group)

        # style_group = QGroupBox("Начертание шрифта")
        # style_layout = QHBoxLayout()
        # style_layout.addSpacing(20)
        # style_layout.addWidget(QLabel("Начертание:"))
        # self.combo_style = QComboBox()
        # self.combo_style.addItems(["Normal", "Bold"])
        # style_layout.addWidget(self.combo_style)
        # style_group.setLayout(style_layout)
        # main_layout.addWidget(style_group)

        # --- Предпросмотр ---
        preview_group = QGroupBox("Предпросмотр")
        preview_layout = QVBoxLayout()
        self.preview_label = QLabel("AaBbCcDdEe FfGgHhIiJj\n0123456789 !@#$%^&*()")
        self.preview_label.setStyleSheet("border: 1px solid #ccc; padding: 8px; background: white;")
        self.preview_label.setMinimumHeight(60)
        self.preview_label.setWordWrap(True)
        preview_layout.addWidget(self.preview_label)
        preview_group.setLayout(preview_layout)
        main_layout.addWidget(preview_group)

        # Обновляем предпросмотр при изменениях
        self.combo.currentTextChanged.connect(self._update_preview)
        self.spin_size.valueChanged.connect(self._update_preview)
        self.combo_style.currentTextChanged.connect(self._update_preview)

        # self.list_widget.itemClicked.connect(self.on_item_clicked)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        # Кнопки OK/Cancel
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        main_layout.addWidget(buttons)

        self.setLayout(main_layout)
        self._update_preview()  # начальный предпросмотр

    def _update_style_options(self, family: str):
        """
        Обновляет combo_style: показывает 'Bold' только если он реально есть у семейства.
        """
        print(self.families_with_bold[family])
        has_bold = self.families_with_bold[family]
        self.combo_style.clear()
        if has_bold:
            self.combo_style.addItems(has_bold)
        else:
            self.combo_style.addItem("Normal")

        # Если Bold убрали из списка, а он был выбран — сбрасываем на Normal
        if self.combo_style.currentText() != "Normal" and not has_bold:
            self.combo_style.setCurrentText("Normal")

    def _update_preview(self):
        font_name = self.combo.currentText()
        point_size = self.spin_size.value()
        style_text = self.combo.currentText()
        f = QFont(font_name)
        f.setPointSize(point_size)
        if style_text.lower() == "bold":
            print('BBBB', style_text.lower())
            f.setWeight(QFont.Weight.Bold)
        if style_text.lower() == "italic":
            print('IIII', style_text.lower())
            f.setItalic(True)
        if style_text.lower() == "normal":
            f.setWeight(QFont.Weight.Normal)
        if style_text.lower() == "lightl":
            f.setWeight(QFont.Weight.Light)


        self.preview_label.setFont(f)

    # def on_item_clicked(self, item):
    #     self.selected_font = item.data(Qt.UserRole)
    #
    # def get_selected_font_path(self):
    #     return self.selected_font


# Настройки окна
class WindowConfigurator(AddLayout, CreateTabWidget, CreateNewTab,
                         SavePdf, CloseTab, PDFFontMapper,
                         CreateElem, ChangeFont, OpenPdf, RenderingText):
    def __init__(self):
        super().__init__()
        # Вкладки с редакторами
        self.tab_widget = None
        # Основной контейнер
        self.central_widget = None
        self.layout = None

        self.text_edit = None
        # Окно выбора файла
        self.root = tk.Tk()
        self.root.withdraw()
        # База шрифтов
        self.font_db = QFontDatabase()
        self.font_cache = {}  # Кэш для ускорения
        self.loaded_font_ids = []  # Храним ID загруженных шрифтов, чтобы не дублировать

        # 1. Инициализация словаря: ключ=(family, weight), значение=путь к файлу
        # weight: "Normal" или "Bold"
        self.font_map = {}

    def create_central_widget(self):
        self.central_widget = QWidget()
        return self.central_widget

    def create_widget(self):
        self.tab_widget = QTabWidget()
        return self.tab_widget

    def create_text_edit(self):
        self.text_edit = QTextEdit()
        return self.text_edit

    # Вкладки с редакторами
    def create_tab_widget(self, close_tab):
        self.tab_widget = self.create_widget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.tabCloseRequested.connect(close_tab)
        return self.tab_widget

    # Создаём layout и сохраняем в self.layout
    def create_layout(self, arg=None):
        self.layout = QVBoxLayout(arg) if arg else QVBoxLayout()
        return self.layout

    # Вставляем макет
    def add_layout(self):
        self.layout = self.create_layout()
        self.central_widget = self.create_central_widget()
        self.layout.addWidget(self.tab_widget)
        self.central_widget.setLayout(self.layout)
        return self.central_widget

    # Создание новой вкладки
    # def create_new_tab(self, title):
    #     text_edit = QTextEdit()
    #
    #     # Рассчитываем размер A4 в пикселях (при DPI = 96)
    #     page_width, page_height = self.calculate_pdf_page_size(dpi=96)
    #
    #     # Устанавливаем фиксированный размер QTextEdit, соответствующий A4
    #     # text_edit.setFixedSize(page_width, page_height)
    #     text_edit.setFixedSize(920, 1123)
    #     # Политика фиксированного размера — виджет не будет растягиваться
    #     text_edit.setSizePolicy(
    #         QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
    #     )
    #
    #     # Добавляем отступы для лучшего отображения текста
    #     text_edit.setViewportMargins(100, 100, 100, 100)
    #
    #     index = self.tab_widget.addTab(text_edit, title)
    #     self.tab_widget.setCurrentIndex(index)
    #     return text_edit
    def create_new_tab(self, title):
        # Рассчитываем размер A4
        page_width, page_height = self.calculate_pdf_page_size(dpi=96)

        # Создаём контейнер для центрирования
        self.central_widget = self.create_central_widget()
        self.layout = self.create_layout(self.central_widget)
        self.layout.setAlignment(Qt.AlignCenter)  # Центрируем по горизонтали и вертикали

        self.text_edit = self.create_text_edit()
        self.text_edit.setFixedSize(page_width, page_height)
        self.text_edit.setSizePolicy(QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed))
        self.text_edit.setViewportMargins(15, 15, 15, 15)  # Отступы внутри QTextEdit

        self.layout.addWidget(self.text_edit)

        index = self.tab_widget.addTab(self.central_widget, title)
        self.tab_widget.setCurrentIndex(index)
        return self.text_edit

    """ Рассчитывает размер страницы A4 """

    def calculate_pdf_page_size(self, dpi=96):
        """
        Рассчитывает размер страницы A4 в пикселях.
        :param dpi: Разрешение экрана (точек на дюйм)
        :return: кортеж (ширина, высота) в пикселях
        """
        # Размеры A4 в мм
        a4_width_mm = 210
        a4_height_mm = 297

        # Конвертируем мм в дюймы, затем в пиксели
        a4_width_inches = a4_width_mm / 25.4  # 1 дюйм = 25.4 мм
        a4_height_inches = a4_height_mm / 25.4

        width_pixels = int(a4_width_inches * dpi)
        height_pixels = int(a4_height_inches * dpi)

        return width_pixels, height_pixels

    # Создание кнопок
    def create_elem(self, toolbar, btn, functions):
        count = 0
        for button in btn:
            button.clicked.connect(functions[count])
            count += 1
            toolbar.addWidget(button)

    # def load_font_file(self, font_path: str): # Пока не работает надо доработать
    #     """
    #     Загружает шрифт в QFontDatabase и запоминает путь к файлу
    #     для последующего гарантированного встраивания в PDF.
    #     """
    #     if not os.path.exists(font_path):
    #         return
    #
    #     # Добавляем шрифт в приложение
    #     font_id = QFontDatabase.addApplicationFont(font_path)
    #
    #     if font_id == -1:
    #         messagebox.showerror("Ошибка", "Не удалось загрузить шрифт.")
    #         return
    #
    #     families = QFontDatabase.applicationFontFamilies(font_id)
    #     if not families:
    #         return
    #
    #     family_name = families[0]
    #
    #     # ОПРЕДЕЛЕНИЕ НАЧЕРТАНИЯ ПО ИМЕНИ ФАЙЛА ИЛИ ЛОГИКЕ
    #     # Простая эвристика: если в имени файла есть 'Bold', считаем его жирным
    #     is_bold_file = "bold" in os.path.basename(font_path).lower()
    #     weight_key = "Bold" if is_bold_file else "Normal"
    #
    #     # Сохраняем связь: (Семейство, Начертание) -> Путь к файлу
    #     self.font_map[(family_name, weight_key)] = font_path
    #
    #     print(f"[Font Loader] Сохранено: {family_name} ({weight_key}) -> {font_path}")
    #
    #     # --- НОВАЯ ФУНКЦИЯ: Открытие диалога выбора шрифта ---

    def open_font_folder_dialog(self):
        """Ищет шрифты в папке 'fonts' рядом со скриптом и показывает диалог."""
        # script_dir = os.path.dirname(os.path.abspath(__file__))
        # font_folder = os.path.join(script_dir, 'fonts')
        #
        # if not os.path.exists(font_folder):
        #     messagebox.showwarning("Папка не найдена",
        #                            f"Папка '{font_folder}' не существует. Создайте её и положите туда .ttf/.otf файлы.")
        #     return
        #
        # # Ищем все ttf и otf файлы рекурсивно
        # patterns = ['*.ttf', '*.otf']
        # font_files = []
        # for pattern in patterns:
        #     font_files.extend(glob.glob(os.path.join(font_folder, pattern), recursive=True))
        #     font_files.extend(glob.glob(os.path.join(font_folder, '**', pattern), recursive=True))
        #
        # if not font_files:
        #     messagebox.showinfo("Шрифты не найдены", "В папке fonts нет файлов .ttf или .otf")
        #     return

        dialog = FontListDialog('fonts', self.tab_widget)
        # dialog = CustomFontDialog(folder_path, parent)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            font_name = dialog.combo.currentText()
            point_size = dialog.spin_size.value()
            style_text = dialog.combo_style.currentText()
            print('point_size', font_name)
            print('style_text', style_text.lower() == "italic")
            font = QFont(font_name, point_size)

            if style_text.lower() == "bold":
                print('BBBB', style_text.lower())
                font.setWeight(QFont.Weight.Bold)
            if style_text.lower() == "italic":
                print('IIII', style_text.lower())
                font.setItalic(True)
            if style_text.lower() == "normal":
                print('nnnnn', style_text.lower())
                font.setWeight(QFont.Weight.Normal)
            if style_text.lower() == "lightl":
                print('llll', style_text.lower())
                font.setWeight(QFont.Weight.Light)



            # if style_text == "Bold":
            #     font.setWeight(QFont.Weight.Bold)  # PyQt6
            #     # font.setBold(True)                  # Альтернатива для PyQt5/6
            # else:
            #     font.setWeight(QFont.Weight.Normal)
            self.apply_font_to_matching_text(font)
            self.set_active_font(font)
        #     return font, True
        # return QFont(), False

        # current_widget = self.tab_widget.currentWidget()
        # text_edit = current_widget.findChild(QTextEdit)
        # current_widget = text_edit
        # if not isinstance(current_widget, QTextEdit):
        #     return

        # current_format = current_widget.currentCharFormat()
        # initial_font = current_format.font()

        # font, ok = QFontDialog.getFont(QFont(font_files))
        # if ok:
        #     self.set_active_font(font)

    def apply_font_to_matching_text(self, new_font):
        """Загружает шрифт и применяет его к тексту с похожим названием."""
        current_widget = self.tab_widget.currentWidget()
        text_edit = current_widget.findChild(QTextEdit)

        if not isinstance(text_edit, QTextEdit):
            return

        # 1. Загружаем шрифт в базу, если еще не загружен
        # font_id = QFontDatabase.addApplicationFont(font_path)
        # if font_id == -1:
        #     messagebox.showerror("Ошибка", "Не удалось загрузить шрифт из файла.")
        #     return
        #
        # self.loaded_font_ids.append(font_id)
        # families = QFontDatabase.applicationFontFamilies(font_id)
        # if not families:
        #     return

        # new_family_name = families[0]
        # print(f"Загружен шрифт: {new_family_name} из {font_path}")

        # Получаем имя файла без расширения для сравнения (например, "Arial-Bold" -> ищем совпадения с "Arial")
        # base_name = os.path.splitext(os.path.basename(font_path))[0]
        # # Очищаем имя от суффиксов типа Bold, Italic для поиска совпадений
        # clean_base = re.sub(r'(Bold|Italic|Regular|Light|Medium)', '', base_name, flags=re.IGNORECASE).strip()

        doc = text_edit.document()
        cursor = QTextCursor(doc)
        cursor.beginEditBlock()
        target_family = new_font.family()

        applied_count = 0


        # 2. Проходим по всем блокам и фрагментам текста
        block = doc.firstBlock()
        while block.isValid():
            iterator = block.begin()
            while not iterator.atEnd():
                fragment = iterator.fragment()
                if fragment.isValid():
                    fmt = fragment.charFormat()
                    current_font = fmt.font()
                    current_family = current_font.family()

                    # Логика сравнения:
                    # Если текущий шрифт в тексте содержит часть имени нового шрифта ИЛИ наоборот
                    match = False
                    if target_family.lower() in current_family.lower():
                        match = True
                    elif current_family.lower() in target_family.lower():
                        match = True

                    # Также проверяем точное совпадение (на случай если пользователь кликнул на тот же шрифт)
                    if current_family == target_family:
                        match = True

                    if match:
                        # Создаем новый формат с новым семейством, сохраняя жирность/курсив если возможно
                        new_fmt = QTextCharFormat(fmt)
                        # new_font = QFont(target_family)
                        print('new_font', new_font.bold())
                        print('new_font2', new_font.pointSize())
                        # Пытаемся сохранить стиль (Bold/Italic), если новый шрифт поддерживает эти веса
                        # if current_font.bold():
                        #     new_font.setBold(True)
                        # if current_font.italic():
                        #     new_font.setItalic(True)

                        new_fmt.setFont(new_font)

                        # Применяем формат к этому фрагменту
                        cursor.setPosition(fragment.position())
                        cursor.setPosition(fragment.position() + fragment.length(), QTextCursor.KeepAnchor)
                        cursor.mergeCharFormat(new_fmt)
                        applied_count += 1

                iterator += 1
            block = block.next()
        #
        cursor.endEditBlock()
        messagebox.showinfo("Готово", f"Шрифт '{target_family}' применен к {applied_count} фрагментам текста.")

    # Остальные методы (change_font, set_active_font, open_pdf, rendering_text, save_as_pdf и т.д.)
    # остаются такими же, как в вашем исходном коде, я их не дублирую для краткости,
    # но убедитесь, что они есть в классе. Ниже приведу только те, что критичны для работы.

    """Смена шрифта через диалоговое окно."""

    def change_font(self):
        """Смена шрифта через диалоговое окно."""
        current_widget = self.tab_widget.currentWidget()
        text_edit = current_widget.findChild(QTextEdit)
        current_widget = text_edit
        if not isinstance(current_widget, QTextEdit):
            return

        current_format = current_widget.currentCharFormat()
        initial_font = current_format.font()

        font, ok = QFontDialog.getFont(initial_font)
        if ok:
            self.set_active_font(font)

    # для change_font
    def set_active_font(self, font):
        """Устанавливает активный шрифт для текущего виджета."""
        current_widget = self.tab_widget.currentWidget()
        self.text_edit = current_widget.findChild(QTextEdit)
        current_widget = self.text_edit
        cursor = current_widget.textCursor()

        if cursor.hasSelection():
            fmt = QTextCharFormat()
            fmt.setFont(font)
            cursor.mergeCharFormat(fmt)

        active_format = QTextCharFormat()
        print(font.family())
        active_format.setFont(font)
        current_widget.setCurrentCharFormat(active_format)

    # Открытие файла
    def open_pdf(self):
        """Открывает PDF-файл и конвертирует в текст для редактирования."""

        filepath = filedialog.askopenfilename(
            title="Открыть файл",
            defaultextension=".pdf",  # Автоматическое добавление расширения, если пользователь его не укажет
            filetypes=[("PDF файлы", "*.pdf"), ("Все файлы", "*.*")]  # Фильтрация типов файлов

        )
        if not filepath:
            return
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                html = f.read()
                print(html)
            self.text_edit.document().setHtml(html)
            messagebox.showinfo("Успех", f"PDF-файл {filepath} успешно открыт!")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось открыть PDF-файл:\n{str(e)}")
        # view = QWebEngineView()
        # view.loadFile(filepath)  # путь к вашему файлу
        # view.resize(595, 842)  # под размер A4 при 72 DPI
        # view.show()
        # self.rendering_text(filepath)

    def get_pdf_page_dimensions(self, filepath, page_num=0):
        """
        Получает размеры конкретной страницы PDF в пикселях.
        :param filepath: Путь к PDF-файлу
        :param page_num: номер страницы (по умолчанию — первая)
        :return: кортеж (ширина, высота) в пикселях
        """
        doc = fitz.open(filepath)
        page = doc.load_page(page_num)
        rect = page.rect  # BBox страницы
        width = int(rect.width)
        height = int(rect.height)
        doc.close()
        return width, height

    def create_new_tab_with_pdf_size(self, title, width, height):
        self.text_edit = self.create_text_edit()
        self.text_edit.setFixedSize(width, height)
        self.text_edit.setSizePolicy(QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed))
        index = self.tab_widget.addTab(self.text_edit, title)
        self.tab_widget.setCurrentIndex(index)
        return self.text_edit

    # Отрисовка текста
    def rendering_text(self, filepath):
        try:

            print('1')
            tab_title = f"Редактирование: {filepath.split('/')[-1]}"
            print('2')
            font_mapping = self.analyze_and_map_fonts(filepath)
            # Получаем точные размеры страницы из PDF
            page_width, page_height = self.get_pdf_page_dimensions(filepath)
            print('3')
            # text_edit = self.create_new_tab_with_pdf_size(tab_title, page_width, page_height)
            self.text_edit = self.create_new_tab(tab_title)
            print('4')
            cursor = self.text_edit.textCursor()

            for page in font_mapping:
                print('page', page)
                prev_block_y0 = None

                for block in page["blocks"]:
                    block_y0 = block["bbox"][1]

                    # Новый абзац по вертикальному отступу между блоками
                    if prev_block_y0 is not None and (block_y0 - prev_block_y0) > 20:
                        cursor.insertBlock()  # Новый абзац

                    prev_block_y0 = block_y0

                    for line in block["lines"]:
                        line_y0 = line["bbox"][1]
                        # # Новый блок внутри абзаца по вертикальному отступу
                        # if prev_line_y0 is not None and abs(line_y0 - prev_line_y0) > 15:
                        #     cursor.insertBlock()

                        prev_line_y0 = line_y0
                        line_x0 = line["bbox"][0]

                        # Добавляем отступ только для первой строки абзаца
                        if (prev_line_y0 is None or abs(line_y0 - prev_line_y0) > 15) and line_x0 > 30:
                            indent_spaces = " " * int((line_x0 - 30) / 8)  # Увеличен делитель для уменьшения отступа
                            if indent_spaces:  # Проверяем, что отступ не пустой
                                cursor.insertText(indent_spaces)

                        for span in line["spans"]:
                            if not span["text"].strip():
                                continue

                            cursor.setCharFormat(span["char_format"])
                            cursor.insertText(span["text"])

                        # Перенос строки после каждой строки PDF
                        cursor.insertText("\n")

                    # Перенос между страницами
                    cursor.insertBlock()

            print('5')

            messagebox.showinfo("Успех", f"PDF-файл {tab_title} успешно открыт!")

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось открыть PDF-файл:\n{str(e)}")

    def save_as_pdf(self):
        """Сохраняет текущий документ в PDF-файл."""
        current_widget = self.tab_widget.currentWidget()
        self.text_edit = current_widget.findChild(QTextEdit)
        if not isinstance(self.text_edit, QTextEdit):
            return
        filepath = filedialog.asksaveasfilename(
            title="Сохранить файл",
            defaultextension=".pdf",  # Автоматическое добавление расширения, если пользователь его не укажет
            filetypes=[("PDF файлы", "*.pdf"), ("Все файлы", "*.*")]  # Фильтрация типов файлов

        )

        if not filepath:
            return

        try:
            # base_dir = os.path.dirname(os.path.abspath(__file__))
            # font_path = os.path.join(base_dir, "fonts", "BrushScript.ttf")
            #
            # if not os.path.exists(font_path):
            #     raise FileNotFoundError(f"Шрифт не найден: {font_path}")
            #
            # doc = fitz.open()
            # page = doc.new_page(width=595, height=842)
            #
            # # Регистрируем шрифт в документе и получаем его имя (например, "F0")
            # # print(fitz.__file__)
            # # font_name = doc.embed_font(fontfile=font_path)  # вернёт что-то вроде "F0"
            # custom_font = fitz.Font("ttf", font_path)  # создаём один раз
            # embedded_name = page.insert_font(fontfile=font_path)
            # print('embedded_name', embedded_name)
            #
            # y_pos = 100.0
            # x_pos = 50.0
            # line_height = 16.0
            #
            # block = self.text_edit.document().begin()
            # while block.isValid():
            #     it = block.begin()
            #     while not it.atEnd():
            #         fragment = it.fragment()
            #         # if fragment.isEmpty():
            #         #     it += 1
            #         #     continue
            #
            #         char_fmt = fragment.charFormat()
            #         font = char_fmt.font()
            #         text = fragment.text()
            #
            #         fontsize = font.pointSize()
            #         if fontsize <= 0:
            #             fontsize = 12
            #         print('embedded_name1', embedded_name)
            #         # Используем зарегистрированное имя шрифта (F0, F1, ...)
            #         bbox = page.insert_text(
            #             (x_pos, y_pos),
            #             text,
            #             fontsize=fontsize,
            #             fontname=embedded_name,  # <-- только fontname, без font
            #             color=(0, 0, 0),
            #         )
            #
            #         x_pos = bbox[2]
            #
            #         if "\n" in text:
            #             x_pos = 50.0
            #             y_pos += line_height
            #
            #         it += 1
            #
            #     x_pos = 50.0
            #     y_pos += line_height + 4.0
            #     block = block.next()
            # print('filepath', filepath)
            # doc.save(filepath, garbage=3, deflate=True, clean=True)
            # doc.close()


            html = self.text_edit.document().toHtml()
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(html)

            # Получаем документ для печати
            # document = self.text_edit.document()
            #
            # printer = QPrinter(QPrinter.HighResolution)
            # printer.setOutputFormat(QPrinter.PdfFormat)
            # printer.setFontEmbeddingEnabled(True)
            # printer.setOutputFileName(filepath.split('/')[-1])
            # printer.setPageSize(QPrinter.A4)
            # printer.setPageMargins(0.01, 0.01, 0.01, 0.01, QPrinter.Millimeter)
            # printer.setResolution(150)
            # document.print_(printer)

            messagebox.showinfo("Успех", f"Документ сохранён как PDF:\n{filepath}")

            # После сохранения открываем PDF в новой вкладке для редактирования
            self.rendering_text(filepath)

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить PDF:\n{str(e)}")

    def normalize_font_name(self, pdf_font_name):
        """Нормализует имя шрифта из PDF для поиска в QFontDatabase."""
        patterns = [
            (r'Regular$', ''),
            (r'Bold$', ''),
            (r'Italic$', ''),
            (r'Light$', ''),
            (r'Medium$', ''),
            (r'DemiBold$', ''),
            (r'Normal$', ''),
            (r'Normal$', ''),
        ]
        print('Do Normalized', pdf_font_name)
        normalized = pdf_font_name
        for pattern, replacement in patterns:
            normalized = re.sub(pattern, replacement, normalized)
        normalized = re.sub(r'[A-Z]{2,}$', '', normalized)
        print('normalized без strip()', normalized)
        print('normalized', normalized.strip())
        return normalized.strip()

    def norm_two_word(self, font_name):
        parts = re.split(r'(?=[A-Z])', font_name)
        return ''.join(word for word in parts if word != ''
                       and parts.index(word) < 2)

    def load_font_to_database(self, font_name):
        """Загружает шрифт в QFontDatabase из файла."""
        # Добавляем в базу из папки fonts
        files = glob.glob('**/*.ttf', recursive=True)
        print('path', font_name)
        file_font = ''
        for file_path in files:

            # Получить директорию
            directory = os.path.dirname(file_path)
            print(directory)  # C:\Users\Documents

            # Получить имя файла
            filename = os.path.basename(file_path)
            print(filename.split('.')[0])  # file.txt

            if font_name == filename.split('.')[0]:
                file_font = file_path
                print('blin ', font_name == filename.split('.')[0])
                break
        print(type(file_font))
        if file_font != '':
            # Загружаем шрифт
            font_id = self.font_db.addApplicationFont(file_font)
            if font_id == -1:
                print("Не удалось загрузить шрифт")
                # return None

            # Получаем имя семейства шрифта
            families = self.font_db.applicationFontFamilies(font_id)
            if families:
                family_name = families[0]
                print(f"Шрифт загружен: {family_name}")
                return family_name
            else:
                print("Не удалось получить имя семейства шрифта")
        return False

    def find_matching_font(self, pdf_font_name):
        """Ищет подходящий шрифт в QFontDatabase для имени из PDF."""

        if pdf_font_name in self.font_cache:
            return self.font_cache[pdf_font_name]

        normalized_name = self.normalize_font_name(pdf_font_name)

        # Добавляем в базу из папки fonts
        # normalized_name = self.load_font_to_database(normalized_name)
        # normalized_name =  self.normalize_font_name(normalized_name)
        print('normalized_name1', normalized_name)
        available_fonts = self.font_db.families()
        print('available_fonts', available_fonts)
        # Точное совпадение ищем в базе
        if normalized_name in available_fonts:
            self.font_cache[pdf_font_name] = normalized_name
            print('self.font_cache', self.font_cache)
            # families = QFontDatabase.applicationFontFamilies(font_id)
            # print('families', families)
            return normalized_name

        # Частичное совпадение
        for font in available_fonts:
            if self.norm_two_word(normalized_name).lower() in self.norm_two_word(font).lower():
                self.font_cache[pdf_font_name] = font
                return font

        family_name = self.load_font_to_database(normalized_name)
        if family_name:
            return family_name
        # Резервный шрифт
        self.font_cache[pdf_font_name] = "Arial"
        return "Arial"

    def dict_styles(self, qt_font):
        dict_style = {'semicondensedsemicon': qt_font.setStretch(QFont.SemiCondensed)}
        return dict_style['semicondensedsemicon']

    def create_qt_font_from_pdf_span(self, span_data):
        """Создаёт QFont и QTextCharFormat на основе данных span'а из PDF."""
        pdf_font_name = span_data["font"]
        size = span_data["size"]
        print('size', round(size))
        print('pdf_font_name', pdf_font_name)
        qt_font_name = self.find_matching_font(pdf_font_name)
        qt_font = QFont(qt_font_name, round(size))
        print('qt_font_name', qt_font_name)
        font_lower = pdf_font_name.lower()
        dict_style = {'semicondensedsemicon': qt_font.setStretch(QFont.SemiCondensed)}
        qt_font.setStretch(QFont.SemiCondensed)
        if 'bold' in font_lower:
            print('styleBold', pdf_font_name.lower())
            qt_font.setBold(True)
        if 'italic' in font_lower:
            print('styleItalic', pdf_font_name.lower())
            qt_font.setItalic(True)
        if 'semicondensedsemicon' in font_lower:
            self.dict_styles(qt_font)
        # Создаём формат символа
        char_format = QTextCharFormat()
        char_format.setFont(qt_font)

        return qt_font, char_format, qt_font_name

    def analyze_and_map_fonts(self, filepath):
        """Анализирует PDF и сопоставляет шрифты с QFontDatabase."""
        # print('8')
        doc = fitz.open(filepath)
        # "font-weight:600"
        print(doc)
        results = []
        # print('9')
        for page_num in range(doc.page_count):
            page = doc.load_page(page_num)
            text_info = page.get_text("dict")
            print('text_info', text_info)
            page_data = {
                "blocks": []
            }
            # print('10')
            for block in text_info["blocks"]:
                if block["type"] == 0:  # Текстовый блок
                    # print('block', block["bbox"])
                    block_data = {
                        "bbox": block["bbox"],
                        "lines": []
                    }
                    for line in block["lines"]:
                        # print('line', line["bbox"])
                        line_data = {
                            "bbox": line["bbox"],
                            "spans": []
                        }

                        for span in line["spans"]:
                            # print('span', span["bbox"])
                            qt_font, char_format, matched_name = self.create_qt_font_from_pdf_span(span)
                            span_data = {
                                "original_font": span["font"],
                                "matched_qt_font": matched_name,
                                "size": span["size"],
                                "text": span["text"],
                                "qt_font": qt_font,
                                "char_format": char_format,  # Сохраняем формат для использования
                                "bbox": span["bbox"]  # Сохраняем bounding box
                            }

                            line_data["spans"].append(span_data)

                        block_data["lines"].append(line_data)

                    page_data["blocks"].append(block_data)

            results.append(page_data)
        # print('11')
        doc.close()
        return results

    def close_tab(self, index):
        """Закрывает вкладку по индексу."""
        if self.tab_widget.count() > 1:
            self.tab_widget.removeTab(index)
        else:
            messagebox.showerror("Предупреждение", "Нельзя закрыть последнюю вкладку!")


class PDFTextEditor(QMainWindow):
    def __init__(self):
        super().__init__()

        # Настройки окна
        self.configurator = WindowConfigurator()
        # Вкладки с редакторами
        self.configurator.create_tab_widget(self.configurator.close_tab)
        # Панель инструментов
        self.toolbar = QToolBar()
        # Кнопки
        self.font_btn = QPushButton("Выбрать шрифт...")
        self.open_btn = QPushButton("Открыть")
        self.save_btn = QPushButton("Сохранить как")
        self.replace_font_btn = QPushButton("Заменить шрифт из папки")  # НОВАЯ КНОПКА
        # Метод инициализации
        self.init_ui()

    def init_ui(self):
        # Настройки окна
        self.setWindowTitle("Редактор с поддержкой PDF")
        self.setGeometry(100, 100, 1200, 800)
        # Создаём начальную вкладку
        self.configurator.create_new_tab("Новая вкладка")
        # Создание центрального виджета
        self.setCentralWidget(self.configurator.add_layout())
        # Панель инструментов
        self.addToolBar(self.toolbar)
        # Создание кнопок
        # print(self.change_font)
        self.configurator.create_elem(
            self.toolbar,
            btn=[self.font_btn, self.open_btn, self.save_btn, self.replace_font_btn],
            functions=[self.configurator.change_font,
                       self.configurator.open_pdf,
                       self.configurator.save_as_pdf,
                       self.configurator.open_font_folder_dialog]
        )




if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = PDFTextEditor()
    window.show()
    sys.exit(app.exec_())
