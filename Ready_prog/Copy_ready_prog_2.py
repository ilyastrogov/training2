from PyQt5.QtWidgets import (QApplication, QMainWindow, QTabWidget, QTextEdit, QGraphicsScene,
                             QPushButton, QVBoxLayout, QWidget, QFontDialog, QFileDialog,
                             QComboBox, QToolBar, QMessageBox, QLabel, QFontComboBox, QGraphicsView)
from PyQt5.QtGui import QTextCharFormat, QFont, QTextDocument, QPdfWriter, QPainter, QFontDatabase, QPen
from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtPrintSupport import QPrinter
import sys
import fitz  # PyMuPDF для работы с PDF
import re
from abc import ABC, abstractmethod
from tkinter import messagebox, filedialog
import tkinter as tk

import os

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
    def create_new_tab(self, title):
        text_edit = QTextEdit()
        index = self.tab_widget.addTab(text_edit, title)
        self.tab_widget.setCurrentIndex(index)
        return text_edit

    # Создание кнопок
    def create_elem(self, toolbar, btn, functions):
        count = 0
        for button in btn:
            button.clicked.connect(functions[count])
            count += 1
            toolbar.addWidget(button)

    """Смена шрифта через диалоговое окно."""
    def change_font(self):
        """Смена шрифта через диалоговое окно."""
        current_widget = self.tab_widget.currentWidget()
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
    # Отрисовка текста
    def rendering_text(self, filepath):
        try:

            print('1')
            tab_title = f"Редактирование: {filepath.split('/')[-1]}"
            print('2')
            font_mapping = self.analyze_and_map_fonts(filepath)
            print('3')
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
        if not isinstance(current_widget, QTextEdit):
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
            document = current_widget.document()


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
        ]

        normalized = pdf_font_name
        for pattern, replacement in patterns:
            normalized = re.sub(pattern, replacement, normalized)
        normalized = re.sub(r'[A-Z]{2,}$', '', normalized)
        return normalized.strip()

    def load_font_to_database(self, font_path):
        """Загружает шрифт в QFontDatabase из файла."""
        # Добавляем в базу из папки fonts
        if not os.path.exists(font_path):
            print(f"Файл {font_path} не найден")
            return None

        font_id = QFontDatabase.addApplicationFont(font_path)
        if font_id == -1:
            print("Не удалось загрузить шрифт")
            return None

        # Получаем имя семейства шрифта
        families = QFontDatabase.applicationFontFamilies(font_id)
        if families:
            family_name = families[0]
            print(f"Шрифт загружен: {family_name}")
            return family_name
        else:
            print("Не удалось получить имя семейства шрифта")
            return None

    def find_matching_font(self, pdf_font_name):
        """Ищет подходящий шрифт в QFontDatabase для имени из PDF."""

        if pdf_font_name in self.font_cache:
            return self.font_cache[pdf_font_name]

        normalized_name = self.normalize_font_name(pdf_font_name)

        # normalized_name = self.load_font_to_database(normalized_name)
        print(normalized_name)
        available_fonts = self.font_db.families()

        # Точное совпадение
        if normalized_name in available_fonts:
            self.font_cache[pdf_font_name] = normalized_name
            return normalized_name

        # Частичное совпадение
        for font in available_fonts:
            if normalized_name.lower() in font.lower():
                self.font_cache[pdf_font_name] = font
                return font

        normalized_name = normalized_name + '.ttf'
        # Добавляем в базу из папки fonts
        normalized_name = self.load_font_to_database(normalized_name)
        print(normalized_name)
        available_fonts = self.font_db.families()

        # Точное совпадение ищем в базе
        if normalized_name in available_fonts:
            self.font_cache[pdf_font_name] = normalized_name
            return normalized_name

        # Резервный шрифт
        self.font_cache[pdf_font_name] = "Arial"
        return "Arial"

    def create_qt_font_from_pdf_span(self, span_data):
        """Создаёт QFont и QTextCharFormat на основе данных span'а из PDF."""
        pdf_font_name = span_data["font"]
        size = span_data["size"]
        print('size', size)
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
        print('8')
        doc = fitz.open(filepath)
        results = []
        print('9')
        for page_num in range(doc.page_count):
            page = doc.load_page(page_num)
            text_info = page.get_text("dict")

            page_data = {
                "blocks": []
            }
            print('10')
            for block in text_info["blocks"]:
                if block["type"] == 0:  # Текстовый блок
                    print('block', block["bbox"])
                    block_data = {
                        "bbox": block["bbox"],
                        "lines": []
                    }
                    for line in block["lines"]:
                        print('line', line["bbox"])
                        line_data = {
                            "bbox": line["bbox"],
                            "spans": []
                        }

                        for span in line["spans"]:
                            print('span', span["bbox"])
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
        print('11')
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
            btn=[self.font_btn, self.open_btn, self.save_btn],
            functions=[self.configurator.change_font,
                       self.configurator.open_pdf,
                       self.configurator.save_as_pdf]
        )


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = PDFTextEditor()
    window.show()
    sys.exit(app.exec_())
