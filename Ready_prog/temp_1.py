import os
from pathlib import Path
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QComboBox, QLabel, QPushButton,
                             QDialogButtonBox, QGroupBox, QHBoxLayout, QSpinBox)
from PyQt5.QtGui import QFont, QFontDatabase, QFontMetrics
from PyQt5.QtWidgets import QApplication
import sys

import os


class CustomFontDialog(QDialog):
    def __init__(self, folder_path, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Выбор шрифта")
        # --- Структура для хранения: семейство -> есть ли Bold ---
        self.families_with_bold = {}

        # --- Загрузка шрифтов из папки ---
        db = QFontDatabase()
        em

        self.loaded_families = list(self.families_with_bold.keys())

        if not self.loaded_families:
            self.reject()
            return

        main_layout = QVBoxLayout()

        # --- Блок: Семейство шрифта ---
        family_group = QGroupBox("Семейство шрифта")
        family_layout = QVBoxLayout()
        family_layout.addWidget(QLabel("Шрифт:"))
        self.combo_family = QComboBox()
        self.combo_family.addItems(self.loaded_families)
        family_layout.addWidget(self.combo_family)
        family_group.setLayout(family_layout)
        main_layout.addWidget(family_group)

        # ГЛАВНОЕ: при смене шрифта в combo_family обновляем варианты стилей
        self.combo_family.currentTextChanged.connect(self._update_style_options)

        # --- Блок: Размер + Начертание ---
        params_group = QGroupBox("Параметры")
        params_layout = QHBoxLayout()

        params_layout.addWidget(QLabel("Размер:"))
        self.spin_size = QSpinBox()
        self.spin_size.setRange(8, 144)
        self.spin_size.setValue(12)
        params_layout.addWidget(self.spin_size)

        params_layout.addSpacing(20)
        params_layout.addWidget(QLabel("Начертание:"))

        self.combo_style = QComboBox()
        # Сразу инициализируем список стилей для первого шрифта в списке
        first_family = self.combo_family.currentText()
        self._update_style_options(first_family)

        params_layout.addWidget(self.combo_style)
        params_group.setLayout(params_layout)
        main_layout.addWidget(params_group)

        # --- Предпросмотр ---
        preview_group = QGroupBox("Предпросмотр")
        preview_layout = QVBoxLayout()
        self.preview_label = QLabel("AaBbCcDdEe FfGgHhIiJj\n0123456789 !@#$%^&*()")
        self.preview_label.setStyleSheet("border: 1px solid #ccc; padding: 8px; background: white;")
        self.preview_label.setMinimumHeight(60)
        self.preview_label.setWordWrap(True)
        preview_layout.addWidget(self.preview_label)
        preview_group.setLayout(preview_layout)
        main_layout.addWidget(preview_group)

        # Обновляем предпросмотр при любых изменениях
        self.combo_family.currentTextChanged.connect(self._update_preview)
        self.spin_size.valueChanged.connect(self._update_preview)
        self.combo_style.currentTextChanged.connect(self._update_preview)

        # Кнопки OK/Cancel
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        main_layout.addWidget(buttons)

        self.setLayout(main_layout)
        self._update_preview()

    def _update_style_options(self, family: str):
        """
        При выборе шрифта проверяет, есть ли у него начертание Bold.
        Если есть — показывает ['Normal', 'Bold'], если нет — только ['Normal'].
        """
        """
                Проверяет, есть ли Bold у семейства, по заранее собранным данным.
                """
        # has_bold = self.families_with_bold.get(family, False)
        print(self.families_with_bold[family])
        has_bold = self.families_with_bold[family]
        self.combo_style.clear()
        if has_bold:
            self.combo_style.addItems(has_bold)
        else:
            self.combo_style.addItem("Normal")

        # Если Bold убрали из списка, а он был выбран — сбрасываем на Normal
        if self.combo_style.currentText() != "Normal" and not has_bold:
            self.combo_style.setCurrentText("Normal")

    def _update_preview(self):
        font_name = self.combo_family.currentText()
        point_size = self.spin_size.value()
        style_text = self.combo_style.currentText()

        f = QFont(font_name, point_size)
        if style_text == "Bold":
            f.setWeight(QFont.Weight.Bold)
        else:
            f.setWeight(QFont.Weight.Normal)

        self.preview_label.setFont(f)

    @staticmethod
    def getFont(folder_path, parent=None):
        dialog = CustomFontDialog(folder_path, parent)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            font_name = dialog.combo_family.currentText()
            point_size = dialog.spin_size.value()
            style_text = dialog.combo_style.currentText()

            font = QFont(font_name, point_size)
            if style_text == "Bold":
                font.setWeight(QFont.Weight.Bold)
            else:
                font.setWeight(QFont.Weight.Normal)
            return font, True
        return QFont(), False


# import os
# # from pathlib import Path
# # from PyQt6.QtWidgets import (
# #     QDialog, QVBoxLayout, QComboBox, QLabel, QPushButton,
# #     QDialogButtonBox, QSpinBox, QGroupBox, QHBoxLayout
# # )
# # from PyQt6.QtGui import QFont, QFontDatabase
#
# class CustomFontDialog(QDialog):
#     def __init__(self, folder_path, parent=None):
#         super().__init__(parent)
#         self.setWindowTitle("Выбор шрифта (папка)")
#         self.selected_font = None
#
#         # 1. Загружаем шрифты только из этой папки
#         self.loaded_families = []
#         db = QFontDatabase()
#         path = Path(folder_path)
#
#         for file in path.iterdir():
#             if file.suffix.lower() in {'.ttf', '.otf'}:
#                 idx = db.addApplicationFont(str(file))
#                 if idx != -1:
#                     families = db.applicationFontFamilies(idx)
#                     self.loaded_families.extend(families)
#
#         # Убираем дубликаты, сохраняя порядок
#         # seen = set()
#         # unique_families = []
#         # for fam in self.loaded_families:
#         #     if fam not in seen:
#         #         seen.add(fam)
#         #         unique_families.append(fam)
#         # self.loaded_families = unique_families
#
#         if not self.loaded_families:
#             # Если шрифтов нет — сразу выходим
#             self.reject()
#             return
#
#         # 2. Создаем UI
#         main_layout = QVBoxLayout()
#
#         # --- Блок выбора семейства ---
#         family_group = QGroupBox("Семейство шрифта")
#         family_layout = QVBoxLayout()
#         lbl_family = QLabel("Выберите шрифт:")
#         self.combo = QComboBox()
#         self.combo.addItems(self.loaded_families)
#         family_layout.addWidget(lbl_family)
#         family_layout.addWidget(self.combo)
#         family_group.setLayout(family_layout)
#         main_layout.addWidget(family_group)
#
#         # --- Блок размера ---
#         size_group = QGroupBox("Размер шрифта")
#         size_layout = QHBoxLayout()
#         lbl_size = QLabel("Размер:")
#         self.spin_size = QSpinBox()
#         self.spin_size.setRange(8, 144)
#         self.spin_size.setValue(12)
#         size_layout.addWidget(lbl_size)
#         size_layout.addWidget(self.spin_size)
#         size_group.setLayout(size_layout)
#         main_layout.addWidget(size_group)
#
#         # Жирность
#         style_group = QGroupBox("Начертание шрифта")
#         style_layout = QHBoxLayout()
#         style_layout.addSpacing(20)
#         style_layout.addWidget(QLabel("Начертание:"))
#         self.combo_style = QComboBox()
#         self.combo_style.addItems(["Normal", "Bold"])
#         style_layout.addWidget(self.combo_style)
#         style_group.setLayout(style_layout)
#         main_layout.addWidget(style_group)
#
#
#         # --- Предпросмотр ---
#         preview_group = QGroupBox("Предпросмотр")
#         preview_layout = QVBoxLayout()
#         self.preview_label = QLabel("AaBbCcDdEe FfGgHhIiJj\n0123456789 !@#$%^&*()")
#         self.preview_label.setStyleSheet("border: 1px solid #ccc; padding: 8px; background: white;")
#         self.preview_label.setMinimumHeight(60)
#         self.preview_label.setWordWrap(True)
#         preview_layout.addWidget(self.preview_label)
#         preview_group.setLayout(preview_layout)
#         main_layout.addWidget(preview_group)
#
#         # Обновляем предпросмотр при изменениях
#         self.combo.currentTextChanged.connect(self._update_preview)
#         self.spin_size.valueChanged.connect(self._update_preview)
#         self.combo_style.currentTextChanged.connect(self._update_preview)
#
#         # Кнопки OK/Cancel
#         buttons = QDialogButtonBox(
#             QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
#         )
#         buttons.accepted.connect(self.accept)
#         buttons.rejected.connect(self.reject)
#         main_layout.addWidget(buttons)
#
#         self.setLayout(main_layout)
#         self._update_preview()  # начальный предпросмотр
#
#     def _update_preview(self):
#         font_name = self.combo.currentText()
#         point_size = self.spin_size.value()
#         style_text = self.combo_style.currentText()
#         f = QFont(font_name)
#         f.setPointSize(point_size)
#         if style_text == "Bold":
#             f.setWeight(QFont.Weight.Bold)
#         else:
#             f.setWeight(QFont.Weight.Normal)
#
#
#         self.preview_label.setFont(f)
#
#     @staticmethod
#     def getFont(folder_path, parent=None):
#         dialog = CustomFontDialog(folder_path, parent)
#         if dialog.exec() == QDialog.DialogCode.Accepted:
#             font_name = dialog.combo.currentText()
#             point_size = dialog.spin_size.value()
#             style_text = dialog.combo_style.currentText()
#             font = QFont(font_name, point_size, style_text)
#             return font, True
#         return QFont(), False
#
#
# # --- ПРИМЕР ИСПОЛЬЗОВАНИЯ ---
# if __name__ == "__main__":
#
#     app = QApplication(sys.argv)
#
#     # Укажите путь к папке со шрифтами
#     my_fonts_folder = "fonts"
#
#     font, ok = CustomFontDialog.getFont(my_fonts_folder)
#     if ok:
#         print(f"Выбран шрифт: {font.family()}, размер: {font.pointSize()}")
#         # Дальше можно применить: some_widget.setFont(font)
#     else:
#         print("Выбор отменён")



#
#
# class CustomFontDialog(QDialog):
#     def __init__(self, folder_path, parent=None):
#         super().__init__(parent)
#         self.setWindowTitle("Выбор шрифта (только из папки)")
#         self.setMinimumSize(300, 200)
#         self.selected_font = None
#
#         # 1. Загружаем шрифты только из этой папки
#         self.loaded_families = []
#         db = QFontDatabase()
#         path = Path(folder_path)
#
#         for file in path.iterdir():
#             if file.suffix.lower() in {'.ttf', '.otf'}:
#                 idx = db.addApplicationFont(str(file))
#                 if idx != -1:
#                     families = db.applicationFontFamilies(idx)
#                     self.loaded_families.extend(families)
#
#         # Убираем дубликаты, сохраняя порядок
#         # seen = set()
#         # unique_families = []
#         # for fam in self.loaded_families:
#         #     if fam not in seen:
#         #         seen.add(fam)
#         #         unique_families.append(fam)
#         # self.loaded_families = unique_families
#
#         # 2. Создаем UI
#         layout = QVBoxLayout()
#
#         lbl = QLabel("Выберите шрифт:")
#         layout.addWidget(lbl)
#
#         self.combo = QComboBox()
#         self.combo.addItems(self.loaded_families)
#         layout.addWidget(self.combo)
#
#         # Предпросмотр
#         self.preview_label = QLabel("AaBbCcDdEe")
#         self.preview_label.setStyleSheet("border: 1px solid gray; padding: 5px;")
#         self.preview_label.setMinimumHeight(40)
#         self._update_preview()
#         self.combo.currentTextChanged.connect(self._update_preview)
#         layout.addWidget(self.preview_label)
#
#         buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
#         buttons.accepted.connect(self.accept)
#         buttons.rejected.connect(self.reject)
#         layout.addWidget(buttons)
#
#         self.setLayout(layout)
#
#     def _update_preview(self):
#         font_name = self.combo.currentText()
#         f = QFont(font_name)
#         f.setPointSize(24)
#         self.preview_label.setFont(f)
#
#     @staticmethod
#     def getFont(folder_path, parent=None):
#         dialog = CustomFontDialog(folder_path, parent)
#         if dialog.exec() == QDialog.DialogCode.Accepted:
#             font_name = dialog.combo.currentText()
#             # Возвращаем QFont. Размер можно задать позже или добавить спинбокс в диалог
#             return QFont(font_name), True
#         return QFont(), False
#
#
# --- ИСПОЛЬЗОВАНИЕ ---
if __name__ == "__main__":

    app = QApplication(sys.argv)

    # Путь к папке с вашими шрифтами
    my_fonts_folder = "fonts"

    font, ok = CustomFontDialog.getFont(my_fonts_folder)
    if ok:
        print(f"Пользователь выбрал: {font.family()}")
        # Применяем шрифт куда нужно
    else:
        print("Выбор отменен")