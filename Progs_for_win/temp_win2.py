import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QTextEdit, QToolBar, QAction, QFontComboBox, QComboBox
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

class TextCanvas(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # Основной layout
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
        self.size_combo.currentTextChanged.connect(self.changeFontSize)
        toolbar.addWidget(self.size_combo)

        # Кнопка сохранения
        save_action = QAction('Сохранить', self)
        save_action.setShortcut('Ctrl+S')
        save_action.triggered.connect(self.saveFile)
        toolbar.addAction(save_action)

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

        # Текстовый холст
        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText("Начните вводить текст здесь...")
        self.text_edit.setFont(QFont("Arial", 12))

        # Добавляем элементы в layout
        layout.addWidget(toolbar)
        layout.addWidget(self.text_edit)
        self.setLayout(layout)

        self.setWindowTitle("Интерактивный текстовый холст")
        self.resize(800, 600)

    # Обработчики форматирования
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

if __name__ == '__main__':
    app = QApplication(sys.argv)
    canvas = TextCanvas()
    canvas.show()
    sys.exit(app.exec_())