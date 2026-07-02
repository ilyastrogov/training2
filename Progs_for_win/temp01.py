from PyQt5.QtWidgets import (QApplication, QMainWindow, QTabWidget, QTextEdit,
                             QPushButton, QVBoxLayout, QWidget, QFontDialog, QFileDialog,
                             QComboBox, QToolBar, QMessageBox, QLabel)
from PyQt5.QtGui import QTextCharFormat, QFont, QTextDocument
from PyQt5.QtCore import Qt
import sys
import fitz  # PyMuPDF для работы с PDF

class PDFTextEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Редактор с поддержкой PDF")
        self.setGeometry(100, 100, 1200, 800)

        # Основной контейнер
        central_widget = QWidget()
        layout = QVBoxLayout()

        # Панель инструментов
        toolbar = QToolBar()
        self.addToolBar(toolbar)

        # Выпадающий список шрифтов
        self.font_combo = QComboBox()
        self.font_combo.addItems([
            "Arial", "Times New Roman", "Courier New",
            "Verdana", "Georgia", "Calibri"
        ])
        self.font_combo.currentTextChanged.connect(self.change_font_from_combo)
        toolbar.addWidget(QLabel("Шрифт: "))
        toolbar.addWidget(self.font_combo)

        # Кнопка выбора шрифта
        font_btn = QPushButton("Выбрать шрифт...")
        font_btn.clicked.connect(self.change_font)
        toolbar.addWidget(font_btn)

        # Кнопка открытия PDF
        open_pdf_btn = QPushButton("Открыть PDF")
        open_pdf_btn.clicked.connect(self.open_pdf)
        toolbar.addWidget(open_pdf_btn)

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
            pdf_document = fitz.open(filepath)
            text_content = ""

            # Извлекаем текст со всех страниц
            for page_num in range(len(pdf_document)):
                page = pdf_document.load_page(page_num)
                text_content += page.get_text() + "\n\n"

            pdf_document.close()

            # Создаём новую вкладку с текстом из PDF
            tab_title = filepath.split('/')[-1]
            text_edit = self.create_new_tab(tab_title)
            text_edit.setText(text_content)

            # Устанавливаем шрифт по умолчанию
            default_font = QFont("Arial", 12)
            text_edit.setCurrentCharFormat(QTextCharFormat())
            fmt = QTextCharFormat()
            fmt.setFont(default_font)
            text_edit.setCurrentCharFormat(fmt)

            QMessageBox.information(self, "Успех", f"PDF-файл {tab_title} успешно открыт!")

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось открыть PDF-файл:\n{str(e)}")

    def close_tab(self, index):
        """Закрывает вкладку по индексу."""
        if self.tab_widget.count() > 1:
            self.tab_widget.removeTab(index)
        else:
            QMessageBox.warning(self, "Предупреждение", "Нельзя закрыть последнюю вкладку!")

    def save_with_format(self):
        """Сохраняет текущий документ с сохранением форматирования."""
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
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PDFTextEditor()
    window.show()
    sys.exit(app.exec_())
