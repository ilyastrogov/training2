from PyQt5.QtWidgets import (QApplication, QMainWindow, QTabWidget, QTextEdit,
                             QPushButton, QVBoxLayout, QWidget, QFontDialog,
                             QFileDialog, QComboBox, QToolBar, QMessageBox,
                             QLabel, QGraphicsView, QDialog, QListWidget,
                             QListWidgetItem, QDialogButtonBox, QHBoxLayout)
from PyQt5.QtGui import (QTextCharFormat, QFont, QTextDocument, QPen,
                         QFontDatabase, QTextCursor)
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QSizePolicy
from PyQt5.QtPrintSupport import QPrinter
import sys
import fitz  # PyMuPDF
import re
import glob
import os
from pathlib import Path
from tkinter import messagebox, filedialog
import tkinter as tk


# --- Диалог выбора шрифта из папки ---
class FontListDialog(QDialog):
    def __init__(self, font_paths, parent=None):
        super().__init__(parent)
        self.font_paths = font_paths
        self.selected_path = None
        self.setWindowTitle("Выберите шрифт из папки fonts")
        self.setMinimumSize(400, 300)

        layout = QVBoxLayout()
        self.list_widget = QListWidget()

        # Заполняем список именами файлов
        for path in self.font_paths:
            filename = os.path.basename(path)
            item = QListWidgetItem(filename)
            item.setData(Qt.UserRole, path)  # Сохраняем полный путь
            self.list_widget.addItem(item)

        self.list_widget.itemClicked.connect(self.on_item_clicked)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout.addWidget(QLabel("Список шрифтов (.ttf, .otf):"))
        layout.addWidget(self.list_widget)
        layout.addWidget(buttons)
        self.setLayout(layout)

    def on_item_clicked(self, item):
        self.selected_path = item.data(Qt.UserRole)

    def get_selected_font_path(self):
        return self.selected_path


class WindowConfigurator:
    def __init__(self):
        self.tab_widget = QTabWidget()
        self.central_widget = QWidget()
        self.layout = QVBoxLayout()
        self.root = tk.Tk()
        self.root.withdraw()
        self.font_db = QFontDatabase()
        self.font_cache = {}
        self.loaded_font_ids = []

        # --- Базовые методы UI ---

    def create_tab_widget(self, close_tab):
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.tabCloseRequested.connect(close_tab)
        return self.tab_widget

    def add_layout(self):
        self.layout.addWidget(self.tab_widget)
        self.central_widget.setLayout(self.layout)
        return self.central_widget

    def calculate_pdf_page_size(self, dpi=96):
        a4_width_mm = 210
        a4_height_mm = 297
        a4_width_inches = a4_width_mm / 25.4
        a4_height_inches = a4_height_mm / 25.4
        width_pixels = int(a4_width_inches * dpi)
        height_pixels = int(a4_height_inches * dpi)
        return width_pixels, height_pixels

    def create_new_tab(self, title):
        page_width, page_height = self.calculate_pdf_page_size(dpi=96)
        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setAlignment(Qt.AlignCenter)

        text_edit = QTextEdit()
        text_edit.setFixedSize(page_width, page_height)
        text_edit.setSizePolicy(QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed))
        text_edit.setViewportMargins(15, 15, 15, 15)
        container_layout.addWidget(text_edit)

        index = self.tab_widget.addTab(container, title)
        self.tab_widget.setCurrentIndex(index)
        return text_edit

    def create_elem(self, toolbar, btn, functions):
        count = 0
        for button in btn:
            button.clicked.connect(functions[count])
            count += 1
            toolbar.addWidget(button)

    # --- НОВАЯ ФУНКЦИЯ: Открытие диалога выбора шрифта ---
    def open_font_folder_dialog(self):
        """Ищет шрифты в папке 'fonts' и показывает диалог."""
        script_dir = os.path.dirname(os.path.abspath(__file__))
        font_folder = os.path.join(script_dir, 'fonts')

        if not os.path.exists(font_folder):
            messagebox.showwarning("Папка не найдена",
                                   f"Папка '{font_folder}' не существует.\nСоздайте её и положите туда .ttf/.otf файлы.")
            return

        patterns = ['*.ttf', '*.otf']
        font_files = []
        for pattern in patterns:
            font_files.extend(glob.glob(os.path.join(font_folder, pattern), recursive=True))
            font_files.extend(glob.glob(os.path.join(font_folder, '**', pattern), recursive=True))

        if not font_files:
            messagebox.showinfo("Шрифты не найдены", "В папке fonts нет файлов .ttf или .otf")
            return

        dialog = FontListDialog(font_files, self.tab_widget)
        if dialog.exec_() == QDialog.Accepted:
            selected_path = dialog.get_selected_font_path()
            if selected_path:
                self.apply_font_to_matching_text(selected_path)

    def apply_font_to_matching_text(self, font_path):
        """Загружает шрифт и применяет его к тексту с похожим названием."""
        current_widget = self.tab_widget.currentWidget()
        # Находим QTextEdit внутри контейнера вкладки
        text_edit = current_widget.findChild(QTextEdit)

        if not isinstance(text_edit, QTextEdit):
            return

        # 1. Загружаем шрифт в базу
        font_id = QFontDatabase.addApplicationFont(font_path)
        if font_id == -1:
            messagebox.showerror("Ошибка", "Не удалось загрузить шрифт из файла.")
            return

        self.loaded_font_ids.append(font_id)
        families = QFontDatabase.applicationFontFamilies(font_id)
        if not families:
            return

        new_family_name = families[0]
        print(f"Загружен шрифт: {new_family_name} из {font_path}")

        # Получаем имя файла без расширения для сравнения
        base_name = os.path.splitext(os.path.basename(font_path))[0]
        # Очищаем имя от суффиксов типа Bold, Italic для поиска совпадений
        clean_base = re.sub(r'(Bold|Italic|Regular|Light|Medium|DemiBold)', '', base_name, flags=re.IGNORECASE).strip()

        doc = text_edit.document()
        cursor = QTextCursor(doc)
        cursor.beginEditBlock()

        applied_count = 0

        # 2. Проходим по всем блокам и фрагментам текста
        block = doc.firstBlock()
        while block.isValid():
            iterator = block.begin()
            while not iterator.atEnd():
                fragment = iterator.fragment()
                if fragment.isValid():
                    fmt = fragment.charFormat()
                    current_font = fmt.font()
                    current_family = current_font.family()

                    # Логика сравнения:
                    match = False

                    # Вариант 1: Имя нового шрифта содержится в имени текущего (Arial -> Arial-Black)
                    if clean_base.lower() in current_family.lower():
                        match = True
                    # Вариант 2: Имя текущего шрифта содержится в имени нового (Arial-Black -> Arial)
                    elif current_family.lower() in clean_base.lower():
                        match = True
                    # Вариант 3: Точное совпадение
                    elif current_family == new_family_name:
                        match = True

                    if match:
                        # Создаем новый формат
                        new_fmt = QTextCharFormat(fmt)
                        new_font = QFont(new_family_name)

                        # Пытаемся сохранить стиль (Bold/Italic)
                        if current_font.bold():
                            new_font.setBold(True)
                        if current_font.italic():
                            new_font.setItalic(True)

                        new_fmt.setFont(new_font)

                        # Применяем формат к этому фрагменту
                        cursor.setPosition(fragment.position())
                        cursor.setPosition(fragment.position() + fragment.length(), QTextCursor.KeepAnchor)
                        cursor.mergeCharFormat(new_fmt)
                        applied_count += 1

                iterator += 1
            block = block.next()

        cursor.endEditBlock()
        messagebox.showinfo("Готово", f"Шрифт '{new_family_name}' применен к {applied_count} фрагментам текста.")

    # --- Остальные методы (исправленные и дополненные) ---

    def change_font(self):
        current_widget = self.tab_widget.currentWidget()
        text_edit = current_widget.findChild(QTextEdit)
        if not isinstance(text_edit, QTextEdit): return
        font, ok = QFontDialog.getFont(text_edit.font())
        if ok:
            self.set_active_font(font)

    def set_active_font(self, font):
        current_widget = self.tab_widget.currentWidget()
        text_edit = current_widget.findChild(QTextEdit)
        if not isinstance(text_edit, QTextEdit): return
        cursor = text_edit.textCursor()
        fmt = QTextCharFormat()
        fmt.setFont(font)
        if cursor.hasSelection():
            cursor.mergeCharFormat(fmt)
        else:
            text_edit.setCurrentCharFormat(fmt)

    def open_pdf(self):
        filepath = filedialog.askopenfilename(title="Открыть файл", filetypes=[("PDF файлы", "*.pdf")])
        if filepath:
            self.rendering_text(filepath)

    def rendering_text(self, filepath):
        try:
            tab_title = f"Редактирование: {os.path.basename(filepath)}"
            font_mapping = self.analyze_and_map_fonts(filepath)
            page_width, page_height = self.get_pdf_page_dimensions(filepath)
            text_edit = self.create_new_tab(tab_title)
            cursor = text_edit.textCursor()

            for page in font_mapping:
                prev_block_y0 = None
                for block in page["blocks"]:
                    block_y0 = block["bbox"][1]
                    if prev_block_y0 is not None and (block_y0 - prev_block_y0) > 20:
                        cursor.insertBlock()
                    prev_block_y0 = block_y0

                    for line in block["lines"]:
                        for span in line["spans"]:
                            if not span["text"].strip(): continue
                            cursor.setCharFormat(span["char_format"])
                            cursor.insertText(span["text"])
                        cursor.insertText("\n")
                    cursor.insertBlock()

            messagebox.showinfo("Успех", f"PDF-файл {tab_title} успешно открыт!")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def save_as_pdf(self):
        current_widget = self.tab_widget.currentWidget()
        text_edit = current_widget.findChild(QTextEdit)
        if not isinstance(text_edit, QTextEdit): return

        filepath = filedialog.asksaveasfilename(title="Сохранить файл", defaultextension=".pdf",
                                                filetypes=[("PDF файлы", "*.pdf")])
        if not filepath: return

        try:
            printer = QPrinter(QPrinter.HighResolution)
            printer.setOutputFormat(QPrinter.PdfFormat)
            printer.setOutputFileName(filepath)
            printer.setPageSize(QPrinter.A4)
            text_edit.document().print_(printer)
            messagebox.showinfo("Успех", f"Документ сохранён: {filepath}")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def normalize_font_name(self, pdf_font_name):
        patterns = [(r'Regular$', ''), (r'Bold$', ''), (r'Italic$', '')]
        normalized = pdf_font_name
        for p, r in patterns:
            normalized = re.sub(p, r, normalized)
        return normalized.strip()

    def load_font_to_database(self, font_name):
        files = glob.glob('**/*.ttf', recursive=True)
        for file_path in files:
            if font_name == os.path.splitext(os.path.basename(file_path))[0]:
                font_id = QFontDatabase.addApplicationFont(file_path)
                if font_id != -1:
                    families = QFontDatabase.applicationFontFamilies(font_id)
                    return families[0] if families else False
        return False

    def find_matching_font(self, pdf_font_name):
        if pdf_font_name in self.font_cache:
            return self.font_cache[pdf_font_name]

        normalized_name = self.normalize_font_name(pdf_font_name)
        available_fonts = self.font_db.families()

        if normalized_name in available_fonts:
            self.font_cache[pdf_font_name] = normalized_name
            return normalized_name

        for font in available_fonts:
            # ИСПРАВЛЕНО: было pdf_name, стало pdf_font_name
            if normalized_name.lower() in font.lower():
                self.font_cache[pdf_font_name] = font
                return font

        family_name = self.load_font_to_database(normalized_name)
        if family_name:
            return family_name

        self.font_cache[pdf_font_name] = "Arial"
        return "Arial"

    def create_qt_font_from_pdf_span(self, span_data):
        # ДОПИСАНО: завершаем оборванный метод
        pdf_font_name = span_data["font"]
        size = span_data["size"]
        qt_font_name = self.find_matching_font(pdf_font_name)
        qt_font = QFont(qt_font_name, int(size))

        font_lower = pdf_font_name.lower()
        if 'bold' in font_lower:
            qt_font.setBold(True)
        if 'italic' in font_lower:
            qt_font.setItalic(True)

        char_format = QTextCharFormat()
        char_format.setFont(qt_font)

        return qt_font, char_format, qt_font_name

    def analyze_and_map_fonts(self, filepath):
        """Анализирует PDF и сопоставляет шрифты с QFontDatabase."""
        # print('8')
        doc = fitz.open(filepath)
        results = []
        # print('9')
        for page_num in range(doc.page_count):
            page = doc.load_page(page_num)
            text_info = page.get_text("dict")

            page_data = {
                "blocks": []
            }
            # print('10')
            for block in text_info["blocks"]:
                if block["type"] == 0:  # Текстовый блок
                    # print('block', block["bbox"])
                    block_data = {
                        "bbox": block["bbox"],
                        "lines": []
                    }
                    for line in block["lines"]:
                        # print('line', line["bbox"])
                        line_data = {
                            "bbox": line["bbox"],
                            "spans": []
                        }

                        for span in line["spans"]:
                            # print('span', span["bbox"])
                            qt_font, char_format, matched_name = self.create_qt_font_from_pdf_span(span)
                            span_data = {
                                "original_font": span["font"],
                                "matched_qt_font": matched_name,
                                "size": span["size"],
                                "text": span["text"],
                                "qt_font": qt_font,
                                "char_format": char_format,  # Сохраняем формат для использования
                                "bbox": span["bbox"]  # Сохраняем bounding box
                            }

                            line_data["spans"].append(span_data)

                        block_data["lines"].append(line_data)

                    page_data["blocks"].append(block_data)

            results.append(page_data)
        # print('11')
        doc.close()
        return results


    def get_pdf_page_dimensions(self, filepath, page_num=0):
        """Получает размеры конкретной страницы PDF в пикселях."""
        try:
            doc = fitz.open(filepath)
            page = doc.load_page(page_num)
            rect = page.rect
            width = int(rect.width)
            height = int(rect.height)
            doc.close()
            return width, height
        except Exception as e:
            print(f"Ошибка получения размеров страницы: {e}")
            # Возвращаем стандартный A4, если не удалось прочитать PDF
            return self.calculate_pdf_page_size(dpi=96)


    def close_tab(self, index):
        if self.tab_widget.count() > 1:
            self.tab_widget.removeTab(index)
        else:
            messagebox.showerror("Предупреждение", "Нельзя закрыть последнюю вкладку!")


class PDFTextEditor(QMainWindow):
    def __init__(self):
        super().__init__()

        self.configurator = WindowConfigurator()
        self.tab_widget = self.configurator.create_tab_widget(self.configurator.close_tab)
        self.toolbar = QToolBar()

        # Кнопки
        self.font_btn = QPushButton("Выбрать шрифт (системный)")
        self.replace_font_btn = QPushButton("Заменить шрифт из папки")  # НОВАЯ КНОПКА
        self.open_btn = QPushButton("Открыть PDF")
        self.save_btn = QPushButton("Сохранить как PDF")

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Редактор с поддержкой PDF и заменой шрифтов")
        self.setGeometry(100, 100, 1200, 800)

        # Создаём начальную вкладку
        self.configurator.create_new_tab("Новая вкладка")

        # Установка центрального виджета
        self.setCentralWidget(self.configurator.add_layout())

        # Добавление тулбара
        self.addToolBar(self.toolbar)

        # Создание кнопок и привязка функций
        buttons = [
            self.font_btn,
            self.replace_font_btn,  # Подключаем новую функцию
            self.open_btn,
            self.save_btn
        ]

        functions = [
            self.configurator.change_font,
            self.configurator.open_font_folder_dialog,  # Вызывает диалог выбора из папки
            self.configurator.open_pdf,
            self.configurator.save_as_pdf
        ]

        self.configurator.create_elem(self.toolbar, btn=buttons, functions=functions)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Настройка стиля (опционально, чтобы окно выглядело современнее)
    app.setStyle("Fusion")

    window = PDFTextEditor()
    window.show()
    sys.exit(app.exec_())
