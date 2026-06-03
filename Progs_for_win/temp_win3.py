import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QTextEdit,
                             QToolBar, QAction, QFontComboBox, QComboBox, QFileDialog,
                             QMessageBox, QStatusBar, QWidget,)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt


class TextCanvas(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_file = None  # Хранит путь к текущему файлу
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

        # Кнопка сохранения
        save_action = QAction('Сохранить', self)
        save_action.setShortcut('Ctrl+S')
        save_action.triggered.connect(self.saveFile)
        toolbar.addAction(save_action)

        # Кнопка сохранения
        open_action = QAction('Открыть', self)
        open_action.setShortcut('Ctrl+A')
        open_action.triggered.connect(self.openFile)
        toolbar.addAction(open_action)

        # Текстовый холст
        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText("Начните вводить текст здесь...")
        self.text_edit.setFont(QFont("Arial", 12))

        # Добавляем элементы в layout
        layout.addWidget(toolbar)
        layout.addWidget(self.text_edit)
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        # Статус-бар для сообщений
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)

        self.setWindowTitle("Интерактивный текстовый холст")
        self.resize(800, 600)

    # Обработчики форматирования (без изменений)
    def changeFont(self, font):
        self.text_edit.setCurrentFont(font)


    def changeFontSize(self, size):
        if size:
            self.text_edit.setFontPointSize(int(size))

    def toggleBold(self):
        fmt = self.text_edit.currentCharFormat()
        fmt.setFontWeight(QFont.Bold if not fmt.fontWeight() == QFont.Bold else QFont.Normal)
        self.text_edit.mergeCurrentCharFormat(fmt)

    def toggleItalic(self):
        state = self.text_edit.fontItalic()
        self.text_edit.setFontItalic(not state)

    def toggleUnderline(self):
        state = self.text_edit.fontUnderline()
        self.text_edit.setFontUnderline(not state)

    def openFile(self):
        # Открываем диалоговое окно выбора файла
        file_path, _ = QFileDialog.getOpenFileName(None, "Открыть файл", "",
                                                   "Все файлы (*);;Текстовые файлы (*.txt);;Python файлы (*.py)")

        if file_path:
            # self.setWindowTitle("Интерактивный текстовый холст")
            # self.resize(800, 600)
            # Здесь можно выполнить действия с выбранным файлом (например, прочитать его содержимое)
            # t = ''
            with open(file_path, 'r') as file:
                content = file.read()
                # t = content
            self.text_edit1 = QTextEdit()
            self.text_edit1.setPlaceholderText(content)
            self.text_edit1.setFont(QFont("Arial", 12))  # Или выполнить другие операции с файлом
            self.setWindowTitle("Интерактивный текстовый холст")
            self.resize(800, 600)

    # Блок сохранения файла
    def saveFile(self):
        """Сохраняет текст в файл с диалогом выбора пути"""
        if self.current_file:
            # Если файл уже был сохранён, перезаписываем его
            self._saveToFile(self.current_file)
        else:
            # Если файла ещё нет, открываем диалог выбора пути
            filename, _ = QFileDialog.getSaveFileName(
                self,
                "Сохранить файл",
                "",
                "Текстовые файлы (*.txt);;Все файлы (*)"
            )
            if filename:
                self.current_file = filename
                self._saveToFile(filename)

    def _saveToFile(self, filepath):
        """Вспомогательный метод для сохранения текста в указанный файл"""
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(self.text_edit.toPlainText())
            self.statusBar.showMessage(f"Файл сохранён: {filepath}", 3000)  # Сообщение на 3 секунды
        except Exception as e:
            QMessageBox.critical(self, "Ошибка сохранения", f"Не удалось сохранить файл:\n{e}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    canvas = TextCanvas()
    canvas.show()
    sys.exit(app.exec_())