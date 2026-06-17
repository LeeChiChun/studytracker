from datetime import date
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QFormLayout, QComboBox, QLineEdit,
    QDateEdit, QPushButton, QHBoxLayout, QLabel
)
from PyQt6.QtCore import QDate, pyqtSignal

from src.control.chapter_controller import ChapterController
from src.control.settings_controller import SettingsController
from src.presentation.dialogs import DuplicateChapterDialog, show_error, show_info
import src.presentation.theme as T


class AddChapterTab(QWidget):
    chapter_added = pyqtSignal()

    def __init__(self, chapter_ctrl: ChapterController,
                 settings_ctrl: SettingsController, parent=None):
        super().__init__(parent)
        self._chapter_ctrl = chapter_ctrl
        self._settings_ctrl = settings_ctrl
        self._build_ui()

    def _build_ui(self) -> None:
        outer = QVBoxLayout(self)
        outer.setContentsMargins(40, 30, 40, 30)

        outer.addWidget(QLabel("<b style='font-size:16px'>新增章節</b>"))
        outer.addSpacing(12)

        form = QFormLayout()
        form.setSpacing(10)

        self._subject_cb = QComboBox()
        form.addRow("科目：", self._subject_cb)

        self._chapter_no = QLineEdit()
        self._chapter_no.setPlaceholderText("例如 1.1、2.3、A-1")
        form.addRow("章節編號：", self._chapter_no)

        self._chapter_name = QLineEdit()
        self._chapter_name.setPlaceholderText("章節名稱")
        form.addRow("章節名稱：", self._chapter_name)

        self._learned_date = QDateEdit(QDate.currentDate())
        self._learned_date.setCalendarPopup(True)
        self._learned_date.setDisplayFormat("yyyy-MM-dd")
        form.addRow("學習日期：", self._learned_date)

        outer.addLayout(form)
        outer.addSpacing(16)

        btn_row = QHBoxLayout()
        submit_btn = QPushButton("確認新增")
        submit_btn.setStyleSheet(T.btn_primary(T.GREEN))
        submit_btn.clicked.connect(self._submit)
        btn_row.addWidget(submit_btn)

        clear_btn = QPushButton("清空")
        clear_btn.clicked.connect(self._clear)
        btn_row.addWidget(clear_btn)
        btn_row.addStretch()

        outer.addLayout(btn_row)
        outer.addStretch()

    def refresh_subjects(self) -> None:
        current = self._subject_cb.currentText()
        self._subject_cb.clear()
        subjects = self._settings_ctrl.get_subjects()
        for s in subjects:
            self._subject_cb.addItem(s.name)
        idx = self._subject_cb.findText(current)
        if idx >= 0:
            self._subject_cb.setCurrentIndex(idx)

    def _submit(self) -> None:
        subject = self._subject_cb.currentText().strip()
        chapter_no = self._chapter_no.text().strip()
        chapter_name = self._chapter_name.text().strip()
        qd = self._learned_date.date()
        learned = date(qd.year(), qd.month(), qd.day())

        if not chapter_no:
            show_error("章節編號不可空白。", self)
            return
        if not chapter_name:
            show_error("章節名稱不可空白。", self)
            return

        if self._chapter_ctrl.chapter_exists(subject, chapter_no):
            dlg = DuplicateChapterDialog(subject, chapter_no, self)
            if dlg.exec() != DuplicateChapterDialog.DialogCode.Accepted:
                return
            if dlg.choice == "update":
                self._chapter_ctrl.update_chapter(subject, chapter_no, chapter_name, learned)
                show_info("已更新現有資料。", self)
                self.chapter_added.emit()
                return

        self._chapter_ctrl.add_chapter(subject, chapter_no, chapter_name, learned)
        show_info(f"已新增：{subject} {chapter_no} {chapter_name}", self)
        self._clear()
        self.chapter_added.emit()

    def _clear(self) -> None:
        self._chapter_no.clear()
        self._chapter_name.clear()
        self._learned_date.setDate(QDate.currentDate())
