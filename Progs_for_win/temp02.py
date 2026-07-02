import fitz  # PyMuPDF
from PyQt5.QtGui import QFont, QFontDatabase, QTextCharFormat
from PyQt5.QtWidgets import QApplication, QTextEdit, QVBoxLayout, QWidget
import sys
import re

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

def analyze_and_map_fonts(filepath):
    """Анализирует PDF и сопоставляет шрифты с QFontDatabase."""
    doc = fitz.open(filepath)
    mapper = PDFFontMapper()
    results = []

    for page_num in range(doc.page_count):
        page = doc.load_page(page_num)
        text_info = page.get_text("dict")

        page_data = {
            "page_number": page_num + 1,
            "spans": []
        }

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

    doc.close()
    return results

# Основной код с исправленным применением шрифтов
if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Анализируем PDF
    font_mapping = analyze_and_map_fonts("Davay2.pdf")

    # Создаём интерфейс
    window = QWidget()
    layout = QVBoxLayout(window)

    text_edit = QTextEdit()
    layout.addWidget(text_edit)

    cursor = text_edit.textCursor()

    for page in font_mapping:
        cursor.insertText(f"\n--- Страница {page['page_number']} ---\n")

        for span in page["spans"]:
            # Устанавливаем формат перед вставкой текста
            cursor.setCharFormat(span["char_format"])
            cursor.insertText(span["text"])

        # Добавляем перевод строки между страницами
        cursor.insertText("\n")

    window.setWindowTitle("Сопоставление шрифтов PDF ↔ QFontDatabase")
    window.show()

    sys.exit(app.exec_())