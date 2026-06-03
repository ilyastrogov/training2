import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QWidget,
                             QFileDialog, QPushButton, QTabWidget, QTextEdit,
                             QComboBox, QSpinBox, QToolBar, QAction, QFontComboBox,
                             QSplitter, QLabel)
from PyQt5.QtGui import QFont, QTextCharFormat
from PyQt5.QtPrintSupport import QPrinter
from PyQt5.QtCore import Qt
# import PyPDF2
import fitz

class MultiCanvasEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Редактор с текстовым и PDF холстами")
        self.setGeometry(100, 100, 1200, 800)

        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Разделитель для двух холстов
        splitter = QSplitter(Qt.Horizontal)

        # Текстовый холст
        self.text_canvas = QTextEdit()
        self.text_canvas.setPlaceholderText("Введите текст здесь...")
        splitter.addWidget(self.text_canvas)

        # PDF холст (только для отображения)
        self.pdf_canvas = QLabel("PDF холст — здесь будет отображаться PDF")
        self.pdf_canvas.setAlignment(Qt.AlignCenter)
        self.pdf_canvas.setStyleSheet("background-color: #f0f0f0; border: 1px solid #ccc;")
        splitter.addWidget(self.pdf_canvas)

        splitter.setSizes([600, 600])
        main_layout.addWidget(splitter)

        # Панель инструментов
        self.toolbar = QToolBar("Форматирование")
        self.addToolBar(Qt.TopToolBarArea, self.toolbar)

        # Выбор шрифта
        self.font_combo = QFontComboBox()
        self.font_combo.currentFontChanged.connect(self.change_font)
        self.toolbar.addWidget(self.font_combo)

        # Размер шрифта
        self.size_spin = QSpinBox()
        self.size_spin.setRange(8, 72)
        self.size_spin.setValue(12)
        self.size_spin.valueChanged.connect(self.change_font_size)
        self.toolbar.addWidget(self.size_spin)

        # Кнопка жирного шрифта
        bold_action = QAction("Жирный", self)
        bold_action.setCheckable(True)
        bold_action.toggled.connect(self.toggle_bold)
        self.toolbar.addAction(bold_action)

        # Кнопка курсива
        italic_action = QAction("Курсив", self)
        italic_action.setCheckable(True)
        italic_action.toggled.connect(self.toggle_italic)
        self.toolbar.addAction(italic_action)

        # Кнопка подчёркивания
        underline_action = QAction("Подчёркнутый", self)
        underline_action.setCheckable(True)
        underline_action.toggled.connect(self.toggle_underline)
        self.toolbar.addAction(underline_action)


        # Кнопки управления
        btn_layout = QVBoxLayout()

        open_pdf_btn = QPushButton("Открыть PDF для просмотра")
        open_pdf_btn.clicked.connect(self.open_pdf)
        btn_layout.addWidget(open_pdf_btn)

        save_pdf_btn = QPushButton("Сохранить текст как PDF")
        save_pdf_btn.clicked.connect(self.save_as_pdf)
        btn_layout.addWidget(save_pdf_btn)

        clear_btn = QPushButton("Очистить холсты")
        clear_btn.clicked.connect(self.clear_canvases)
        btn_layout.addWidget(clear_btn)

        main_layout.addLayout(btn_layout)


    def open_pdf(self):
        """Открывает PDF для просмотра в PDF холсте"""
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Открыть текстовый файл",
            "",
            "Текстовые файлы (*.txt);;Все файлы (*)"
        )
        tab_name = filename.split('/')[-1]
        text = ExtractText().extraction(tab_name)
        print(tab_name)
        print(text)
        # self.pdf_canvas = QTextEdit()
        # self.pdf_canvas.setPlainText(text)
        # self.pdf_canvas.setReadOnly(False)  # Только для чтения
        # self.addNewTab(filename)
        # index = self.pdf_canvas.addNewTab(self.text_edit, tab_name)
        # self.pdf_canvas.setCurrentIndex(index)
        # self.statusBar.showMessage(f"Файл открыт: {filename}", 3000)
        # filename, _ = QFileDialog.getOpenFileName(
        #     self, "Открыть PDF‑файл", "", "PDF Files (*.pdf)"
        # )
        # if filename:
        #     try:
        #         with open(filename, 'rb') as file:
        #             reader = PyPDF2.PdfReader(file)
        #             text = ""
        #             for page_num in range(len(reader.pages)):
        #                 page = reader.pages[page_num]
        #                 text += f"\n--- Страница {page_num + 1} ---\n"
        #                 text += page.extract_text() or ""
        #     # Отображаем текст в PDF холсте (в реальном приложении здесь было бы изображение страницы PDF)
        self.pdf_canvas.setText(f"Содержимое PDF:\n{text[:500]}...")  # показываем первые 500 символов
        #         self.setWindowTitle(f"Редактор — {filename.split('/')[-1]}")
        #     except Exception as e:
        #         print(f"Ошибка открытия PDF: {e}")

    def save_as_pdf(self):
        """Сохраняет текст из текстового холста как PDF"""
        text = self.text_canvas.toPlainText()
        if not text:
            print("Нет текста для сохранения")
            return

        save_filename, _ = QFileDialog.getSaveFileName(
            self, "Сохранить как PDF", "document.pdf", "PDF Files (*.pdf)"
        )
        if save_filename:
            printer = QPrinter(QPrinter.HighResolution)
            printer.setOutputFormat(QPrinter.PdfFormat)
            printer.setOutputFileName(save_filename)
            printer.setPageSize(QPrinter.A4)

            # Печатаем содержимое текстового холста в PDF
            self.text_canvas.document().print_(printer)

    def clear_canvases(self):
        """Очищает оба холста"""
        self.text_canvas.clear()
        self.pdf_canvas.setText("PDF холст — здесь будет отображаться PDF")

    # Методы форматирования для текстового холста
    def change_font(self, font):
        cursor = self.text_canvas.textCursor()
        if cursor.hasSelection():
            fmt = QTextCharFormat()
            fmt.setFont(font)
            cursor.mergeCharFormat(fmt)
        else:
            self.text_canvas.setCurrentFont(font)

    def change_font_size(self, size):
        cursor = self.text_canvas.textCursor()
        if cursor.hasSelection():
            fmt = QTextCharFormat()
            fmt.setFontPointSize(size)
            cursor.mergeCharFormat(fmt)
        else:
            font = self.text_canvas.currentFont()
            font.setPointSize(size)
            self.text_canvas.setCurrentFont(font)

    def toggle_bold(self, checked):
        fmt = QTextCharFormat()
        fmt.setFontWeight(QFont.Bold if checked else QFont.Normal)
        self.text_canvas.mergeCurrentCharFormat(fmt)

    def toggle_italic(self, checked):
        fmt = QTextCharFormat()
        fmt.setFontItalic(checked)
        self.text_canvas.mergeCurrentCharFormat(fmt)


    def toggle_underline(self, checked):
        fmt = QTextCharFormat()
        fmt.setUnderlineStyle(QTextCharFormat.SingleUnderline if checked else QTextCharFormat.NoUnderline)
        self.text_canvas.mergeCurrentCharFormat(fmt)


class ExtractText:
    """ Класс для извлечения текста из PDF файла"""
    def extraction(self, input_filename: str) -> str:
        text = ''
        with fitz.open(input_filename) as doc:
            for page in doc:
                page_text = page.get_text()
                text += page_text
        return text

if __name__ == "__main__":
    app = QApplication(sys.argv)
    editor = MultiCanvasEditor()
    editor.show()
    sys.exit(app.exec_())