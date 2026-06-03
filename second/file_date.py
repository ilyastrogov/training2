# Выведите в консоль даты всех выходных дней текущего
# года в формате год-месяц-день. Создать файл, ввести в него данные.
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.styles import ParagraphStyle

import fitz

import date_day

class StorageData:
    """ Класс для хранения переменных """
    def __init__(self):
        self.date = ''
        self.text = ''
        self.document = ''

class SearchDate(StorageData):
    """ Класс для поиска даты в тексте """
    def search_date(self, text: str) -> str:
        self.date = ''.join(date for date in text.split() if date_day.CheckDate(date).validate_date())
        print(self.date)
        active_date_day = date_day.Result(self.date)
        return active_date_day.active_classes()


class ExtractText(StorageData):
    """ Класс для извлечения текста из PDF файла"""
    def extraction(self, input_filename: str) -> str:
        with fitz.open(input_filename) as doc:
            for page in doc:
                page_text = page.get_text()
                self.text += page_text
        return self.text

class CreateFile(StorageData):
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

class ActiveClasses:
    """ Класс для активации классов """

    @staticmethod
    def activation(file_to_read: str) -> str:
        text = SearchDate().search_date(ExtractText().extraction(file_to_read))
        return f'{WritingText().writing(CreateFile().creation('poluchilos.pdf'), text)}'
""" Активация программы """
a = ActiveClasses()
a.activation('test.pdf')
# activation_create_pdf = CreateFile()
# new_file = activation_create_pdf.creation()
# input_filename = "test.pdf"
# text2 = ExtractText().extraction()
# d = SearchDate()
# text = d.search_date()
# print(text)
# activation_writing = WritingText()
# activation_writing.writing(new_file)

# def extract_text_and_save(input_filename, output_filename):
#     doc = fitz.open(input_filename)
#     extracted_text = ""
#     for page in doc:
#         extracted_text += page.get_text()
#     print(extracted_text)
#     # Сохраняем извлечённый текст в новый PDF-файл
#     # with fitz.open(output_filename, 'wb') as output_file:
#     #     output_file.write(extracted_text.encode('utf-8'))
#     # Открытие PDF-файла
#     with pymupdf.open(output_filename) as pdf:
#         # Доступ к странице (например, к первой)
#         page = pdf
#
#         # Определение текста и позиции
#         text = extracted_text
#         position = pymupdf.Point(100, 200)  # Координаты (x, y) на странице
#
#         # Добавление текста с параметрами (размер шрифта, название шрифта и т. д.)
#         page.insert_text(position, text, fontsize=12, fontname="Helvetica")
#
#         # Сохранение изменённого PDF-файла
#         pdf.save("modified_file.pdf")
#
#  # Пример использования
# input_filename = "output_pymupdf.pdf"  # Исходный PDF-файл
# # output_filename = "hello_world.pdf"    # Новый PDF-файл для сохранения
# extract_text_and_save(input_filename, output_filename)
# # extract_and_save_text(input_filename, output_filename)
