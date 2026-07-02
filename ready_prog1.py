from PyQt5.QtWidgets import (QApplication, QMainWindow, QTabWidget, QTextEdit,
                             QPushButton, QVBoxLayout, QWidget, QFontDialog, QFileDialog,
                             QComboBox, QToolBar, QMessageBox, QLabel, QFontComboBox)
from PyQt5.QtGui import QTextCharFormat, QFont, QTextDocument, QPdfWriter, QPainter, QFontDatabase
from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtPrintSupport import QPrinter
import sys
import fitz  # PyMuPDF для работы с PDF
import re
from abc import ABC, abstractmethod

# class InitUI(ABC):
#     def __init__(self):
#         pass

#  Настройки окна
class WindowConfigurator(ABC):
    @abstractmethod
    def setup_window(self):
        pass

# class CreateContainer(ABC):
#     @abstractmethod
#     def create_container(self):
#         pass
# Вкладки с редакторами
class CreateTabWidget(ABC):
    @abstractmethod
    def create_tab_widget(self):
        pass
# Вставляем макет
class AddLayout(ABC):
    @abstractmethod
    def add_layout(self):
        pass

class CreateToolbar(ABC):
    @abstractmethod
    def create_toolbar(self):
        pass
# Выпадающий список шрифтов
# class CreateFont(ABC):
#     @abstractmethod
#     def create_font_combo(self):
#         pass
# Создание кнопок
class CreateElem(ABC):
    @abstractmethod
    def create_elem(self, btn, functions):
        pass

class CreateNewTab(ABC):
    @abstractmethod
    def create_new_tab(self, title):
        pass

class ElementCreator(ABC):
    @abstractmethod
    def create1(self):
        pass

# class ChangeFont(ABC):
#     @abstractmethod
#     def change_font(self):
#         pass

# class ChangeFontFromCombo(ABC):
#     @abstractmethod
#     def change_font_from_combo(self, font_family):
#         pass

# class SetActiveFont(ABC):
#     @abstractmethod
#     def set_active_font(self, font):
#         pass
#
# class OpenPdf(ABC):
#     @abstractmethod
#     def open_pdf(self):
#         pass
#
# class SaveAsPdf(ABC):
#     @abstractmethod
#     def save_as_pdf(self):
#         pass
#
# class OpenSavedPdfForEdit(ABC):
#     @abstractmethod
#     def open_saved_pdf_for_edit(self, filepath):
#         pass
#
# class CloseTab(ABC):
#     @abstractmethod
#     def close_tab(self, index):
#         pass
#
# class NormalizeFontName(ABC):
#     @abstractmethod
#     def normalize_font_name(self, pdf_font_name):
#         pass
#
# class FindMatchingFont(ABC):
#     @abstractmethod
#     def find_matching_font(self, pdf_font_name):
#         pass
#
#
# class CreateFontFromSpan(ABC):
#     @abstractmethod
#     def create_qt_font_from_pdf_span(self, span_data):
#         pass
#
# class AnalyzeAndMapFonts(ABC):
#     @abstractmethod
#     def analyze_and_map_fonts(self, filepath):
#         pass

class Base(WindowConfigurator, CreateTabWidget, CreateToolbar,
             CreateElem, AddLayout, CreateNewTab, ElementCreator):
    # def __init__(self):
    #     super().__init__()
    def create1(self, btn, functions):
        # Настройки окна
        self.setup_window()
        # Панель инструментов
        self.create_tab_widget()

        # Вставляем макет
        self.add_layout()

        # Создание кнопок

        self.create_elem(btn=[self.font_btn, self.open_btn, self.save_btn],
                         functions=[self.change_font, self.open_pdf, self.save_as_pdf])

        # Создаём начальную вкладку
        self.create_new_tab(title="Новая вкладка")
    def create_tab_widget(self):
        self.addToolBar(self.toolbar)

class BaseWindow(QMainWindow):#, WindowConfigurator, CreateTabWidget, CreateToolbar,
             # CreateFont,
             #CreateElem, AddLayout, CreateNewTab, ElementCreator# ChangeFont, #ChangeFontFromCombo,
             # SetActiveFont, OpenPdf, SaveAsPdf,
             #OpenSavedPdfForEdit, CloseTab, NormalizeFontName, FindMatchingFont,
             #CreateFontFromSpan, AnalyzeAndMapFonts

    def __init__(self):
        super().__init__()
        # Основной контейнер
        self.central_widget = QWidget()
        self.layout = QVBoxLayout()
        # Панель инструментов
        self.toolbar = QToolBar()
        # Вкладки с редакторами
        self.tab_widget = QTabWidget()
        # Выпадающий список шрифтов
        self.font_combo = QFontComboBox()
        self.fmt = QTextCharFormat()
        self.active_format = QTextCharFormat()
        # Создание кнопок
        self.font_btn = QPushButton("Выбрать шрифт...")
        self.open_btn = QPushButton("Открыть")
        self.save_btn = QPushButton("Сохранить как")
        # Создаём начальную вкладку
        self.text_edit = QTextEdit()
        # База шрифтов
        self.font_db = QFontDatabase()
        self.font_cache = {}  # Кэш для ускорения
        self.base = Base
        self.init_ui()
        # self.initUI()

# class PDFEditorWindow(BaseWindow):

    def init_ui(self):
        self.base.create_tab_widget(self)

    # Настройки окна
    def setup_window(self):
        self.setWindowTitle("Редактор с поддержкой PDF")
        self.setGeometry(100, 100, 1200, 800)

    # Панель инструментов
    def create_tab_widget(self):
        self.addToolBar(self.toolbar)

    # Вставляем макет
    def add_layout(self):
        self.layout.addWidget(self.tab_widget)
        self.central_widget.setLayout(self.layout)
        self.setCentralWidget(self.central_widget)

    # Выпадающий список шрифтов
    # def create_font_combo(self):
    #     self.toolbar.addSeparator()
    #     self.font_combo.currentTextChanged.connect(self.change_font_from_combo)
    #     self.toolbar.addWidget(QLabel("Шрифт: "))
    #     self.toolbar.addWidget(self.font_combo)

    # Создание кнопок
    def create_elem(self, btn, functions):
        count = 0
        for button in btn:
            button.clicked.connect(functions[count])
            count += 1
            self.toolbar.addWidget(button)

    def change_font(self):
        """Смена шрифта через диалоговое окно."""
        current_widget = self.tab_widget.currentWidget()
        if not isinstance(current_widget, QTextEdit):
            return

        current_format = current_widget.currentCharFormat()
        initial_font = current_format.font()

        font, ok = QFontDialog.getFont(initial_font, self)
        if ok:
            self.set_active_font(font)

    # def change_font_from_combo(self, font_family):
    #     """Смена шрифта из выпадающего списка."""
    #     current_widget = self.tab_widget.currentWidget()
    #     if not isinstance(current_widget, QTextEdit):
    #         return
    #
    #     cursor = current_widget.textCursor()
    #     current_font = current_widget.currentCharFormat().font()
    #     new_font = QFont(font_family, current_font.pointSize())
    #     self.set_active_font(new_font)

    def set_active_font(self, font):
        """Устанавливает активный шрифт для текущего виджета."""
        current_widget = self.tab_widget.currentWidget()
        cursor = current_widget.textCursor()

        if cursor.hasSelection():

            self.fmt.setFont(font)
            cursor.mergeCharFormat(self.fmt)


        self.active_format.setFont(font)
        current_widget.setCurrentCharFormat(self.active_format)


    def create_new_tab(self, title):

        """Создаёт новую вкладку с QTextEdit."""
        index = self.tab_widget.addTab(self.text_edit, title)
        self.tab_widget.setCurrentIndex(index)
        return self.text_edit

    def open_pdf(self):
        """Открывает PDF-файл и конвертирует в текст для редактирования."""
        filepath, _ = QFileDialog.getOpenFileName(
            self, "Открыть PDF-файл", "", "PDF files (*.pdf)"
        )
        if not filepath:
            return

        try:
            # Открываем PDF с помощью PyMuPDF
            print('1')
            tab_title = f"Редактирование: {filepath.split('/')[-1]}"
            print('2')
            font_mapping = self.analyze_and_map_fonts(filepath)
            print('3')
            text_edit = self.create_new_tab(tab_title)
            print('4')
            cursor = text_edit.textCursor()

            for page in font_mapping:

                for span in page["spans"]:
                    # Устанавливаем формат перед вставкой текста
                    cursor.setCharFormat(span["char_format"])
                    cursor.insertText(span["text"])

            text_edit.setTextCursor(cursor)
            print('5')
            default_font = QFont("Arial", 12)

            self.fmt.setFont(default_font)
            text_edit.setCurrentCharFormat(self.fmt)

            QMessageBox.information(self, "Успех", f"PDF-файл {tab_title} успешно открыт!")

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось открыть PDF-файл:\n{str(e)}")

    def save_as_pdf(self):
        """Сохраняет текущий документ в PDF-файл."""
        current_widget = self.tab_widget.currentWidget()
        if not isinstance(current_widget, QTextEdit):
            return

        filepath, _ = QFileDialog.getSaveFileName(
            self, "Сохранить как PDF", "", "PDF files (*.pdf)"
        )
        if not filepath:
            return

        try:
            document = current_widget.document()
            printer = QPrinter(QPrinter.HighResolution)
            printer.setOutputFormat(QPrinter.PdfFormat)
            printer.setOutputFileName(filepath.split('/')[-1])
            printer.setPageSize(QPrinter.A4)
            printer.setPageMargins(0.1, 0.1, 0.1, 0.1, QPrinter.Millimeter)

            document.print_(printer)

            QMessageBox.information(self, "Успех", f"Документ сохранён как PDF:\n{filepath}")

            # После сохранения открываем PDF в новой вкладке для редактирования
            self.open_saved_pdf_for_edit(filepath)

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить PDF:\n{str(e)}")

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
                # "page_number": page_num + 1,
                "spans": []
            }
            print('10')
            for block in text_info["blocks"]:
                if block["type"] == 0:  # Текстовый блок
                    for line in block["lines"]:
                        for span in line["spans"]:
                            qt_font, char_format, matched_name = self.create_qt_font_from_pdf_span(span)
                            span_data = {
                                "original_font": span["font"],
                                "matched_qt_font": matched_name,
                                "size": span["size"],
                                "text": span["text"],
                                "qt_font": qt_font,
                                "char_format": char_format  # Сохраняем формат для использования
                            }
                            page_data["spans"].append(span_data)

            results.append(page_data)
        print('11')
        doc.close()
        return results

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PDFEditorWindow()
    window.show()
    sys.exit(app.exec_())