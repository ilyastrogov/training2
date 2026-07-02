import sys
import fitz  # PyMuPDF
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QWidget,
                             QFileDialog, QPushButton, QTabWidget, QTextEdit,
                             QToolBar, QFontComboBox, QLabel, QMessageBox)
from PyQt5.QtGui import QTextCharFormat, QFont, QColor, QTextCursor, QFontDatabase
from PyQt5.QtCore import Qt
from PyQt5.QtPrintSupport import QPrinter

class PDFEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PDF Редактор с заменой шрифтов")
        self.setGeometry(100, 100, 1200, 800)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Панель инструментов
        toolbar = QToolBar("Инструменты")
        self.addToolBar(toolbar)

        open_btn = QPushButton("Открыть PDF")
        open_btn.clicked.connect(self.open_pdf)
        toolbar.addWidget(open_btn)

        save_btn = QPushButton("Сохранить как PDF (со стилями)")
        save_btn.clicked.connect(self.save_as_pdf_with_styles)
        toolbar.addWidget(save_btn)

        toolbar.addSeparator()
        toolbar.addWidget(QLabel("Шрифт для замены:"))
        self.font_combo = QFontComboBox()
        self.font_combo.setCurrentFont(QFont("Arial"))  # шрифт по умолчанию
        self.font_combo.currentFontChanged.connect(self.change_font)
        toolbar.addWidget(self.font_combo)

        apply_font_btn = QPushButton("Применить выбранный шрифт ко всему тексту")
        apply_font_btn.clicked.connect(self.apply_selected_font)
        toolbar.addWidget(apply_font_btn)

        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        main_layout.addWidget(self.tabs)

    def open_pdf(self):
        """Открывает PDF через PyMuPDF и загружает в QTextEdit"""
        filename, _ = QFileDialog.getOpenFileName(
            self, "Открыть PDF", "", "PDF Files (*.pdf)"
        )
        if filename:
            try:

                with fitz.open(filename) as doc:
                    print('1')
                    res = self.analyze_fonts_in_pdf(doc)
                    print(res)
                    for page_data in res:
                        print(f"\nСтраница {page_data['page']}:")
                        for font_group in page_data["fonts_used"]:
                            print(f"  Шрифт: {font_group['font_name']} (размер {font_group['size']}pt)")
                            chars = ''.join([c['character'] for c in font_group['characters']])
                            print(f"  Символы: {chars}")

                    page_data = doc[0].get_text("dict")  # первая страница
                    editable_widget = self.create_editable_canvas_from_dict(page_data)
                    tab_name = filename.split('/')[-1]
                    index = self.tabs.addTab(editable_widget, tab_name)
                    self.tabs.setCurrentIndex(index)


                # tab_name = filename.split('/')[-1]

                # widget = QWidget()
                # layout = QVBoxLayout(widget)
                #
                # broadway_font = QFont("Broadway")  # Размер 16 пунктов
                #
                # # Создаём метку с текстом и применяем шрифт
                # label = QLabel("Текст шрифтом BroadwayRegular")
                # label.setFont(broadway_font)
                # #
                # # layout.addWidget(label)
                # # self.setLayout(layout)
                # # self.setWindowTitle("Пример шрифта Broadway")
                # # self.show()
                #
                #
                #
                # self.text_edit = QTextEdit()
                # # self.text_edit.setFont(broadway_font)
                # self.text_edit.setPlaceholderText("Редактируемый PDF‑холст (шрифты будут заменены)")
                # layout.addWidget(label)
                #
                # html_content = ''
                # with fitz.open(filename) as doc:
                #     html_content = ''.join(page.get_text("html") for page in doc)
                #
                # print('1', html_content)
                # # self.text_edit = QTextEdit()
                # # self.text_edit.setReadOnly(False)
                # print('3', self.text_edit)
                # self.text_edit.setHtml(html_content)
                # self.text_edit.setFont(broadway_font)
                # index = self.tabs.addTab(self.text_edit, tab_name)
                # print('index', index)
                # self.tabs.setCurrentIndex(index)
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось открыть PDF: {e}")

    def change_font(self, font):

        cursor = self.text_edit.textCursor()
        if cursor.hasSelection():
            fmt = QTextCharFormat()
            fmt.setFont(font)
            cursor.mergeCharFormat(fmt)
        else:
            self.text_edit.setCurrentFont(font)

    def create_editable_canvas_from_dict(self, page_data):
        """Создаёт редактируемый холст из данных PDF"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText("Редактируемый PDF‑холст (шрифты будут заменены)")
        layout.addWidget(self.text_edit)

        self.apply_dict_styles_to_text_edit(self.text_edit, page_data)
        widget.text_edit = self.text_edit
        return widget

    def apply_dict_styles_to_text_edit(self, text_edit, page_data):
        """Применяет стили из PDF к QTextEdit (без шрифтов — они будут заменены)"""
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

                        # Берём размер, цвет и стили из PDF, но шрифт заменяем
                        font_size = int(span.get("size", 12))
                        color_hex = span.get("color", 0)
                        flags = span.get("flags", 0)

                        fmt = QTextCharFormat()
                        # Шрифт будет заменён позже — пока ставим заполнитель

                        f = QFont("BrushScript")
                        fmt.setFont(f)
                        fmt.setFontPointSize(font_size)

                        # Обработка цвета
                        if isinstance(color_hex, int) and color_hex != 0:
                            r = (color_hex >> 16) & 0xFF
                            g = (color_hex >> 8) & 0xFF
                            b = color_hex & 0xFF
                            fmt.setForeground(QColor(r, g, b))

                        # Обработка стилей (жирный, курсив, подчёркивание)
                        if flags & 2:  # жирный
                            fmt.setFontWeight(QFont.Bold)
                        if flags & 1:  # курсив
                            fmt.setFontItalic(True)
                        if flags & 4:  # подчёркивание
                            fmt.setFontUnderline(True)

                        cursor.insertText(text, fmt)
                    cursor.insertBlock()  # перенос строки

    def analyze_fonts_in_pdf(self, doc):
        # doc = fitz.open(filepath)
        results = []

        for page_num in range(doc.page_count):

            page = doc.load_page(page_num)

            # Извлекаем текст с полной информацией о символах
            text_info = page.get_text("dict")

            page_fonts = []
            for block in text_info["blocks"]:

                if block["type"] == 0:  # Текстовый блок
                    for line in block["lines"]:
                        for span in line["spans"]:
                        # Информация о шрифте для всего span'а
                            font_info = {
                                "font_name": span["font"],
                                "size": span["size"],
                                "color": span["color"],
                                "characters": []
                            }

                            # Разбираем каждый символ в span'е
                            for i, char in enumerate(span["text"]):
                                print('7', i, char)
                                char_info = {
                                    "character": char,
                                    "position": i,
                                    "x0": span["bbox"][0], # + span["widths"][i] * i,
                                    "y0": span["bbox"][1],
                                    # "width": span["widths"][i]
                                }
                                print('8')
                                font_info["characters"].append(char_info)
                                print('9')
                                page_fonts.append(font_info)
                                print('10')
                            results.append({
                                "page": page_num + 1,
                                "fonts_used": page_fonts
                            })

        # doc.close()
        return results

    def apply_selected_font(self):
        """Применяет выбранный в QFontComboBox шрифт ко всему тексту в текущей вкладке"""
        current_tab = self.tabs.currentWidget()
        if current_tab and hasattr(current_tab, 'text_edit'):
            text_edit = current_tab.text_edit
            selected_font = self.font_combo.currentFont()

            # Применяем шрифт ко всему документу
            cursor = text_edit.textCursor()
            cursor.select(QTextCursor.Document)  # выделяем весь текст

            fmt = QTextCharFormat()
            fmt.setFont(selected_font)
            cursor.mergeCharFormat(fmt)  # применяем формат

            QMessageBox.information(self, "Успех", "Шрифт успешно применён ко всему тексту!")
        else:
            QMessageBox.warning(self, "Внимание", "Нет активной вкладки для применения шрифта")

    def close_tab(self, index):
        self.tabs.removeTab(index)
    def save_as_pdf_with_styles(self):
        """Сохраняет текущий редактируемый текст в PDF через QPrinter с сохранением стилей"""
        current_tab = self.tabs.currentWidget()
        if current_tab and hasattr(current_tab, 'text_edit'):
            text_edit = current_tab.text_edit

            filename, _ = QFileDialog.getSaveFileName(
                self, "Сохранить как PDF", "", "PDF Files (*.pdf)"
            )
            if filename:
                try:
                    printer = QPrinter(QPrinter.HighResolution)
                    printer.setOutputFormat(QPrinter.PdfFormat)
                    printer.setOutputFileName(filename)
                    printer.setPageSize(QPrinter.A4)
                    printer.setPageMargins(0.1, 0.1, 0.1, 0.1, QPrinter.Millimeter)

                    text_edit.document().print_(printer)
                    QMessageBox.information(self, "Успех", f"Файл сохранён: {filename}")
                except Exception as e:
                    QMessageBox.critical(self, "Ошибка сохранения", f"Не удалось сохранить PDF: {e}")
                else:
                    QMessageBox.warning(self, "Внимание", "Нет активной вкладки для сохранения")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    viewer = PDFEditor()
    viewer.show()
    sys.exit(app.exec_())


# import sys
# import fitz  # PyMuPDF
# from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QWidget,
#                              QFileDialog, QPushButton, QTabWidget, QTextEdit,
#                              QToolBar, QMessageBox, QLabel)
# from PyQt5.QtGui import QTextCharFormat, QFont, QColor, QFontDatabase, QTextCursor
# from PyQt5.QtPrintSupport import QPrinter
# from PyQt5.QtCore import Qt
#
# class PDFEditor(QMainWindow):
#     def __init__(self):
#         super().__init__()
#         self.setWindowTitle("PDF Редактор с сохранением стилей")
#         self.setGeometry(100, 100, 1200, 800)
#
#         central_widget = QWidget()
#         self.setCentralWidget(central_widget)
#         main_layout = QVBoxLayout(central_widget)
#
#         # Панель инструментов
#         toolbar = QToolBar("Инструменты")
#         self.addToolBar(toolbar)
#
#         open_btn = QPushButton("Открыть PDF")
#         open_btn.clicked.connect(self.open_pdf)
#         toolbar.addWidget(open_btn)
#
#         save_btn = QPushButton("Сохранить как PDF (со стилями)")
#         save_btn.clicked.connect(self.save_as_pdf_with_styles)
#         toolbar.addWidget(save_btn)
#
#         self.tabs = QTabWidget()
#         self.tabs.setTabsClosable(True)
#         self.tabs.tabCloseRequested.connect(self.close_tab)
#         main_layout.addWidget(self.tabs)
#
#     def open_pdf(self):
#         """Открывает PDF через PyMuPDF и загружает в QTextEdit с точной передачей шрифтов"""
#         filename, _ = QFileDialog.getOpenFileName(
#             self, "Открыть PDF", "", "PDF Files (*.pdf)"
#         )
#         if filename:
#             try:
#                 with fitz.open(filename) as doc:
#                     page_data = doc[0].get_text("dict")  # первая страница
#                     editable_widget = self.create_editable_canvas_from_dict(page_data)
#                 tab_name = filename.split('/')[-1]
#                 index = self.tabs.addTab(editable_widget, tab_name)
#                 self.tabs.setCurrentIndex(index)
#             except Exception as e:
#                 QMessageBox.critical(self, "Ошибка", f"Не удалось открыть PDF: {e}")
#
#     def create_editable_canvas_from_dict(self, page_data):
#         """Создаёт редактируемый холст из данных PDF с точной передачей шрифтов"""
#         widget = QWidget()
#         layout = QVBoxLayout(widget)
#
#         text_edit = QTextEdit()
#         text_edit.setPlaceholderText("Редактируемый PDF‑холст (шрифты из PDF)")
#         layout.addWidget(text_edit)
#
#         self.apply_dict_styles_to_text_edit(text_edit, page_data)
#         widget.text_edit = text_edit
#         return widget
#
#     def apply_dict_styles_to_text_edit(self, text_edit, page_data):
#         """Применяет стили из PDF к QTextEdit с улучшенной обработкой шрифтов"""
#         cursor = text_edit.textCursor()
#         cursor.select(QTextCursor.Document)
#         cursor.removeSelectedText()
#
#         for block in page_data["blocks"]:
#             if block["type"] == 0:  # текстовый блок
#                 for line in block["lines"]:
#                     for span in line["spans"]:
#                         text = span["text"]
#                         if not text or text.isspace():
#                             continue
#
#                         # Получаем данные из PDF
#                         font_name_raw = span.get("font", "Arial")
#                         font_size = int(span.get("size", 12))
#                         color_hex = span.get("color", 0)
#                         flags = span.get("flags", 0)
#
#                         # Нормализуем название шрифта для Qt
#                         font_family = self.normalize_font_name(font_name_raw)
#
#                         # Создаём формат
#                         fmt = QTextCharFormat()
#                         fmt.setFontFamily(font_family)
#                         fmt.setFontPointSize(font_size)
#
#                         # Обработка цвета
#                         if isinstance(color_hex, int) and color_hex != 0:
#                             r = (color_hex >> 16) & 0xFF
#                             g = (color_hex >> 8) & 0xFF
#                             b = color_hex & 0xFF
#                             fmt.setForeground(QColor(r, g, b))
#
#                         # Обработка стилей
#                         if flags & 2:  # жирный
#                             fmt.setFontWeight(QFont.Bold)
#                         if flags & 1:  # курсив
#                             fmt.setFontItalic(True)
#                         if flags & 4:  # подчёркивание
#                             fmt.setFontUnderline(True)
#
#                         # Вставляем текст с форматом
#                         cursor.insertText(text, fmt)
#
#                     # Перенос строки после каждого span
#                     cursor.insertBlock()
#
#     def normalize_font_name(self, font_name):
#         """Нормализует название шрифта для Qt с улучшенной обработкой"""
#         # Убираем постфиксы типа "-Bold", "-Italic", "-Regular"
#         font_name = font_name.split('-')[0]
#         # Удаляем суффиксы типа "MT", "PSMT"
#         font_name = font_name.replace("MT", "").replace("PSMT", "")
#
#         font_map = {
#             "TimesNewRoman": "Times New Roman",
#             "TimesNew": "Times New Roman",
#             "Helvetica": "Helvetica",
#             "Arial": "Arial",
#             "Courier": "Courier",
#             "Calibri": "Calibri",
#             "Georgia": "Georgia",
#             "Verdana": "Verdana",
#             "Tahoma": "Tahoma",
#             "Trebuchet": "Trebuchet MS",
#             "Garamond": "Garamond",
#             "Bookman": "Bookman Old Style",
#             "Palatino": "Palatino Linotype",
#         }
#
#         normalized = font_map.get(font_name, font_name)
#
#         # Проверяем, что шрифт реально существует в системе
#         available_fonts = QFontDatabase().families()
#         if normalized not in available_fonts:
#             # Если не найден, ищем частичное совпадение
#             for available in available_fonts:
#                 if normalized.lower() in available.lower():
#                     print(f"Шрифт '{normalized}' не найден. Используем аналог: '{available}'")
#                 return available
#
#         print(f"Используем шрифт: {normalized}")
#         return normalized
#
#     def save_as_pdf_with_styles(self):
#         """Сохраняет текущий редактируемый текст в PDF через QPrinter с сохранением стилей"""
#         current_tab = self.tabs.currentWidget()
#         if current_tab and hasattr(current_tab, 'text_edit'):
#             text_edit = current_tab.text_edit
#
#             filename, _ = QFileDialog.getSaveFileName(
#                 self, "Сохранить как PDF", "", "PDF Files (*.pdf)"
#             )
#             if filename:
#                 try:
#                     printer = QPrinter(QPrinter.HighResolution)
#                     printer.setOutputFormat(QPrinter.PdfFormat)
#                     printer.setOutputFileName(filename)
#                     printer.setPageSize(QPrinter.A4)
#                     printer.setPageMargins(0.1, 0.1, 0.1, 0.1, QPrinter.Millimeter)
#
#                     text_edit.document().print_(printer)
#                     QMessageBox.information(self, "Успех", f"Файл сохранён: {filename}")
#                 except Exception as e:
#                     QMessageBox.critical(self, "Ошибка сохранения", f"Не удалось сохранить PDF: {e}")
#                 else:
#                     QMessageBox.warning(self, "Внимание", "Нет активной вкладки для сохранения")
#
#     def close_tab(self, index):
#         self.tabs.removeTab(index)
#
# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     viewer = PDFEditor()
#     viewer.show()
#     sys.exit(app.exec_())


