
import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QTextEdit,
                             QToolBar, QAction, QFontComboBox, QComboBox, QFileDialog,
                             QMessageBox, QStatusBar, QTabWidget, QWidget)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.styles import ParagraphStyle

import fitz

# import
# from file_date import WritingText, CreateFile
class TextTab(QWidget):
    """Виджет вкладки с текстовым редактором и информацией о файле"""
    def __init__(self, filepath=None):
        super().__init__()
        self.filepath = filepath
        self.initUI()

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
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # Основной layout
        central_widget = QWidget()
        layout = QVBoxLayout()

        # Панель инструментов
        toolbar = QToolBar()
        toolbar.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)

        # Поле выбора шрифта
        self.font_combo = QFontComboBox()
        self.font_combo.currentFontChanged.connect(self.changeFont)
        toolbar.addWidget(self.font_combo)

        # Поле выбора размера шрифта
        self.size_combo = QComboBox()
        self.size_combo.addItems([str(s) for s in range(8, 72, 2)])
        self.size_combo.setCurrentText("12")
        self.size_combo.currentTextChanged.connect(self.changeFontSize)
        toolbar.addWidget(self.size_combo)

        # Кнопки форматирования
        bold_action = QAction('Жирный', self)
        bold_action.triggered.connect(self.toggleBold)
        toolbar.addAction(bold_action)

        italic_action = QAction('Курсив', self)
        italic_action.triggered.connect(self.toggleItalic)
        toolbar.addAction(italic_action)

        underline_action = QAction('Подчёркнутый', self)
        underline_action.triggered.connect(self.toggleUnderline)
        toolbar.addAction(underline_action)

        # Кнопка открытия файла
        open_action = QAction('Открыть', self)
        open_action.setShortcut('Ctrl+O')
        open_action.triggered.connect(self.openFile)
        toolbar.addAction(open_action)

        # Кнопка сохранения
        save_action = QAction('Сохранить', self)
        save_action.setShortcut('Ctrl+S')
        save_action.triggered.connect(self.saveCurrentTab)
        toolbar.addAction(save_action)

        # Виджет вкладок
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)  # Возможность закрывать вкладки
        self.tab_widget.tabCloseRequested.connect(self.closeTab)

        # Добавляем начальную пустую вкладку
        self.addNewTab()

        layout.addWidget(toolbar)
        layout.addWidget(self.tab_widget)
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        # Статус-бар для сообщений
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)

        self.setWindowTitle("Интерактивный текстовый холст с вкладками")
        self.resize(900, 700)

    # Методы для работы с вкладками
    def addNewTab(self, filepath=None):
        """Добавляет новую вкладку с текстовым редактором"""
        tab = TextTab(filepath)
        if filepath:
            tab_name = filepath.split('/')[-1]  # Берём только имя файла
        else:
            tab_name = "Новый документ"

        index = self.tab_widget.addTab(tab, tab_name)
        self.tab_widget.setCurrentIndex(index)

    def closeTab(self, index):
        """Закрывает вкладку по индексу"""
        if self.tab_widget.count() > 1:  # Не даём закрыть последнюю вкладку
            self.tab_widget.removeTab(index)
        else:
            QMessageBox.information(self, "Внимание", "Нельзя закрыть последнюю вкладку!")

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
        if filename:
            self.addNewTab(filename)
            self.statusBar.showMessage(f"Файл открыт: {filename}", 3000)

    # Блок сохранения файла
    def saveCurrentTab(self):
        """Сохраняет текущий активный файл"""
        current_widget = self.tab_widget.currentWidget()
        if not current_widget:
            return

        if current_widget.filepath:  # Если файл уже был открыт
            self._saveToFile(current_widget.filepath, current_widget.text_edit)
        else:  # Если это новый документ
            filename, _ = QFileDialog.getSaveFileName(
                self,
                "Сохранить файл",
                "",
                "Текстовые файлы (*.txt);;Все файлы (*)"
            )
            if filename:
                current_widget.filepath = filename
                tab_name = filename.split('/')[-1]
                pdf_file = tab_name.split('.')[0] + '.pdf'
                self.tab_widget.setTabText(self.tab_widget.currentIndex(), tab_name)
                self._saveToFile(filename, current_widget.text_edit)
                with open(filename, 'r', encoding='utf-8') as input_file:
                    for element in input_file.readlines():
                        WritingText().writing(CreateFile().creation(pdf_file), element)


    def _saveToFile(self, filepath, text_edit):
        """Вспомогательный метод для сохранения текста в указанный файл"""
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(text_edit.toPlainText())
            self.statusBar.showMessage(f"Файл сохранён: {filepath}", 3000)  # Сообщение на 3 секунды
        except Exception as e:
            QMessageBox.critical(self, "Ошибка сохранения", f"Не удалось сохранить файл:\n{e}")

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
    """ Класс для записи текста в новый файл """

    @staticmethod
    def writing(new_file: str, text: str)  -> str:
        pdfmetrics.registerFont(TTFont('DejaVuSans', 'DejaVuSans.ttf'))
        my_style = ParagraphStyle(name='MyStyle', fontName='DejaVuSans', fontSize=12)

        with fitz.open(new_file):
            doc = SimpleDocTemplate(
            new_file,
            pagesize=letter,
            bottomMargin=.4 * inch,
            topMargin=.6 * inch,
            rightMargin=.8 * inch,
            leftMargin=.8 * inch
            )
            story = [Paragraph(text, my_style)]
            doc.build(story)
        return doc.filename
if __name__ == '__main__':
    app = QApplication(sys.argv)
    canvas = TextCanvas()
    canvas.show()
    sys.exit(app.exec_())