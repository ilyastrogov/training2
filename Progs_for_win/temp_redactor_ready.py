import sys
import fitz  # PyMuPDF
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QWidget,
                             QFileDialog, QPushButton, QTabWidget, QTextEdit,
                             QComboBox, QToolBar, QLabel, QScrollArea)
from PyQt5.QtGui import QTextCharFormat, QFont, QColor, QTextCursor
from PyQt5.QtCore import Qt


class PDFDictToEditableCanvas(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PDF → dict → Редактируемый холст")
        self.setGeometry(100, 100, 1200, 800)

        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Панель инструментов
        toolbar = QToolBar("Инструменты")
        self.addToolBar(toolbar)

        open_btn = QPushButton("Открыть PDF в новой вкладке")
        open_btn.clicked.connect(self.open_pdf_in_new_tab)
        toolbar.addWidget(open_btn)

        # Виджет вкладок
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        layout.addWidget(self.tabs)

    def open_pdf_in_new_tab(self):
        """Открывает PDF в новой вкладке с извлечением через dict"""
        filename, _ = QFileDialog.getOpenFileName(
            self, "Открыть PDF", "", "PDF Files (*.pdf)"
        )
        if filename:
            try:
                # Загружаем PDF документ
                doc = fitz.open(filename)
                # Извлекаем данные в формате dict (первая страница)
                page_data = doc[0].get_text("dict")
                # Создаём редактируемый холст
                editable_widget = self.create_editable_canvas_from_dict(page_data)
                # Добавляем вкладку
                tab_name = filename.split('/')[-1]
                index = self.tabs.addTab(editable_widget, tab_name)
                self.tabs.setCurrentIndex(index)
            except Exception as e:
                print(f"Ошибка открытия PDF: {e}")

    def create_editable_canvas_from_dict(self, page_data):
        """Создаёт редактируемый холст из данных dict"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Редактируемый текстовый холст
        text_edit = QTextEdit()
        text_edit.setPlaceholderText("Редактируемый PDF‑холст с сохранением стилей...")
        layout.addWidget(text_edit)

        # Применяем стили из dict к тексту
        self.apply_dict_styles_to_text_edit(text_edit, page_data)

        # Сохраняем ссылку на текстовый редактор
        widget.text_edit = text_edit
        return widget

    def apply_dict_styles_to_text_edit(self, text_edit, page_data):
        """Применяет стили из dict формата к QTextEdit"""
        cursor = text_edit.textCursor()
        cursor.select(QTextCursor.Document)
        cursor.removeSelectedText()
        cursor.movePosition(QTextCursor.End)

        # Обрабатываем блоки текста
        for block in page_data["blocks"]:
            if block["type"] == 0:  # текстовый блок
                for line in block["lines"]:
                    for span in line["spans"]:
                        text = span["text"].strip()
                        if not text:  # пропускаем пустые строки
                            continue

                        font = span["font"]
                        size = int(span["size"])
                        color = span.get("color", 0)  # цвет в HEX или RGB

                        # Создаём формат для текста
                        fmt = QTextCharFormat()
                        fmt.setFontFamily(font)
                        fmt.setFontPointSize(size)

                        # Обработка цвета (конвертируем из HEX/RGB)
                        if isinstance(color, int):
                            # Конвертируем HEX в QColor
                            qcolor = QColor(
                                (color >> 16) & 0xFF,  # красный
                                (color >> 8) & 0xFF,   # зелёный
                                color & 0xFF             # синий
                            )
                            fmt.setForeground(qcolor)

                            # Обработка флагов стилей
                            flags = span.get("flags", 0)
                            if flags & 2:  # жирный (bold)
                                fmt.setFontWeight(QFont.Bold)
                            if flags & 1:  # курсив (italic)
                                fmt.setFontItalic(True)
                            if flags & 4:  # подчёркивание
                                fmt.setFontUnderline(True)

                        # Вставляем текст со стилем
                            cursor.insertText(text, fmt)

        # Добавляем перенос строки после каждой строки в блоке
        cursor.insertBlock()

    # Добавляем дополнительный перенос между блоками
        cursor.insertBlock()
        cursor.insertBlock()


    def close_tab(self, index):
        """Закрывает вкладку"""
        self.tabs.removeTab(index)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    viewer = PDFDictToEditableCanvas()
    viewer.show()
    sys.exit(app.exec_())
