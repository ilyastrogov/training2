from PyQt5.QtWidgets import (QApplication, QMainWindow, QTabWidget, QTextEdit,
                             QPushButton, QVBoxLayout, QWidget, QFontDialog, QFileDialog,
                             QComboBox, QToolBar, QMessageBox, QLabel, QFontComboBox)
from PyQt5.QtGui import QTextCharFormat, QFont, QTextDocument, QPdfWriter, QPainter, QFontDatabase
from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtPrintSupport import QPrinter
import sys
import fitz  # PyMuPDF для работы с PDF
import re

class PDFTextEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Редактор с поддержкой PDF")
        self.setGeometry(100, 100, 1200, 800)

        # Основной контейнер
        central_widget = QWidget()
        layout = QVBoxLayout()

        # Панель инструментов
        self.toolbar = QToolBar()
        self.addToolBar(self.toolbar)

        # Выпадающий список шрифтов
        self.toolbar.addSeparator()
        self.font_combo = QFontComboBox()
        # self.font_combo.addItems([
        #     "Arial", "Times New Roman", "Courier New",
        #     "Verdana", "Georgia", "Calibri"
        # ])
        self.font_combo.currentTextChanged.connect(self.change_font_from_combo)
        self.toolbar.addWidget(QLabel("Шрифт: "))
        self.toolbar.addWidget(self.font_combo)

        # Кнопка выбора шрифта
        font_btn = QPushButton("Выбрать шрифт...")
        font_btn.clicked.connect(self.change_font)
        self.toolbar.addWidget(font_btn)

        # Кнопка открытия PDF
        open_pdf_btn = QPushButton("Открыть PDF")
        open_pdf_btn.clicked.connect(self.open_pdf)
        self.toolbar.addWidget(open_pdf_btn)

        # Кнопка сохранения в PDF
        save_pdf_btn = QPushButton("Сохранить как PDF")
        save_pdf_btn.clicked.connect(self.save_as_pdf)
        self.toolbar.addWidget(save_pdf_btn)

        # Вкладки с редакторами
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.tabCloseRequested.connect(self.close_tab)

        layout.addWidget(self.tab_widget)
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        # Создаём начальную вкладку
        self.create_new_tab("Новая вкладка")

    def create_new_tab(self, title):
        """Создаёт новую вкладку с QTextEdit."""
        text_edit = QTextEdit()
        index = self.tab_widget.addTab(text_edit, title)
        self.tab_widget.setCurrentIndex(index)
        return text_edit

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

    def change_font_from_combo(self, font_family):
        """Смена шрифта из выпадающего списка."""
        current_widget = self.tab_widget.currentWidget()
        if not isinstance(current_widget, QTextEdit):
            return

        cursor = current_widget.textCursor()
        current_font = current_widget.currentCharFormat().font()
        new_font = QFont(font_family, current_font.pointSize())
        self.set_active_font(new_font)

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
            font_mapping = PDFFontMapper().analyze_and_map_fonts(filepath)
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
            # pdf_document = fitz.open(filepath)
            # text_content = ""
            #
            # # Извлекаем текст со всех страниц
            # for page_num in range(len(pdf_document)):
            #     page = pdf_document.load_page(page_num)
            #     text_content += page.get_text() + "\n\n"
            #
            # pdf_document.close()
            #
            # # Создаём новую вкладку с текстом из PDF
            # tab_title = filepath.split('/')[-1]
            # text_edit = self.create_new_tab(tab_title)
            # text_edit.setText(text_content)

            # Устанавливаем шрифт по умолчанию
            default_font = QFont("Arial", 12)
            fmt = QTextCharFormat()
            fmt.setFont(default_font)
            text_edit.setCurrentCharFormat(fmt)

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
            # Получаем документ для печати
            document = current_widget.document()

            # # Создаём PDF-писатель
            # pdf_writer = QPdfWriter(filepath)
            # pdf_writer.setPageSize(QPdfWriter.A4)
            # pdf_writer.setResolution(300)  # DPI
            #
            # painter = QPainter()
            # painter.begin(pdf_writer)
            #
            # # Настраиваем область печати
            # page_rect = pdf_writer.pageLayout().fullRect()
            # painter.setViewport(page_rect.toRect())
            # painter.setWindow(page_rect.toRect())
            #
            # # Печатаем документ
            # document.drawContents(painter)
            # painter.end()

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

    def open_saved_pdf_for_edit(self, filepath):
        """Открывает сохранённый PDF для редактирования в новой вкладке."""
        try:
            tab_title = f"Редактирование: {filepath.split('/')[-1]}"
            font_mapping = PDFFontMapper().analyze_and_map_fonts(filepath)
            text_edit = self.create_new_tab(tab_title)
            cursor = text_edit.textCursor()

            for page in font_mapping:


                for span in page["spans"]:
                    # Устанавливаем формат перед вставкой текста
                    cursor.setCharFormat(span["char_format"])
                    cursor.insertText(span["text"])
            print('1')
            text_edit.setTextCursor(cursor)
            print('2')
            # pdf_document = fitz.open(filepath)
            # text_content = ""
            #
            # for page_num in range(len(pdf_document)):
            #     page = pdf_document.load_page(page_num)
            #     text_content += page.get_text() + "\n\n"
            #
            # pdf_document.close()

            # Создаём новую вкладку с текстом из сохранённого PDF
            # tab_title = f"Редактирование: {filepath.split('/')[-1]}"
            # text_edit = self.create_new_tab(tab_title)
            # text_edit.setText(text_content)

            # Устанавливаем тот же шрифт, что был в оригинале
            current_widget = self.tab_widget.currentWidget()

            if isinstance(current_widget, QTextEdit):
                current_font = current_widget.currentCharFormat().font()
                fmt = QTextCharFormat()
                fmt.setFont(current_font)
                text_edit.setCurrentCharFormat(fmt)

            QMessageBox.information(
                self,
                "Успех",
                f"Сохранённый PDF открыт для редактирования:\n{tab_title}"
            )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Ошибка",
                f"Не удалось открыть сохранённый PDF для редактирования:\n{str(e)}"
            )

    def close_tab(self, index):
        """Закрывает вкладку по индексу."""
        if self.tab_widget.count() > 1:
            self.tab_widget.removeTab(index)
        else:
            QMessageBox.warning(self, "Предупреждение", "Нельзя закрыть последнюю вкладку!")

    def save_with_format(self):
        """Сохраняет текущий документ с сохранением форматирования (HTML)."""
        current_widget = self.tab_widget.currentWidget()
        if not isinstance(current_widget, QTextEdit):
            return

        filepath, _ = QFileDialog.getSaveFileName(
            self, "Сохранить файл", "", "HTML files (*.html);;All files (*.*)"
        )
        if not filepath:
            return

        # Сохраняем текущий формат курсора
        try:
            current_format = current_widget.currentCharFormat()
            if current_format is None:
                current_format = QTextCharFormat()
        except Exception as e:
            print(f"Ошибка получения формата: {e}")
            current_format = QTextCharFormat()

        # Сохраняем HTML
        try:
            html_content = current_widget.toHtml()
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(html_content)

            # Обновляем заголовок вкладки
            tab_title = filepath.split('/')[-1]
            self.tab_widget.setTabText(self.tab_widget.currentIndex(), tab_title)

            # Восстанавливаем формат
            self.safe_set_current_char_format(current_widget, current_format)

            QMessageBox.information(self, "Успех", "Файл успешно сохранён!")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить файл:\n{str(e)}")

    def safe_set_current_char_format(self, widget, format_to_set):
        """Безопасно устанавливает текущий формат символа."""
        if not isinstance(widget, QTextEdit):
            return False

        if not isinstance(format_to_set, QTextCharFormat):
            if isinstance(format_to_set, QFont):
                temp_format = QTextCharFormat()
                temp_format.setFont(format_to_set)
                format_to_set = temp_format
            else:
                format_to_set = QTextCharFormat()

        try:
            widget.setCurrentCharFormat(format_to_set)
            return True
        except Exception as e:
            print(f"Ошибка установки формата: {e}")
            return False

    def is_valid_text_edit(self, widget):
        """Проверяет валидность виджета QTextEdit."""
        return (isinstance(widget, QTextEdit) and
                widget is not None and
                widget.isVisible() and
                widget.document() is not None)

# Запуск приложения

class PDFFontMapper:
    def __init__(self):
        self.font_db = QFontDatabase()
        self.font_cache = {}  # Кэш для ускорения

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
        mapper = PDFFontMapper()
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
                            qt_font, char_format, matched_name = mapper.create_qt_font_from_pdf_span(span)
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
    window = PDFTextEditor()
    window.show()
    sys.exit(app.exec_())
