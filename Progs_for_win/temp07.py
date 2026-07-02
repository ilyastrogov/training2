import sys
import fitz  # PyMuPDF
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QWidget,
                             QFileDialog, QPushButton, QTabWidget, QTextEdit,
                             QToolBar, QMessageBox, QLabel, QFontComboBox,
                             QComboBox, QSpinBox, QColorDialog, QHBoxLayout,
                             QSizePolicy, QGraphicsScene, QGraphicsView, QGraphicsTextItem)
from PyQt5.QtGui import (QTextCharFormat, QFont, QColor, QFontDatabase,
                        QPageSize, QPainter, QTextDocument, QTextCursor, QPen)
from PyQt5.QtPrintSupport import QPrinter
from PyQt5.QtCore import Qt, QRectF, QPointF

class PDFEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PDF Редактор с полным сохранением макета")
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

        save_btn = QPushButton("Сохранить как PDF")
        save_btn.clicked.connect(self.save_as_pdf_with_styles)
        toolbar.addWidget(save_btn)

        toolbar.addSeparator()

        # Панель управления шрифтами (как в предыдущем коде)
        font_layout = QHBoxLayout()
        font_layout.addWidget(QLabel("Шрифт:"))
        self.font_combo = QFontComboBox()
        self.font_combo.currentFontChanged.connect(self.apply_current_format)
        font_layout.addWidget(self.font_combo)

        font_layout.addWidget(QLabel("Размер:"))
        self.size_spin = QSpinBox()
        self.size_spin.setRange(6, 72)
        self.size_spin.setValue(12)
        self.size_spin.valueChanged.connect(self.apply_current_format)
        font_layout.addWidget(self.size_spin)

        font_layout.addWidget(QLabel("Начертание:"))
        self.style_combo = QComboBox()
        self.style_combo.addItems(["Обычный", "Жирный", "Курсив", "Жирный курсив"])
        self.style_combo.currentTextChanged.connect(self.apply_current_format)
        font_layout.addWidget(self.style_combo)

        font_layout.addWidget(QLabel("Цвет:"))
        self.color_btn = QPushButton("Выбрать цвет")
        self.color_btn.clicked.connect(self.choose_font_color)
        font_layout.addWidget(self.color_btn)

        for item in font_layout.children():
            toolbar.addWidget(item)

        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        main_layout.addWidget(self.tabs)

        self.current_color = QColor(0, 0, 0)  # чёрный по умолчанию

    def open_pdf(self):
        """Открывает PDF через PyMuPDF и загружает в QGraphicsView с сохранением макета"""
        filename, _ = QFileDialog.getOpenFileName(
            self, "Открыть PDF", "", "PDF Files (*.pdf)"
        )
        if filename:
            try:
                with fitz.open(filename) as doc:
                    page_data = doc[0].get_text("dict")  # первая страница
                    editable_widget = self.create_editable_canvas_from_dict(page_data)
                tab_name = filename.split('/')[-1]
                index = self.tabs.addTab(editable_widget, tab_name)
                self.tabs.setCurrentIndex(index)
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось открыть PDF: {e}")

    def create_editable_canvas_from_dict(self, page_data):
        """Создаёт редактируемый холст из данных PDF с сохранением всех отступов и позиций"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Используем QGraphicsView для точного позиционирования
        scene = QGraphicsScene()
        view = QGraphicsView(scene)
        view.setRenderHint(QPainter.Antialiasing)
        view.setDragMode(QGraphicsView.ScrollHandDrag)
        view.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        view.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        # Устанавливаем размер сцены как размер страницы A4 в пикселях (при 96 DPI)
        a4_width_px = 595  # 210 мм * 96/25.4
        a4_height_px = 842  # 297 мм * 96/25.4
        scene.setSceneRect(0, 0, a4_width_px, a4_height_px)

        # Рисуем границы страницы
        scene.addRect(0, 0, a4_width_px, a4_height_px, QPen(Qt.gray))

        # Обрабатываем блоки текста
        for block in page_data["blocks"]:
            if block["type"] == 0:  # текстовый блок
                self.add_text_block_to_scene(scene, block, a4_height_px)

        layout.addWidget(view)
        widget.graphics_view = view
        widget.scene = scene
        return widget

    def add_text_block_to_scene(self, scene, block, page_height):
        """Добавляет текстовый блок на сцену с сохранением позиций"""
        bbox = block["bbox"]  # [x0, y0, x1, y1]

        # Конвертируем координаты PyMuPDF (y вниз) в Qt (y вверх)
        y0_qt = page_height - bbox[3]
        y1_qt = page_height - bbox[1]
        height = y1_qt - y0_qt


        for line in block["lines"]:
            line_bbox = line["bbox"]
            y_line_qt = page_height - line_bbox[3]  # позиция Y строки

            for span in line["spans"]:
                text = span["text"]
                if not text or text.isspace():
                    continue

                # Получаем данные из PDF
                font_name_raw = span.get("font", "Arial")
                font_size = int(span.get("size", 12))
                color_hex = span.get("color", 0)
                flags = span.get("flags", 0)

                # Нормализуем название шрифта для Qt
                font_family = self.normalize_font_name(font_name_raw)

                # Создаём шрифт
                font = QFont(font_family, font_size)

                # Обработка стилей
                if flags & 2:  # жирный
                    font.setWeight(QFont.Bold)
                if flags & 1:  # курсив
                    font.setItalic(True)

                # Обработка цвета
                color = QColor(0, 0, 0)  # чёрный по умолчанию
                if isinstance(color_hex, int) and color_hex != 0:
                    r = (color_hex >> 16) & 0xFF
                    g = (color_hex >> 8) & 0xFF
                    b = color_hex & 0xFF
                    color = QColor(r, g, b)

                # Создаём текстовый элемент
                text_item = QGraphicsTextItem(text)
                text_item.setFont(font)
                text_item.setDefaultTextColor(color)

            # Позиционируем элемент — используем координаты начала строки и текущего span
                span_bbox = span["bbox"]
                x_pos = span_bbox[0]  # координата X из PDF
                y_pos = y_line_qt + (line_bbox[3] - span_bbox[1])  # корректировка по высоте символа

                text_item.setPos(x_pos, y_pos)

                # Добавляем на сцену
                scene.addItem(text_item)

    def normalize_font_name(self, font_name):
        """Нормализует название шрифта для Qt с улучшенной обработкой"""
        # Убираем постфиксы типа "-Bold", "-Italic", "-Regular"
        font_name = font_name.split('-')[0]
        # Удаляем суффиксы типа "MT", "PSMT"
        font_name = font_name.replace("MT", "").replace("PSMT", "")

        font_map = {
            "TimesNewRoman": "Times New Roman",
            "TimesNew": "Times New Roman",
            "Helvetica": "Helvetica",
            "Arial": "Arial",
            "Courier": "Courier",
            "Calibri": "Calibri",
            "Georgia": "Georgia",
            "Verdana": "Verdana",
            "Tahoma": "Tahoma",
            "Trebuchet": "Trebuchet MS",
            "Garamond": "Garamond",
            "Bookman": "Bookman Old Style",
            "Palatino": "Palatino Linotype",
        }

        normalized = font_map.get(font_name, font_name)

        # Проверяем, что шрифт реально существует в системе
        available_fonts = QFontDatabase().families()
        if normalized not in available_fonts:
            # Если не найден, ищем частичное совпадение
            for available in available_fonts:
                if normalized.lower() in available.lower():
                    print(f"Шрифт '{normalized}' не найден. Используем аналог: '{available}'")
                    return available

        print(f"Используем шрифт: {normalized}")
        return normalized

    def apply_current_format(self):
        """Применяет текущий выбранный формат к выделенному тексту в QGraphicsTextItem"""
        current_tab = self.tabs.currentWidget()
        if not current_tab or not hasattr(current_tab, 'scene'):
            return

        scene = current_tab.scene

        # Получаем выделенный элемент (упрощённая логика — в реальности нужно отслеживать выделение)
        selected_items = scene.selectedItems()
        if not selected_items:
            return

        for item in selected_items:
            if isinstance(item, QGraphicsTextItem):
                font = item.font()
                font.setFamily(self.font_combo.currentFont().family())
                font.setPointSize(self.size_spin.value())

                style_text = self.style_combo.currentText()
                if style_text == "Жирный":
                    font.setWeight(QFont.Bold)
                elif style_text == "Курсив":
                    font.setItalic(True)
                elif style_text == "Жирный курсив":
                    font.setWeight(QFont.Bold)
                    font.setItalic(True)
                else:  # "Обычный"
                    font.setWeight(QFont.Normal)
                    font.setItalic(False)

                item.setFont(font)
                item.setDefaultTextColor(self.current_color)

    def choose_font_color(self):
        """Открывает диалог выбора цвета шрифта"""
        color = QColorDialog.getColor(self.current_color, self, "Выберите цвет шрифта")
        if color.isValid():
            self.current_color = color
            self.apply_current_format()

    def save_as_pdf_with_styles(self):
        """Сохраняет текущий редактируемый холст в PDF с сохранением позиций и стилей"""
        current_tab = self.tabs.currentWidget()
        if current_tab and hasattr(current_tab, 'graphics_view'):
            view = current_tab.graphics_view
            scene = current_tab.scene

            filename, _ = QFileDialog.getSaveFileName(
                self, "Сохранить как PDF", "", "PDF Files (*.pdf)"
            )
            if filename:
                try:
                    # Создаём новый PDF документ
                    doc = fitz.open()
                    page = doc.new_page(width=595, height=842)  # A4 в пикселях при 96 DPI

                    # Проходим по всем элементам сцены и добавляем их в PDF
                    for item in scene.items():
                        if isinstance(item, QGraphicsTextItem):
                            text = item.toPlainText()
                            pos = item.pos()
                            font = item.font()

                            # Конвертируем цвет
                            color_rgb = item.defaultTextColor().getRgb()[:3]
                            color_hex = (color_rgb[0] << 16) | (color_rgb[1] << 8) | color_rgb[2]

                            # Добавляем текст в PDF с координатами
                            page.insert_text(
                                (pos.x(), pos.y()),
                                text,
                                fontsize=font.pointSize(),
                                fontname=font.family(),
                                color=color_hex / 0xFFFFFF,  # нормализация цвета для PyMuPDF
                                overlay=True
                            )

                    doc.save(filename)
                    doc.close()
                    QMessageBox.information(self, "Успех", f"Файл сохранён: {filename}")
                except Exception as e:
                    QMessageBox.critical(self, "Ошибка сохранения", f"Не удалось сохранить PDF: {e}")

                else:
                    QMessageBox.warning(self, "Внимание", "Нет активной вкладки для сохранения")


    def close_tab(self, index):
        self.tabs.removeTab(index)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    viewer = PDFEditor()
    viewer.show()
    sys.exit(app.exec_())
