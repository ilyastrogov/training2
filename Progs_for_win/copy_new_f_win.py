import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QTextEdit, QScrollArea,
                             QToolBar, QAction, QFontComboBox, QComboBox, QFileDialog, QSpinBox,
                             QMessageBox, QStatusBar, QTabWidget, QWidget, QLabel, QLineEdit, QPlainTextEdit)
from PyQt5.QtGui import QFont, QPixmap, QTextCharFormat, QColor
from PyQt5.QtCore import Qt, QUrl

from PyQt5.QtWebEngineWidgets import QWebEngineView

from urllib.request import pathname2url

from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.styles import ParagraphStyle

import os
import fitz

from pathlib import Path
import platform

from PyQt5.QtPrintSupport import QPrinter
from PyQt5.QtWidgets import QFileDialog


# import
# from file_date import WritingText, CreateFile
class TextTab(QWidget):
    """Виджет вкладки с текстовым редактором и информацией о файле"""

    def __init__(self, filepath=None):
        super().__init__()
        self.filepath = filepath
        self.initUI()
        # self.web_view = QWebEngineView()
        # self.setCentralWidget(self.web_view)

    def initUI(self):
        layout = QVBoxLayout()

        # Текстовый редактор для вкладки
        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText("Начните вводить текст здесь...")
        self.text_edit.setFont(QFont("Arial", 12))

        layout.addWidget(self.text_edit)
        self.setLayout(layout)

        # Если есть путь к файлу — загружаем его содержимое
        if self.filepath:
            self.loadFileContent()

    def loadFileContent(self):
        """Загружает содержимое файла в текстовый редактор"""
        try:
            with open(self.filepath, 'r', encoding='utf-8') as f:
                self.text_edit.setText(f.read())
        except Exception as e:
            QMessageBox.critical(self, "Ошибка загрузки", f"Не удалось открыть файл:\n{e}")


class TextCanvas(QMainWindow):
    def __init__(self, search_path):
        super().__init__()
        self.initUI()
        self.search_path = search_path

    def initUI(self):
        # Основной layout
        central_widget = QWidget()
        self.layout = QVBoxLayout()

        # Панель инструментов
        self.toolbar = QToolBar()
        self.toolbar.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)

        # Выбор шрифта11111111111 pdf
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

        # Кнопка подчёркивания
        underline_action = QAction("Подчёркнутый", self)
        underline_action.setCheckable(True)
        underline_action.toggled.connect(self.toggle_underline)
        self.toolbar.addAction(underline_action)

        # Поле выбора шрифта2222222222222 txt
        # self.font_combo = QFontComboBox()
        # self.font_combo.currentFontChanged.connect(self.changeFont)
        # self.toolbar.addWidget(self.font_combo)

        # Поле выбора размера шрифта
        self.size_combo = QComboBox()
        self.size_combo.addItems([str(s) for s in range(8, 72, 2)])
        self.size_combo.setCurrentText("12")
        self.size_combo.currentTextChanged.connect(self.changeFontSize)
        self.toolbar.addWidget(self.size_combo)

        # Кнопки форматирования
        bold_action = QAction('Жирный', self)
        bold_action.triggered.connect(self.toggleBold)
        self.toolbar.addAction(bold_action)

        italic_action = QAction('Курсив', self)
        italic_action.triggered.connect(self.toggleItalic)
        self.toolbar.addAction(italic_action)

        underline_action = QAction('Подчёркнутый', self)
        underline_action.triggered.connect(self.toggleUnderline)
        self.toolbar.addAction(underline_action)

        # Кнопка открытия файла
        open_action = QAction('Открыть', self)
        open_action.setShortcut('Ctrl+O')
        open_action.triggered.connect(self.openFile)
        self.toolbar.addAction(open_action)

        # Кнопка сохранения
        save_action = QAction('Сохранить', self)
        save_action.setShortcut('Ctrl+S')
        save_action.triggered.connect(self.saveCurrentTab)
        self.toolbar.addAction(save_action)

        # Виджет вкладок
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)  # Возможность закрывать вкладки
        self.tab_widget.tabCloseRequested.connect(self.closeTab)
        self.tab_widget.currentWidget()
        # self.layout.addWidget(self.tab_widget)

        # Добавляем начальную пустую вкладку
        self.addNewTab()

        self.layout.addWidget(self.toolbar)
        self.layout.addWidget(self.tab_widget)
        central_widget.setLayout(self.layout)
        self.setCentralWidget(central_widget)

        # Статус-бар для сообщений
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)

        self.setWindowTitle("Интерактивный текстовый холст с вкладками")
        self.resize(900, 700)

        self.document_cache = {}

    # Методы для работы с вкладками
    def addNewTab(self, filepath=None):
        """Добавляет новую вкладку с текстовым редактором"""
        # tab = TextTab(filepath)

        extension = ''
        if filepath:
            tab_name = filepath.split('/')[-1]  # Берём только имя файла
            extension = tab_name.split('.')[1]
        else:
            tab = TextTab(filepath)
            tab_name = "Новый документ.txt"
            index = self.tab_widget.addTab(tab, tab_name)
            self.tab_widget.setCurrentIndex(index)
        # print(tab_name)
        if extension == 'pdf':
            try:
                # text = ExtractText().extraction(tab_name)
                html_content = ''
                with fitz.open(filepath) as doc:
                    html_content = ''.join(page.get_text("html") for page in doc)

                print('1')

                # printer = QPrinter(QPrinter.HighResolution)
                # printer.setOutputFormat(QPrinter.PdfFormat)
                # printer.setOutputFileName(tab_name)
                # printer.setPageSize(QPrinter.A4)
                # printer.setPageMargins(0.1, 0.1, 0.1, 0.1, QPrinter.Millimeter)
                # self.text_edit = QTextEdit()
                # print('2', printer)
                # text_html = self.text_edit.toHtml()
                # text_file = QTextEdit.toHtml(self.tab_widget.currentWidget())
                # print('2', text_file)
                self.text_edit = QTextEdit()
                print('3', self.text_edit)
                self.text_edit.setHtml(html_content)
                # temp_text_edit.print(printer)

                # print('4', temp_text_edit.print(printer))
                # current_widget = self.tab_widget.currentWidget()
                # text_html = current_widget.text_edit.toHtml()
                # temp_text_edit1 = QTextEdit()
                # temp_text_edit1.setHtml(temp_text_edit.document().toHtml())
                # print('2', text_html)
                # self.text_edit.setPlainText(text)
                # self.text_edit.setReadOnly(False)  # Только для чтения
                #
                # index = self.tab_widget.addTab(self.text_edit, tab_name)
                # self.tab_widget.setCurrentIndex(index)
                # web_view = QWebEngineView()
                # print('1', web_view)
                # web_view.load(QUrl.fromLocalFile(filepath))
                # # web_view = ''
                # print('2', web_view)
                # # index = self.tabs.addTab(web_view, tab_name)
                # # print('', index)
                # index = self.tab_widget.addTab(web_view, "WebEngine")
                # self.tab_widget.setCurrentIndex(index)
                # self.web_view.load(QUrl.fromLocalFile(filepath))
                # Загружаем PDF документ
                # doc = fitz.open(filepath)
                # self.document_cache[filepath] = doc
                # print('doc', doc)
                #
                # # Создаём виджет для отображения PDF
                # pdf_widget = CreatePdfViewer().create_pdf_viewer(doc)
                # print('pdf_widget', pdf_widget)
                # # Добавляем вкладку
                # tab_name = filepath.split('/')[-1]
                index = self.tab_widget.addTab(self.text_edit, tab_name)
                print('index', index)
                self.tab_widget.setCurrentIndex(index)
            except Exception as e:
                print(f"Ошибка извлечения текста: {e}")

        elif extension == 'txt':
            print('jib,rf')
            tab = TextTab(filepath)
            print('jib,rf', tab)
            index = self.tab_widget.addTab(tab, tab_name)
            self.tab_widget.setCurrentIndex(index)

    def closeTab(self, index):
        """Закрывает вкладку по индексу"""
        if self.tab_widget.count() > 1:  # Не даём закрыть последнюю вкладку
            self.tab_widget.removeTab(index)
        else:
            QMessageBox.information(self, "Внимание", "Нельзя закрыть последнюю вкладку!")

            # Методы форматирования

    def change_font(self, font):
        file_name = self.tab_widget.tabText(self.tab_widget.currentIndex())
        # file_name = file + '.txt'
        print('f', file_name)
        if file_name.split('.')[1] == 'pdf':
            print('2', file_name)
            cursor = self.text_edit.textCursor()
            if cursor.hasSelection():
                fmt = QTextCharFormat()
                fmt.setFont(font)
                cursor.mergeCharFormat(fmt)
            else:
                self.text_edit.setCurrentFont(font)
        elif file_name.split('.')[1] == 'txt':
            print('3', file_name)
            self.changeFont(font)

    def change_font_size(self, size):
        cursor = self.text_edit.textCursor()
        if cursor.hasSelection():
            fmt = QTextCharFormat()
            fmt.setFontPointSize(size)
            cursor.mergeCharFormat(fmt)
        else:
            font = self.text_edit.currentFont()
            font.setPointSize(size)
            self.text_edit.setCurrentFont(font)

    def toggle_bold(self, checked):
        fmt = QTextCharFormat()
        fmt.setFontWeight(QFont.Bold if checked else QFont.Normal)
        self.text_edit.mergeCurrentCharFormat(fmt)

    def toggle_underline(self, checked):
        fmt = QTextCharFormat()
        fmt.setUnderlineStyle(QTextCharFormat.SingleUnderline if checked else QTextCharFormat.NoUnderline)
        self.text_edit.mergeCurrentCharFormat(fmt)

    # Обработчики форматирования
    def changeFont(self, font):
        current_tab = self.getCurrentTextEdit()
        if current_tab:
            current_tab.setCurrentFont(font)

    def changeFontSize(self, size):
        current_tab = self.getCurrentTextEdit()
        if current_tab and size:
            current_tab.setFontPointSize(int(size))

    def toggleBold(self):
        current_tab = self.getCurrentTextEdit()
        if current_tab:
            fmt = current_tab.currentCharFormat()
            fmt.setFontWeight(QFont.Bold if not fmt.fontWeight() == QFont.Bold else QFont.Normal)
            current_tab.mergeCurrentCharFormat(fmt)

    def toggleItalic(self):
        current_tab = self.getCurrentTextEdit()
        if current_tab:
            state = current_tab.fontItalic()
            current_tab.setFontItalic(not state)

    def toggleUnderline(self):
        current_tab = self.getCurrentTextEdit()
        if current_tab:
            state = current_tab.fontUnderline()
            current_tab.setFontUnderline(not state)

    def getCurrentTextEdit(self):
        """Возвращает текущий текстовый редактор из активной вкладки"""
        current_widget = self.tab_widget.currentWidget()
        if current_widget:
            return current_widget.text_edit
        return None

    # Блок открытия файла
    def openFile(self):
        """Открывает диалог выбора файла и загружает его в новой вкладке"""
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Открыть текстовый файл",
            "",
            "Текстовые файлы (*.txt);;Все файлы (*)"
        )
        self.addNewTab(filename)
        self.statusBar.showMessage(f"Файл открыт: {filename}", 3000)

    # Блок сохранения файла
    def saveCurrentTab(self):
        """Сохраняет текущий активный файл"""
        # print('1b', self.tab_widget.tabText(self.tab_widget.currentIndex()))
        # file_name = ''
        file_name = self.tab_widget.tabText(self.tab_widget.currentIndex())
        print('file_name', self.tab_widget.childrenRegion())
        # textpp_file = QTextEdit(self.tab_widget.currentWidget())
        # print('file_textpp', textpp_file)
        # file_current_text = self.tab_widget.currentWidget().text_edit.toPlainText()
        # current_widget = self.tab_widget.currentWidget()

        # print('file_name', textpp_file)
        # current_widget = ''
        # text_file = ''
        if file_name.split('.')[1] == 'txt':
            current_widget = self.tab_widget.currentWidget()
            text_file = current_widget.text_edit.toPlainText()
            if not current_widget:
                print('2')
                return
            if current_widget.filepath:  # Если файл уже был открыт
                print('3')
                self._saveToFile(current_widget.filepath, text_file)
            else:
                filename, _ = QFileDialog.getSaveFileName(
                    self,
                    "Сохранить файл",
                    "",
                    "Текстовые файлы (*.txt);;Файлы PDF (*.pdf);;Все файлы (*)"
                )
                if filename:
                    current_widget.filepath = filename
                    tab_name = filename.split('/')[-1]
                    if tab_name.split('.')[1] == 'txt':
                        self.tab_widget.setTabText(self.tab_widget.currentIndex(), tab_name)
                        self._saveToFile(filename, text_file)
                    elif tab_name.split('.')[1] == 'pdf':
                        print('blinbom')
                        text_file = current_widget.text_edit.toHtml()
                        temp_text_edit = QTextEdit()
                        temp_text_edit.setHtml(text_file)
                        print('333', temp_text_edit)
                        self._saveToFile(tab_name, temp_text_edit)
                        # WritingText().writing(CreateFile().creation(tab_name), text_file)
                        # self.text_edit = QTextEdit()
                        # self.text_edit.setPlainText(text_file)
                        # self.text_edit.setReadOnly(False)
                        # index = self.tab_widget.addTab(self.text_edit, tab_name)
                        # self.tab_widget.setCurrentIndex(index)
                        # self.addNewTab(current_widget.filepath)
                        # self.closeTab(0)


        elif file_name.split('.')[1] == 'pdf':  # Если файл уже был открыт
            print('44')
            # file_path = self.search_path.find_file_smart(file_name)
            print('444')
            # current_widget = self.tab_widget.currentWidget()
            # print('current_widget', current_widget)
            # self.tab_widget.setTabText(self.tab_widget.currentIndex(), file_name)
            text_file = QTextEdit.toHtml(self.tab_widget.currentWidget())
            temp_text_edit = QTextEdit()
            temp_text_edit.setHtml(text_file)
            print('4444', temp_text_edit)
            self._saveToFile(file_name, temp_text_edit)

    def _saveToFile(self, filepath, text_edit):
        """Вспомогательный метод для сохранения текста в указанный файл"""
        print('выбранный файл', str(filepath).split('.')[-1])
        try:
            if filepath.split('.')[-1] == 'txt':
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(text_edit)
                    print('в выбранный файл')
                self.statusBar.showMessage(f"Файл сохранён: {filepath}", 8000)  # Сообщение на 3 секунды
            elif filepath.split('.')[-1] == 'pdf':
                # symbols = str.maketrans('/\/', '///')
                # path = str(filepath).translate(symbols)
                print('555')
                self.tab_widget.setTabText(self.tab_widget.currentIndex(), filepath)
                WritingTextHTML().writing_html(filepath, text_edit)
                self.statusBar.showMessage(f"Файл сохранён: {filepath}", 8000)
            #     WritingText().writing(CreateFile().creation(filepath), text_edit)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка сохранения", f"Не удалось сохранить файл:\n{e}")


class ExtractText:
    """ Класс для извлечения текста из PDF файла"""

    def extraction(self, input_filename: str) -> str:
        text = ''
        with fitz.open(input_filename) as doc:
            for page in doc:
                page_text = page.get_text()
                text += page_text
        return text


class CreatePdfViewer:
    @staticmethod
    def create_pdf_viewer(doc):
        """Создаёт виджет для просмотра PDF"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Выборка страниц
        page_selector = QComboBox()
        for i in range(len(doc)):
            page_selector.addItem(f"Страница {i + 1}")
        page_selector.currentIndexChanged.connect(
            lambda index: ShouPdf().show_pdf_page(doc, index, widget)
        )
        layout.addWidget(page_selector)

        # Область для отображения страницы
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(False)
        widget.scroll_area = scroll_area  # Сохраняем ссылку
        layout.addWidget(scroll_area)
        # self.text_edit = QTextEdit()
        # self.text_edit.setPlainText(text)
        # self.text_edit.setReadOnly(False)

        # Показываем первую страницу
        ShouPdf().show_pdf_page(doc, 0, widget)

        return widget


class ShouPdf:
    @staticmethod
    def show_pdf_page(doc, page_num, parent_widget):
        """Отображает указанную страницу PDF"""
        try:
            page = doc.load_page(page_num)
            # Конвертируем страницу в изображение
            pix = page.get_pixmap(dpi=150)  # Высокое разрешение

            # Конвертируем в QPixmap для отображения
            img_data = pix.tobytes("ppm")
            pixmap = QPixmap()
            pixmap.loadFromData(img_data)

            # Создаём метку для изображения
            label = QLabel()
            label.setPixmap(pixmap)
            label.setAlignment(Qt.AlignCenter)

            # Обновляем содержимое скролл‑области
            parent_widget.scroll_area.setWidget(label)
        except Exception as e:
            print(f"Ошибка отображения страницы: {e}")


class CreateFile:
    """ Класс для создания нового файла """

    @staticmethod
    def creation(name_f) -> str:
        document = fitz.open()
        document.new_page()
        output = name_f
        document.save(filename=output)
        document.close()
        return output


class WritingText:
    @staticmethod
    def writing(new_file: str, text) -> None:
        pdfmetrics.registerFont(TTFont('DejaVuSans', 'DejaVuSans.ttf'))
        my_style = ParagraphStyle(name='MyStyle', fontName='DejaVuSans', fontSize=12)
        with fitz.open(new_file):
            doc = SimpleDocTemplate(
                new_file.split('/')[-1],
                pagesize=letter,
                bottomMargin=.4 * inch,
                topMargin=.6 * inch,
                rightMargin=.8 * inch,
                leftMargin=.8 * inch
            )
            story = [Paragraph(text, my_style)]
            doc.build(story)
        return doc.filename


class WritingTextHTML:
    """ Класс для записи текста в новый файл """

    @staticmethod
    def writing_html(new_file: str, text) -> None:
        pdfmetrics.registerFont(TTFont('DejaVuSans', 'DejaVuSans.ttf'))
        my_style = ParagraphStyle(name='MyStyle', fontName='DejaVuSans', fontSize=12)

        printer = QPrinter(QPrinter.HighResolution)
        printer.setOutputFormat(QPrinter.PdfFormat)
        printer.setOutputFileName(new_file)
        printer.setPageSize(QPrinter.A4)
        printer.setPageMargins(0.1, 0.1, 0.1, 0.1, QPrinter.Millimeter)

        text.document().print_(printer)
        # Сохраняем файл
        # with open(new_file, 'wb') as f:
        #     f.write(pdf)

        # with fitz.open(new_file):
        #     doc = SimpleDocTemplate(
        #     new_file.split('/')[-1],
        #     pagesize=letter,
        #     bottomMargin=.4 * inch,
        #     topMargin=.6 * inch,
        #     rightMargin=.8 * inch,
        #     leftMargin=.8 * inch
        #     )
        #     story = [Paragraph(text, my_style)]
        #     doc.build(story)
        # return doc.filename


class SearchPath:
    def find_file_smart(self, filename: str) -> Path | None:
        """
        Ищет файл сначала в текущей директории, потом во всём компьютере.

        Args:
            filename: имя файла для поиска

        Returns:
            Path объекта найденного файла или None, если не найден
        """
        # Шаг 1. Поиск в текущей директории (не рекурсивно)
        current_dir = Path.cwd()
        local_matches = list(current_dir.glob(filename))
        local_files = [p for p in local_matches if p.is_file()]

        if local_files:
            print(f"✅ Файл найден в текущей директории: {local_files[0].absolute()}")
            return local_files[0].resolve()

        print(f"❌ Файл не найден в текущей директории. Начинаю поиск по всему компьютеру...")

        # Шаг 2. Поиск по всему компьютеру
        system = platform.system()

        if system == "Windows":
            # В Windows ищем по всем дискам C:\, D:\ и т. д.
            drives = [Path(f"{letter}:\\") for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ"]
            drives = [drive for drive in drives if drive.exists()]
            for drive in drives:
                try:
                    matches = drive.rglob(filename)
                    for file_path in matches:
                        if file_path.is_file():
                            print(f"✅ Файл найден: {file_path.resolve()}")
                            return file_path.resolve()
                except PermissionError:
                    print(f"⚠️  Нет доступа к диску {drive}, пропускаю...")
                    continue
        else:  # Linux, macOS и др.
            # Начинаем с корневой директории /
            try:
                matches = Path("/").rglob(filename)
                for file_path in matches:
                    if file_path.is_file():
                        print(f"✅ Файл найден: {file_path.resolve()}")
                        return file_path.resolve()
            except PermissionError:
                print("⚠️  Нет доступа к некоторым директориям, часть системы может быть не проверена.")

        print("❌ Файл не найден на всём компьютере.")
        return None

    # Использование
    # if __name__ == "__main__":
    #     filename_to_find = "document.txt"  # Замените на нужное имя файла
    #     result = find_file_smart(filename_to_find)
    #
    #     if result:
    #         print(f"\nИтоговый путь: {result}")
    #     else:
    #         print("\nФайл не найден.")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    search_filepath = SearchPath()
    canvas = TextCanvas(search_filepath)
    canvas.show()
    sys.exit(app.exec_())