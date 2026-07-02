import sys
import fitz  # PyMuPDF
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QWidget,
                             QFileDialog, QPushButton, QTabWidget, QTextEdit,
                             QToolBar)
from PyQt5.QtGui import QTextCharFormat, QFont, QColor, QTextCursor
from PyQt5.QtCore import Qt


class PDFDictToEditableCanvas(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PDF → dict → Редактируемый холст (со стилями)")
        self.setGeometry(100, 100, 1200, 800)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        toolbar = QToolBar("Инструменты")
        self.addToolBar(toolbar)

        open_btn = QPushButton("Открыть PDF в новой вкладке")
        open_btn.clicked.connect(self.open_pdf_in_new_tab)
        toolbar.addWidget(open_btn)

        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        layout.addWidget(self.tabs)

    def open_pdf_in_new_tab(self):
        filename, _ = QFileDialog.getOpenFileName(
            self, "Открыть PDF", "", "PDF Files (*.pdf)"
        )
        if filename:
            try:
                doc = fitz.open(filename)
                page_data = doc[0].get_text("dict")
                editable_widget = self.create_editable_canvas_from_dict(page_data)
                tab_name = filename.split('/')[-1]
                index = self.tabs.addTab(editable_widget, tab_name)
                self.tabs.setCurrentIndex(index)
            except Exception as e:
                print(f"Ошибка открытия PDF: {e}")

    def create_editable_canvas_from_dict(self, page_data):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        text_edit = QTextEdit()
        text_edit.setPlaceholderText("Редактируемый PDF‑холст с сохранением стилей...")
        layout.addWidget(text_edit)

        self.apply_dict_styles_to_text_edit(text_edit, page_data)
        widget.text_edit = text_edit
        return widget

    def apply_dict_styles_to_text_edit(self, text_edit, page_data):
        cursor = text_edit.textCursor()
        cursor.select(QTextCursor.Document)
        cursor.removeSelectedText()

        for block in page_data["blocks"]:
            if block["type"] == 0:  # текстовый блок
                for line in block["lines"]:
                    for span in line["spans"]:
                        text = span["text"]
                        if not text or text.isspace():
                            continue

                        font_name = span.get("font", "Arial")
                        font_size = int(span.get("size", 12))
                        color_hex = span.get("color", 0)
                        flags = span.get("flags", 0)

                        # Нормализация названия шрифта
                        font_name1 = self.normalize_font_name(font_name)
                        print(font_name1)

                        # Создаём новый формат для каждого фрагмента
                        fmt = QTextCharFormat()
                        fmt.setFontFamily(font_name1)
                        fmt.setFontPointSize(font_size)

                        # Обработка цвета
                        if isinstance(color_hex, int) and color_hex != 0:
                            # Конвертируем HEX в RGB
                            r = (color_hex >> 16) & 0xFF
                            g = (color_hex >> 8) & 0xFF
                            b = color_hex & 0xFF
                            fmt.setForeground(QColor(r, g, b))

                        # Обработка стилей через флаги
                        if flags & 2:  # жирный
                            fmt.setFontWeight(QFont.Bold)
                        if flags & 1:  # курсив
                            fmt.setFontItalic(True)
                        if flags & 4:  # подчёркивание
                            fmt.setFontUnderline(True)

                # Вставляем текст с применением формата
                        cursor.insertText(text, fmt)

    # После каждой строки — перенос
                    cursor.insertBlock()

    # После блока — дополнительный перенос
            cursor.insertBlock()
            cursor.insertBlock()

    def normalize_font_name(self, font_name):
        """Нормализует название шрифта для Qt"""
        # Убираем постфиксы типа "-Bold", "-Italic"
        font_name = font_name.split('-')[0]
        # Заменяем распространённые названия
        font_map = {
            "TimesNewRomanPSMT": "Times New Roman",
            "Helvetica": "Helvetica",
            "ArialMT": "Arial",
            "CourierStd": "Courier",
        }
        return font_map.get(font_name, font_name)
    def close_tab(self, index):
        self.tabs.removeTab(index)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    viewer = PDFDictToEditableCanvas()
    viewer.show()
    sys.exit(app.exec_())
