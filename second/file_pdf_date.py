# Выведите в консоль даты всех выходных дней текущего
# года в формате год-месяц-день. Создать файл, ввести в него данные.
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.styles import ParagraphStyle

import fitz

from datetime import date, time, datetime, timedelta
import time
from dateutil.parser import parse

import dateparser

import date_day

class StorageData:
    def __init__(self):
        self.date = ''
        self.text = ''
        # print(self.text)

class SearchDate:
    def zaebalsya(self, date3):
        try:
            parse(date3)
            return True
        except ValueError:
            return False
    def search_date(self):
        date5 = ''.join(date for date in text2.split() if self.zaebalsya(date))
        print(date5)
        active_date_day = date_day.Result(date5)
        return active_date_day.day_week()


class ExtractText(StorageData):
    def extraction(self):

        with fitz.open(input_filename) as doc:
            for page in doc:
                page_text = page.get_text()
                self.text += page_text

        return self.text
class WritingText:
    def writing(self):
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

class CreateFile:

    def creation(self):
        doc = fitz.open()
        doc.new_page()
        output = "new_file.pdf"
        doc.save(filename=output)
        doc.close()
        return output

activation_create_pdf = CreateFile()
new_file = activation_create_pdf.creation()
input_filename = "test.pdf"
text2 = ExtractText().extraction()
d = SearchDate()
text = d.search_date()
print(text)
activation_writing = WritingText()
activation_writing.writing()