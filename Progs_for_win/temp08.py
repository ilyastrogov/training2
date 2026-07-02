from PyQt5.QtWidgets import (QApplication, QMainWindow, QTabWidget, QGraphicsScene,
                             QPushButton, QVBoxLayout, QWidget, QFontDialog, QFileDialog,
                             QComboBox, QToolBar, QMessageBox, QLabel, QFontComboBox, QGraphicsView)
from PyQt5.QtGui import (QTextCharFormat, QFont, QTextDocument, QPdfWriter,
                         QPainter, QFontDatabase, QPen, QTextCursor, QFontMetrics)
from PyQt5.QtCore import Qt, QRectF, QPointF
from PyQt5.QtPrintSupport import QPrinter
import sys
import fitz  # PyMuPDF для работы с PDF
import re
from abc import ABC, abstractmethod
import tkinter as tk
from tkinter import messagebox, filedialog

from PySide6.QtGui import QColor


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
        """Создаёт новую вкладку с QGraphicsView."""
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
    def set_active_font_on_canvas(self, font, item):
        pass

""" Открытие файла """
class OpenPdf(ABC):
    @abstractmethod
    def open_pdf(self):
        pass
class PDFCanvas(QGraphicsView):
    def __init__(self):
        super().__init__()
        self.scene = QGraphicsScene()
        self.setScene(self.scene)
        a4_width, a4_height = 595, 842
        self.scene.setSceneRect(0, 0, a4_width, a4_height)

        # Рисуем границы страницы для отладки
        self.scene.addRect(0, 0, a4_width, a4_height, QPen(Qt.gray))

    def add_text_item(self, text, x, y, font, color=None):
        """Добавляет текст в сцену с проверкой границ."""
        if color is None:
            color = Qt.black
        elif isinstance(color, int):
            color = Qt.GlobalColor(color)

        text_item = self.scene.addText(text, font)
        text_item.setDefaultTextColor(color)

        # Проверка границ: не выходим за пределы сцены
        scene_rect = self.scene.sceneRect()
        max_x = scene_rect.width() - 20  # отступ справа 20 px
        max_y = scene_rect.height() - 20  # отступ снизу 20 px

        final_x = max(20, min(x, max_x))  # отступ слева 20 px
        final_y = max(20, min(y, max_y))  # отступ сверху 20 px

        text_item.setPos(final_x, final_y)
        return text_item

    def clear_canvas(self):
        """Очищает холст."""
        self.scene.clear()
# class PDFCanvas(QGraphicsView):
#     """Холст для точного отображения текста из PDF с сохранением позиционирования."""
#
#     def __init__(self):
#         super().__init__()
#         self.scene = QGraphicsScene()
#         self.setScene(self.scene)
#         # Устанавливаем размер A4 в пикселях (72 DPI)
#         a4_width, a4_height = 595, 842
#         self.scene.setSceneRect(0, 0, a4_width, a4_height)
#
#         # Рисуем границы страницы для отладки
#         self.scene.addRect(0, 0, a4_width, a4_height, QPen(Qt.gray))
#
#     def add_text_item(self, text, x, y, font, color=Qt.black):
#         """Добавляет текст в сцену с точным позиционированием."""
#         text_item = self.scene.addText(text, font)
#         color = Qt.GlobalColor(color)
#         text_item.setDefaultTextColor(color)
#         text_item.setPos(x, y)
#         return text_item
#
#     def clear_canvas(self):
#         """Очищает холст."""
#         self.scene.clear()

class PDFFontMapper:
    # def __init__(self):
    #     self.font_db = QFontDatabase()
    #     self.font_cache = {}  # Кэш для ускорения
    def __init__(self):
        self.font_db = QFontDatabase()
        self.font_cache = {}

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

    def find_matching_font(self, pdf_font_name):
        """Ищет подходящий шрифт в QFontDatabase для имени из PDF."""
        if pdf_font_name in self.font_cache:
            return self.font_cache[pdf_font_name]

        normalized_name = self.normalize_font_name(pdf_font_name)

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

        # Резервный шрифт
        self.font_cache[pdf_font_name] = "Arial"
        return "Arial"

    def create_qt_font_from_pdf_span(self, span_data):
        """Создаёт QFont и QTextCharFormat на основе данных span'а из PDF."""
        pdf_font_name = span_data["font"]
        size = span_data["size"]

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

    # def pdf_to_qt_coords(self, pdf_y, page_height):
    #     """Конвертирует Y‑координату из PDF (низ) в Qt (верх)."""
    #     return page_height - pdf_y
    def pdf_to_qt_coords(self, pdf_y, page_height):
        """Конвертирует Y‑координату из PDF (низ) в Qt (верх)."""
        return page_height - pdf_y

    def analyze_and_map_fonts(self, filepath):
        doc = fitz.open(filepath)
        results = []
        page_height = 842  # A4 при 72 DPI

        for page_num in range(doc.page_count):
            page = doc.load_page(page_num)
            text_info = page.get_text("dict")

            page_data = {"blocks": [], "page_height": page_height}

            for block in text_info["blocks"]:
                if block["type"] == 0:  # Текстовый блок
                    block_data = {"bbox": block["bbox"], "lines": []}
                    for line in block["lines"]:
                        line_data = {"bbox": line["bbox"], "spans": []}
                        for span in line["spans"]:
                    # Конвертируем координаты
                            x0, pdf_y0, x1, pdf_y1 = span["bbox"]
                            qt_y0 = self.pdf_to_qt_coords(pdf_y0, page_height)
                            qt_y1 = self.pdf_to_qt_coords(pdf_y1, page_height)

                # Рассчитываем высоту строки для позиционирования следующей строки
                            line_height = span["size"] * 1.2

                            qt_font, char_format, matched_name = self.create_qt_font_from_pdf_span(span)
                            span_data = {
                                "original_font": span["font"],
                                "matched_qt_font": matched_name,
                                "size": span["size"],
                                "text": span["text"],
                                "qt_font": qt_font,
                                "char_format": char_format,
                                "bbox": [x0, qt_y0, x1, qt_y1],
                                "line_height": line_height
                            }
                            line_data["spans"].append(span_data)

                        block_data["lines"].append(line_data)

                    page_data["blocks"].append(block_data)
            results.append(page_data)
        doc.close()
        return results
    # def analyze_and_map_fonts(self, filepath):
    #     """Анализирует PDF и сопоставляет шрифты с QFontDatabase."""
    #     doc = fitz.open(filepath)
    #     results = []
    #     page_height = 842  # Высота A4 в пикселях при 72 DPI
    #
    #     for page_num in range(doc.page_count):
    #         page = doc.load_page(page_num)
    #         text_info = page.get_text("dict")
    #
    #         page_data = {"blocks": []}
    #
    #         for block in text_info["blocks"]:
    #             if block["type"] == 0:  # Текстовый блок
    #                 block_data = {"bbox": block["bbox"], "lines": []}
    #                 for line in block["lines"]:
    #                     line_data = {"bbox": line["bbox"], "spans": []}
    #                     for span in line["spans"]:
    #                 # Конвертируем координаты
    #                         x0, pdf_y0, x1, pdf_y1 = span["bbox"]
    #                         qt_y0 = self.pdf_to_qt_coords(pdf_y0, page_height)
    #                         qt_y1 = self.pdf_to_qt_coords(pdf_y1, page_height)
    #
    #                         qt_font, char_format, matched_name = self.create_qt_font_from_pdf_span(span)
    #                         span_data = {
    #                             "original_font": span["font"],
    #                             "matched_qt_font": matched_name,
    #                             "size": span["size"],
    #                             "text": span["text"],
    #                             "qt_font": qt_font,
    #                             "char_format": char_format,
    #                             "bbox": [x0, qt_y0, x1, qt_y1]  # Уже конвертированные координаты
    #                         }
    #                         line_data["spans"].append(span_data)
    #                     block_data["lines"].append(line_data)
    #                 page_data["blocks"].append(block_data)
    #         results.append(page_data)
    #     doc.close()
    #     return results

# Настройки окна


class WindowConfigurator(AddLayout, CreateTabWidget, CreateNewTab, CreateElem, ChangeFont, OpenPdf):
    def __init__(self):
        super().__init__()
        # Вкладки с редакторами
        self.tab_widget = QTabWidget()
        # Основной контейнер
        self.central_widget = QWidget()
        self.layout = QVBoxLayout()

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

    # Создание новой вкладки с PDFCanvas
    def create_new_tab(self, title):
        canvas = PDFCanvas()
        index = self.tab_widget.addTab(canvas, title)
        self.tab_widget.setCurrentIndex(index)
        return canvas

    # Создание кнопок
    def create_elem(self, toolbar, btn, functions):
        count = 0
        for button in btn:
            button.clicked.connect(functions[count])
            count += 1
            toolbar.addWidget(button)

    """Смена шрифта через диалоговое окно."""
    def change_font(self):
        """Смена шрифта для выделенного текста на холсте."""
        current_widget = self.tab_widget.currentWidget()
        if not isinstance(current_widget, PDFCanvas):
            return

        current_scene = current_widget.scene
        selected_items = current_scene.selectedItems()

        if not selected_items:
            QMessageBox.warning(self.central_widget, "Предупреждение", "Сначала выделите текст на холсте")
            return

        # Получаем текущий шрифт первого выделенного элемента для инициализации диалога
        initial_font = QFont("Arial", 12)  # Резервный шрифт
        for item in selected_items:
            if hasattr(item, 'font'):
                initial_font = item.font()
                break

        font, ok = QFontDialog.getFont(initial_font)
        if ok:
            self.set_active_font_on_canvas(font, selected_items)

    def set_active_font_on_canvas(self, font, items):
        """Устанавливает шрифт для выделенных элементов на холсте."""
        for item in items:
            if hasattr(item, 'setFont'):
                item.setFont(font)

    # Открытие файла
    def open_pdf(self):
        """Открывает PDF-файл и отображает на холсте с точным позиционированием."""
        root = tk.Tk()
        root.withdraw()

        filepath = filedialog.askopenfilename(
            title="Открыть файл",
            filetypes=[("PDF files", "*.pdf"),
                       ("All files", "*.*")]
        )
        if not filepath:
            return

        try:
            tab_title = f"Редактирование: {filepath.split('/')[-1]}"
            font_mapper = PDFFontMapper()
            font_mapping = font_mapper.analyze_and_map_fonts(filepath)
            canvas = self.create_new_tab(tab_title)

            current_y = 20  # начинаем с отступом сверху 20 px
            line_spacing = 10  # межстрочный интервал

            for page_data in font_mapping:
                page_height = page_data["page_height"]
                for block in page_data["blocks"]:
                    for line in block["lines"]:
                        line_spans = line["spans"]
                        if not line_spans:
                            continue

                # Берём Y первой span'ы в строке — это верхняя граница строки
                        first_span = line_spans[0]
                        x0, y0, x1, y1 = first_span["bbox"]

                # Устанавливаем Y для всей строки
                        current_y = y0

                        for span in line_spans:
                            text = span["text"].strip()
                            if not text:
                                continue

                            qt_font = span["qt_font"]
                            canvas.add_text_item(text, x0, current_y, qt_font)

                            # Сдвигаем X для следующего span'а в строке
                            x0 += self.estimate_text_width(text, qt_font)

                        # Переходим к следующей строке с учётом межстрочного интервала
                            current_y += span["line_height"] + line_spacing

            messagebox.showinfo("Успех", f"PDF-файл {tab_title} успешно открыт!")

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось открыть PDF-файл:\n{str(e)}")

    def estimate_text_width(self, text, font):
        """Оценивает ширину текста в пикселях."""
        metrics = QFontMetrics(font)
        return metrics.width(text)
    # def open_pdf(self):
    #     """Открывает PDF-файл и отображает на холсте с точным позиционированием."""
    #     root = tk.Tk()
    #     root.withdraw()  # скрываем основное окно
    #
    #     filepath = filedialog.askopenfilename(
    #         title="Открыть файл",
    #         filetypes=[("PDF files", "*.pdf"),
    #                    ("All files", "*.*")]
    #     )
    #     if not filepath:
    #         return
    #
    #     try:
    #         tab_title = f"Редактирование: {filepath.split('/')[-1]}"
    #         font_mapper = PDFFontMapper()
    #         font_mapping = font_mapper.analyze_and_map_fonts(filepath)
    #         canvas = self.create_new_tab(tab_title)
    #
    #         # Отображаем текст с точным позиционированием
    #         for page_data in font_mapping:
    #             for block in page_data["blocks"]:
    #                 for line in block["lines"]:
    #                     for span in line["spans"]:
    #                         x0, y0, x1, y1 = span["bbox"]
    #                         canvas.add_text_item(
    #             span["text"],
    #             x0,
    #             y0,
    #             span["qt_font"]
    #         )
    #
    #         messagebox.showinfo("Успех", f"PDF-файл {tab_title} успешно открыт!")
    #
    #     except Exception as e:
    #         messagebox.showerror("Ошибка", f"Не удалось открыть PDF-файл:\n{str(e)}")

class PDFTextEditor(QMainWindow):
    def __init__(self):
        super().__init__()

        # Настройки окна
        self.configurator = WindowConfigurator()
        # Вкладки с редакторами
        self.tab_widget = self.configurator.create_tab_widget(self.close_tab)
        # Панель инструментов
        self.toolbar = QToolBar()
        # Кнопки
        self.font_btn = QPushButton("Выбрать шрифт...")
        self.open_btn = QPushButton("Открыть PDF")
        self.save_btn = QPushButton("Сохранить как PDF")

        self.init_ui()

    def init_ui(self):
        # Настройки окна
        self.setWindowTitle("Редактор PDF с точным позиционированием")
        self.setGeometry(100, 100, 1200, 800)
        # Создаём начальную вкладку
        self.configurator.create_new_tab("Новая вкладка")
        # Создание центрального виджета
        self.setCentralWidget(self.configurator.add_layout())
        # Панель инструментов
        self.addToolBar(self.toolbar)
        # Создание кнопок
        self.configurator.create_elem(
            self.toolbar,
            btn=[self.font_btn, self.open_btn, self.save_btn],
            functions=[self.configurator.change_font, self.configurator.open_pdf, self.save_as_pdf]
        )

    def save_as_pdf(self):
        """Сохраняет текущий холст в PDF-файл."""
        current_widget = self.tab_widget.currentWidget()
        if not isinstance(current_widget, PDFCanvas):
            return

        filepath, _ = QFileDialog.getSaveFileName(
            self, "Сохранить как PDF", "", "PDF files (*.pdf)"
        )
        if not filepath:
            return

        try:
            printer = QPrinter(QPrinter.HighResolution)
            printer.setOutputFormat(QPrinter.PdfFormat)
            printer.setOutputFileName(filepath)
            printer.setPageSize(QPrinter.A4)
            printer.setPageMargins(0.1, 0.1, 0.1, 0.1, QPrinter.Millimeter)

            painter = QPainter(printer)
            current_widget.render(painter)
            painter.end()

            QMessageBox.information(self, "Успех", f"Документ сохранён как PDF:\n{filepath}")

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить PDF:\n{str(e)}")

    def close_tab(self, index):
        """Закрывает вкладку по индексу."""
        if self.tab_widget.count() > 1:
            self.tab_widget.removeTab(index)
        else:
            QMessageBox.warning(self, "Предупреждение", "Нельзя закрыть последнюю вкладку!")

if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = PDFTextEditor()
    window.show()
    sys.exit(app.exec_())
