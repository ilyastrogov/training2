from PyQt5.QtWidgets import (QApplication, QMainWindow, QTabWidget, QTextEdit, QGraphicsScene,
                             QPushButton, QVBoxLayout, QWidget, QFontDialog, QFileDialog,
                             QComboBox, QToolBar, QMessageBox, QLabel, QListWidget,
                             QFontComboBox, QGraphicsView, QListWidgetItem, QDialogButtonBox,
                             QGroupBox, QHBoxLayout, QSpinBox)
from PyQt5.QtGui import (QTextCharFormat, QFont, QTextDocument, QPdfWriter, QTextCursor,
                         QPainter, QFontDatabase, QPen)
from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtWidgets import QSizePolicy, QDialog

import sys

from abc import ABC, abstractmethod
from tkinter import messagebox, filedialog
import tkinter as tk



# Основной контейнер
class AddLayout(ABC):

    @abstractmethod
    def create_layout(self, arg=None):
        pass

    @abstractmethod
    def add_layout(self):
        pass


# Вкладки с редакторами
class CreateTabWidget(ABC):
    @abstractmethod
    def create_tab_widget(self, close_tab):
        pass


# Создание новой вкладки
class CreateNewTab(ABC):
    @abstractmethod
    def create_new_tab(self, title):
        """Создаёт новую вкладку с QTextEdit."""
        pass

    """ Рассчитывает размер страницы A4 """

    @abstractmethod
    def calculate_pdf_page_size(self, dpi=96):
        pass


# Создание кнопок
class CreateElem(ABC):
    @abstractmethod
    def create_elem(self, toolbar, btn, functions):
        pass


"""Смена шрифта через диалоговое окно."""


class ChangeFont(ABC):
    @abstractmethod
    def change_font(self):
        pass

    @abstractmethod
    def set_active_font(self, font):
        pass


""" Открытие файла """


class OpenPdf(ABC):
    @abstractmethod
    def open_pdf(self):
        pass

""" Сохранение файла """


class SavePdf(ABC):
    @abstractmethod
    def save_as_pdf(self):
        pass


class CloseTab(ABC):
    @abstractmethod
    def close_tab(self, index):
        pass





# Настройки окна
class WindowConfigurator(AddLayout, CreateTabWidget, CreateNewTab,
                         SavePdf, CloseTab,
                         CreateElem, ChangeFont, OpenPdf):
    def __init__(self):
        super().__init__()
        # Вкладки с редакторами
        self.tab_widget = None
        # Основной контейнер
        self.central_widget = None
        self.layout = None

        self.text_edit = None
        # Окно выбора файла
        self.root = tk.Tk()
        self.root.withdraw()
        # База шрифтов
        self.font_db = QFontDatabase()
        self.font_cache = {}  # Кэш для ускорения
        self.loaded_font_ids = []  # Храним ID загруженных шрифтов, чтобы не дублировать

        # 1. Инициализация словаря: ключ=(family, weight), значение=путь к файлу
        # weight: "Normal" или "Bold"
        self.font_map = {}

    def create_central_widget(self):
        self.central_widget = QWidget()
        return self.central_widget

    def create_widget(self):
        self.tab_widget = QTabWidget()
        return self.tab_widget

    def create_text_edit(self):
        self.text_edit = QTextEdit()
        return self.text_edit

    # Вкладки с редакторами
    def create_tab_widget(self, close_tab):
        self.tab_widget = self.create_widget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.tabCloseRequested.connect(close_tab)
        return self.tab_widget

    # Создаём layout и сохраняем в self.layout
    def create_layout(self, arg=None):
        self.layout = QVBoxLayout(arg) if arg else QVBoxLayout()
        return self.layout

    # Вставляем макет
    def add_layout(self):
        self.layout = self.create_layout()
        self.central_widget = self.create_central_widget()
        self.layout.addWidget(self.tab_widget)
        self.central_widget.setLayout(self.layout)
        return self.central_widget


    def create_new_tab(self, title):
        # Рассчитываем размер A4
        page_width, page_height = self.calculate_pdf_page_size(dpi=96)

        # Создаём контейнер для центрирования
        self.central_widget = self.create_central_widget()
        self.layout = self.create_layout(self.central_widget)
        self.layout.setAlignment(Qt.AlignCenter)  # Центрируем по горизонтали и вертикали

        self.text_edit = self.create_text_edit()
        self.text_edit.setFixedSize(page_width, page_height)
        self.text_edit.setSizePolicy(QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed))
        self.text_edit.setViewportMargins(15, 15, 15, 15)  # Отступы внутри QTextEdit

        self.layout.addWidget(self.text_edit)

        index = self.tab_widget.addTab(self.central_widget, title)
        self.tab_widget.setCurrentIndex(index)
        return self.text_edit

    """ Рассчитывает размер страницы A4 """

    def calculate_pdf_page_size(self, dpi=96):
        """
        Рассчитывает размер страницы A4 в пикселях.
        :param dpi: Разрешение экрана (точек на дюйм)
        :return: кортеж (ширина, высота) в пикселях
        """
        # Размеры A4 в мм
        a4_width_mm = 210
        a4_height_mm = 297

        # Конвертируем мм в дюймы, затем в пиксели
        a4_width_inches = a4_width_mm / 25.4  # 1 дюйм = 25.4 мм
        a4_height_inches = a4_height_mm / 25.4

        width_pixels = int(a4_width_inches * dpi)
        height_pixels = int(a4_height_inches * dpi)

        return width_pixels, height_pixels

    # Создание кнопок
    def create_elem(self, toolbar, btn, functions):
        count = 0
        for button in btn:
            button.clicked.connect(functions[count])
            count += 1
            toolbar.addWidget(button)



    """Смена шрифта через диалоговое окно."""

    def change_font(self):
        """Смена шрифта через диалоговое окно."""
        current_widget = self.tab_widget.currentWidget()
        text_edit = current_widget.findChild(QTextEdit)
        current_widget = text_edit
        if not isinstance(current_widget, QTextEdit):
            return

        current_format = current_widget.currentCharFormat()
        initial_font = current_format.font()

        font, ok = QFontDialog.getFont(initial_font)
        if ok:
            self.set_active_font(font)

    # для change_font
    def set_active_font(self, font):
        """Устанавливает активный шрифт для текущего виджета."""
        current_widget = self.tab_widget.currentWidget()
        self.text_edit = current_widget.findChild(QTextEdit)
        current_widget = self.text_edit
        cursor = current_widget.textCursor()

        if cursor.hasSelection():
            fmt = QTextCharFormat()
            fmt.setFont(font)
            cursor.mergeCharFormat(fmt)

        active_format = QTextCharFormat()
        print(font.family())
        active_format.setFont(font)
        current_widget.setCurrentCharFormat(active_format)

    # Открытие файла
    def open_pdf(self):
        """Открывает PDF-файл и конвертирует в текст для редактирования."""

        filepath = filedialog.askopenfilename(
            title="Открыть файл",
            defaultextension=".pdf",  # Автоматическое добавление расширения, если пользователь его не укажет
            filetypes=[("PDF файлы", "*.pdf"), ("Все файлы", "*.*")]  # Фильтрация типов файлов

        )
        if not filepath:
            return
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                html = f.read()
                print(html)
            self.text_edit.document().setHtml(html)
            messagebox.showinfo("Успех", f"PDF-файл {filepath} успешно открыт!")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось открыть PDF-файл:\n{str(e)}")




    def save_as_pdf(self):
        """Сохраняет текущий документ в PDF-файл."""
        current_widget = self.tab_widget.currentWidget()
        self.text_edit = current_widget.findChild(QTextEdit)
        if not isinstance(self.text_edit, QTextEdit):
            return
        filepath = filedialog.asksaveasfilename(
            title="Сохранить файл",
            defaultextension=".pdf",  # Автоматическое добавление расширения, если пользователь его не укажет
            filetypes=[("PDF файлы", "*.pdf"), ("Все файлы", "*.*")]  # Фильтрация типов файлов

        )

        if not filepath:
            return

        try:


            html = self.text_edit.document().toHtml()
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(html)


            messagebox.showinfo("Успех", f"Документ сохранён как PDF:\n{filepath}")


        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить PDF:\n{str(e)}")



    def close_tab(self, index):
        """Закрывает вкладку по индексу."""
        if self.tab_widget.count() > 1:
            self.tab_widget.removeTab(index)
        else:
            messagebox.showerror("Предупреждение", "Нельзя закрыть последнюю вкладку!")


class PDFTextEditor(QMainWindow):
    def __init__(self):
        super().__init__()

        # Настройки окна
        self.configurator = WindowConfigurator()
        # Вкладки с редакторами
        self.configurator.create_tab_widget(self.configurator.close_tab)
        # Панель инструментов
        self.toolbar = QToolBar()
        # Кнопки
        self.font_btn = QPushButton("Выбрать шрифт...")
        self.open_btn = QPushButton("Открыть")
        self.save_btn = QPushButton("Сохранить как")
        self.replace_font_btn = QPushButton("Заменить шрифт из папки")  # НОВАЯ КНОПКА
        # Метод инициализации
        self.init_ui()

    def init_ui(self):
        # Настройки окна
        self.setWindowTitle("Редактор с поддержкой PDF")
        self.setGeometry(100, 100, 1200, 800)
        # Создаём начальную вкладку
        self.configurator.create_new_tab("Новая вкладка")
        # Создание центрального виджета
        self.setCentralWidget(self.configurator.add_layout())
        # Панель инструментов
        self.addToolBar(self.toolbar)
        # Создание кнопок
        # print(self.change_font)
        self.configurator.create_elem(
            self.toolbar,
            btn=[self.font_btn, self.open_btn, self.save_btn],
            functions=[self.configurator.change_font,
                       self.configurator.open_pdf,
                       self.configurator.save_as_pdf]
        )




if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = PDFTextEditor()
    window.show()
    sys.exit(app.exec_())
