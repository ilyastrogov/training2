from PyQt5.QtWidgets import (QApplication, QMainWindow, QTabWidget, QTextEdit, QGraphicsScene,
                             QPushButton, QVBoxLayout, QWidget, QFontDialog, QFileDialog,
                             QComboBox, QToolBar, QMessageBox, QLabel, QListWidget,
                             QFontComboBox, QGraphicsView, QListWidgetItem, QDialogButtonBox)
from PyQt5.QtGui import (QTextCharFormat, QFont, QTextDocument, QPdfWriter, QTextCursor,
                         QPainter, QFontDatabase, QPen)
from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtWidgets import QSizePolicy, QDialog
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
        self.font_paths = font_paths
        self.selected_path = None
        self.setWindowTitle("Выберите шрифт из папки fonts")
        self.setMinimumSize(400, 300)

        layout = QVBoxLayout()

        self.list_widget = QListWidget()
        # Заполняем список именами файлов
        for path in self.font_paths:
            filename = os.path.basename(path)
            item = QListWidgetItem(filename)
            item.setData(Qt.UserRole, path)  # Сохраняем полный путь в данных элемента
            self.list_widget.addItem(item)

        self.list_widget.itemClicked.connect(self.on_item_clicked)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout.addWidget(QLabel("Список шрифтов (.ttf, .otf):"))
        layout.addWidget(self.list_widget)
        layout.addWidget(buttons)
        self.setLayout(layout)

    def on_item_clicked(self, item):
        self.selected_path = item.data(Qt.UserRole)
        # Можно добавить предварительный просмотр или просто подтверждение

    def get_selected_font_path(self):
        return self.selected_path
# Настройки окна
class WindowConfigurator(AddLayout, CreateTabWidget, CreateNewTab,
                         SavePdf, CloseTab, PDFFontMapper,
                         CreateElem, ChangeFont, OpenPdf, RenderingText):
    def __init__(self):
        super().__init__()
        # Вкладки с редакторами
        self.tab_widget = QTabWidget()
        # Основной контейнер
        self.central_widget = QWidget()
        self.layout = QVBoxLayout()
        # Окно выбора файла
        self.root = tk.Tk()
        self.root.withdraw()
        # База шрифтов
        self.font_db = QFontDatabase()
        self.font_cache = {}  # Кэш для ускорения
        self.loaded_font_ids = []  # Храним ID загруженных шрифтов, чтобы не дублировать

    # Вкладки с редакторами
    def create_tab_widget(self, close_tab):
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.tabCloseRequested.connect(close_tab)
        return self.tab_widget
    # Вставляем макет
    def add_layout(self):
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
        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setAlignment(Qt.AlignCenter)  # Центрируем по горизонтали и вертикали

        text_edit = QTextEdit()
        text_edit.setFixedSize(page_width, page_height)
        text_edit.setSizePolicy(QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed))
        text_edit.setViewportMargins(15, 15, 15, 15)  # Отступы внутри QTextEdit

        container_layout.addWidget(text_edit)

        index = self.tab_widget.addTab(container, title)
        self.tab_widget.setCurrentIndex(index)
        return text_edit

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

        # --- НОВАЯ ФУНКЦИЯ: Открытие диалога выбора шрифта ---
    def open_font_folder_dialog(self):
        """Ищет шрифты в папке 'fonts' рядом со скриптом и показывает диалог."""
        script_dir = os.path.dirname(os.path.abspath(__file__))
        font_folder = os.path.join(script_dir, 'fonts')

        if not os.path.exists(font_folder):
            messagebox.showwarning("Папка не найдена",
                                   f"Папка '{font_folder}' не существует. Создайте её и положите туда .ttf/.otf файлы.")
            return

        # Ищем все ttf и otf файлы рекурсивно
        patterns = ['*.ttf', '*.otf']
        font_files = []
        for pattern in patterns:
            font_files.extend(glob.glob(os.path.join(font_folder, pattern), recursive=True))
            font_files.extend(glob.glob(os.path.join(font_folder, '**', pattern), recursive=True))

        if not font_files:
            messagebox.showinfo("Шрифты не найдены", "В папке fonts нет файлов .ttf или .otf")
            return

        dialog = FontListDialog(font_files, self.tab_widget)
        if dialog.exec_() == QDialog.Accepted:
            selected_path = dialog.get_selected_font_path()
            if selected_path:
                self.apply_font_to_matching_text(selected_path)

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

    def apply_font_to_matching_text(self, font_path):
        """Загружает шрифт и применяет его к тексту с похожим названием."""
        current_widget = self.tab_widget.currentWidget()
        text_edit = current_widget.findChild(QTextEdit)

        if not isinstance(text_edit, QTextEdit):
            return

        # 1. Загружаем шрифт в базу, если еще не загружен
        font_id = QFontDatabase.addApplicationFont(font_path)
        if font_id == -1:
            messagebox.showerror("Ошибка", "Не удалось загрузить шрифт из файла.")
            return

        self.loaded_font_ids.append(font_id)
        families = QFontDatabase.applicationFontFamilies(font_id)
        if not families:
            return

        new_family_name = families[0]
        print(f"Загружен шрифт: {new_family_name} из {font_path}")

        # Получаем имя файла без расширения для сравнения (например, "Arial-Bold" -> ищем совпадения с "Arial")
        base_name = os.path.splitext(os.path.basename(font_path))[0]
        # Очищаем имя от суффиксов типа Bold, Italic для поиска совпадений
        clean_base = re.sub(r'(Bold|Italic|Regular|Light|Medium)', '', base_name, flags=re.IGNORECASE).strip()

        doc = text_edit.document()
        cursor = QTextCursor(doc)
        cursor.beginEditBlock()

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
                    if clean_base.lower() in current_family.lower():
                        match = True
                    elif current_family.lower() in clean_base.lower():
                        match = True

                    # Также проверяем точное совпадение (на случай если пользователь кликнул на тот же шрифт)
                    if current_family == new_family_name:
                        match = True

                    if match:
                        # Создаем новый формат с новым семейством, сохраняя жирность/курсив если возможно
                        new_fmt = QTextCharFormat(fmt)
                        new_font = QFont(new_family_name)

                        # Пытаемся сохранить стиль (Bold/Italic), если новый шрифт поддерживает эти веса
                        if current_font.bold():
                            new_font.setBold(True)
                        if current_font.italic():
                            new_font.setItalic(True)

                        new_fmt.setFont(new_font)

                        # Применяем формат к этому фрагменту
                        cursor.setPosition(fragment.position())
                        cursor.setPosition(fragment.position() + fragment.length(), QTextCursor.KeepAnchor)
                        cursor.mergeCharFormat(new_fmt)
                        applied_count += 1

                iterator += 1
            block = block.next()

        cursor.endEditBlock()
        messagebox.showinfo("Готово", f"Шрифт '{new_family_name}' применен к {applied_count} фрагментам текста.")

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
        text_edit = current_widget.findChild(QTextEdit)
        current_widget = text_edit
        cursor = current_widget.textCursor()

        if cursor.hasSelection():
            fmt = QTextCharFormat()
            fmt.setFont(font)
            cursor.mergeCharFormat(fmt)

        active_format = QTextCharFormat()
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
        self.rendering_text(filepath)

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
        text_edit = QTextEdit()
        text_edit.setFixedSize(width, height)
        text_edit.setSizePolicy(QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed))
        index = self.tab_widget.addTab(text_edit, title)
        self.tab_widget.setCurrentIndex(index)
        return text_edit
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
            text_edit = self.create_new_tab(tab_title)
            print('4')
            cursor = text_edit.textCursor()

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
        current_widget1 = current_widget.findChild(QTextEdit)
        if not isinstance(current_widget1, QTextEdit):
            return
        filepath = filedialog.asksaveasfilename(
            title="Сохранить файл",
            defaultextension=".pdf",  # Автоматическое добавление расширения, если пользователь его не укажет
            filetypes=[("PDF файлы", "*.pdf"), ("Все файлы", "*.*")]  # Фильтрация типов файлов

        )

        if not filepath:
            return

        try:
            # Получаем документ для печати
            document = current_widget1.document()


            printer = QPrinter(QPrinter.HighResolution)
            printer.setOutputFormat(QPrinter.PdfFormat)
            printer.setOutputFileName(filepath.split('/')[-1])
            printer.setPageSize(QPrinter.A4)
            printer.setPageMargins(0.1, 0.1, 0.1, 0.1, QPrinter.Millimeter)

            document.print_(printer)

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
        ]

        normalized = pdf_font_name
        for pattern, replacement in patterns:
            normalized = re.sub(pattern, replacement, normalized)
        normalized = re.sub(r'[A-Z]{2,}$', '', normalized)
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
            font_id = QFontDatabase.addApplicationFont(file_font)
            if font_id == -1:
                print("Не удалось загрузить шрифт")
                # return None

            # Получаем имя семейства шрифта
            families = QFontDatabase.applicationFontFamilies(font_id)
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

    def create_qt_font_from_pdf_span(self, span_data):
        """Создаёт QFont и QTextCharFormat на основе данных span'а из PDF."""
        pdf_font_name = span_data["font"]
        size = span_data["size"]
        print('pdf_font_name', pdf_font_name)
        qt_font_name = self.find_matching_font(pdf_font_name)
        qt_font = QFont(qt_font_name, int(size))

        font_lower = pdf_font_name.lower()
        if 'bold' in font_lower:
            qt_font.setBold(True)
        if 'italic' in font_lower:
            qt_font.setItalic(True)

        # Создаём формат символа
        char_format = QTextCharFormat()
        char_format.setFont(qt_font)

        return qt_font, char_format, qt_font_name

    def analyze_and_map_fonts(self, filepath):
        """Анализирует PDF и сопоставляет шрифты с QFontDatabase."""
        # print('8')
        doc = fitz.open(filepath)
        results = []
        # print('9')
        for page_num in range(doc.page_count):
            page = doc.load_page(page_num)
            text_info = page.get_text("dict")

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
        self.tab_widget = self.configurator.create_tab_widget(self.configurator.close_tab)
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


# class MonotypeCorsivaDownloader:
#     def __init__(self, download_folder="downloaded_fonts"):
#         self.download_folder = Path(download_folder)
#         self.download_folder.mkdir(exist_ok=True)
#         self.base_url = "https://ofont.ru"
#         self.session = requests.Session()
#         self.session.headers.update({
#             'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
#         })
#
#     def find_font_page(self, font_name="Monotype Corsiva"):
#         """Ищет страницу шрифта по его названию через поиск на сайте."""
#         # search_url = f"{self.base_url}/search"
#         # print('search_url', search_url)
#         print(f"Загружаем страницу: {self.base_url}")
#         response = self.session.get(self.base_url, timeout=10)
#         response.raise_for_status()
#
#         soup = BeautifulSoup(response.text, 'html.parser')
#         search_input  = soup.find('input', id='search')
#         print('search', search_input)
#
#         # Ищем форму, содержащую это поле
#         form = search_input.find_parent('form')
#         search_url1 = ''
#         if form:
#             action_url = form.get('action', '')  # URL для отправки формы
#             method = form.get('method', 'GET').upper()  # метод отправки
#
#             # Преобразуем относительный URL в абсолютный
#             # base_url = 'https://example.com'
#             search_url1 = urljoin(self.base_url, action_url)
#
#             print(f"URL формы поиска: {search_url1}")
#             print(f"Метод: {method}")
#         else:
#             print("Форма не найдена")
#         search_url = ''
#         params = {'q': font_name}
#         response = self.session.get(search_url1, params=params, timeout=10)
#         response.raise_for_status()
#         print('resp', response.raise_for_status())
#         soup = BeautifulSoup(response.text, 'html.parser')
#
#         font_links = soup.find_all('a', href=re.compile(r'/view/\d+'))
#         print('ddddd', font_links)
#
#         for link in font_links:
#
#             href = link.get('href')
#
#             pattern = rf'{font_name}'
#             match = re.search(pattern, str(link))
#             # # Проверяем, что название шрифта содержится в тексте ссылки (нестрогое совпадение)
#             if match and href:
#                 # Формируем полный URL
#                 if href.startswith('/'):
#                     search_url = f"{self.base_url}{href}"
#                     print('22', search_url)
#         return search_url
#
#
#     def _make_absolute_url(self, relative_url, base_url):
#         """Создаёт абсолютный URL из относительного."""
#         if relative_url.startswith('http'):
#             return relative_url
#         elif relative_url.startswith('/'):
#             # Берём домен из base_url
#             from urllib.parse import urlparse
#             base_domain = f"{urlparse(base_url).scheme}://{urlparse(base_url).netloc}"
#             return f"{base_domain}{relative_url}"
#         else:
#             # Относительный путь в текущей директории
#             return f"{base_url.rsplit('/', 1)[0]}/{relative_url}"
#
#     def find_download_link(self, page_url):
#         """Ищет реальную ссылку для скачивания шрифта на указанной странице."""
#         try:
#             print(f"Загружаем страницу: {page_url}")
#             response = self.session.get(page_url, timeout=10)
#             response.raise_for_status()
#
#             soup = BeautifulSoup(response.text, 'html.parser')
#
#             # Вариант 1: ищем прямые ссылки на .ttf файлы
#             ttf_links = soup.find_all('a', href=re.compile(r'\.ttf$', re.IGNORECASE))
#             for link in ttf_links:
#                 href = link.get('href')
#                 if href and not href.startswith('#'):
#                     full_url = self._make_absolute_url(href, page_url)
#                     print(f"Прямая ссылка на TTF: {full_url}")
#                     return full_url
#
#             # Вариант 2: ищем кнопки скачивания (обычно класс 'btn' или 'download-btn')
#             download_buttons = soup.find_all('a', class_=re.compile(r'btn|download', re.IGNORECASE))
#             for button in download_buttons:
#                 href = button.get('href')
#                 onclick = button.get('onclick')
#
#                 if href:
#                     full_url = self._make_absolute_url(href, page_url)
#                     print(f"Кнопка скачивания: {full_url}")
#                     return full_url
#                 elif onclick and 'download' in onclick.lower():
#                     # Иногда ссылка генерируется через JavaScript
#                     match = re.search(r"['\"]([^'\"]+)", onclick)
#                     if match:
#                         js_url = match.group(1)
#                         full_url = self._make_absolute_url(js_url, page_url)
#                         print(f"Ссылка из JavaScript: {full_url}")
#                         return full_url
#
#             # Вариант 3: ищем формы с действием download
#             download_forms = soup.find_all('form', action=re.compile(r'download', re.IGNORECASE))
#             for form in download_forms:
#                 action = form.get('action')
#                 if action:
#                     full_url = self._make_absolute_url(action, page_url)
#                     print(f"Форма скачивания: {full_url}")
#                     return full_url
#
#             print("Не удалось найти ссылку для скачивания")
#             return None
#         except Exception as e:
#             print(f"Ошибка при поиске ссылки: {e}")
#             return None
#
#     def download_font(self, link, filename="Monotype_Corsiva.ttf"):
#         """Скачивает шрифт по найденной ссылке с проверкой содержимого."""
#         try:
#             if not link or link.startswith('#') or link.startswith('javascript:'):
#                 print("Недопустимая ссылка для скачивания")
#                 return False
#
#             headers = self.session.headers.copy()
#             # Не добавляем Referer с кириллицей — это частая причина ошибки
#             # headers['Referer'] = self._encode_url(self.search_url)  # Убираем эту строку
#
#             response = self.session.get(
#                 link,
#                 stream=True,
#                 timeout=30,
#                 headers=headers,
#                 allow_redirects=True
#             )
#             response.raise_for_status()
#
#             # Проверка размера файла
#             content_length = response.headers.get('content-length')
#             if content_length and int(content_length) == 0:
#                 print("Предупреждение: сервер сообщает о нулевом размере файла")
#
#             save_path = self.download_folder / filename
#
#             with open(save_path, 'wb') as f:
#                 for chunk in response.iter_content(chunk_size=8192):
#                     if chunk:
#                         f.write(chunk)
#
#             # Проверка размера скачанного файла
#             file_size = save_path.stat().st_size
#             if file_size == 0:
#                 print("Ошибка: файл скачан, но имеет нулевой размер")
#                 save_path.unlink()  # Удаляем пустой файл
#                 return False
#
#             print(f"Шрифт успешно скачан: {save_path} (размер: {file_size} байт)")
#             return save_path
#         except Exception as e:
#             print(f"Ошибка скачивания: {e}")
#             return False
#
#     def run(self, font_name="Monotype Corsiva", filename=None):
#         """Основной метод для запуска процесса."""
#         print(f"Начинаем поиск шрифта: {font_name}...")
#
#         # Шаг 1: находим страницу шрифта
#         font_page_url = self.find_font_page(font_name)
#         if not font_page_url:
#             print("Не удалось найти страницу шрифта")
#             return False
#
#         # Шаг 2: находим ссылку для скачивания на этой странице
#         download_link = self.find_download_link(font_page_url)
#         if not download_link:
#             print("Не удалось найти ссылку для скачивания")
#             return False
#
#         print(f"Найденная ссылка для скачивания: {download_link}")
#
#         # Определяем имя файла (если не задано)
#         if not filename:
#             filename = f"{font_name.replace(' ', '_')}.ttf"
#
#         # Шаг 3: скачиваем шрифт
#         success = self.download_font(download_link, filename)
#         return success

if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = PDFTextEditor()
    window.show()
    sys.exit(app.exec_())
