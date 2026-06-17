from datetime import date
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem,
    QHeaderView, QPushButton, QDialog, QFormLayout,
    QLineEdit, QDateEdit, QLabel, QHBoxLayout
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QBrush, QColor

from src.control.chapter_controller import ChapterController
from src.control.settings_controller import SettingsController
from src.presentation.dialogs import show_error, show_info
import src.presentation.theme as T


class _EditChapterDialog(QDialog):
    def __init__(self, chapter, parent=None):
        super().__init__(parent)
        self.setWindowTitle("編輯章節")
        self.setMinimumWidth(360)
        self._chapter = chapter
        self.new_chapter_no: str = chapter.chapter_no
        self.new_chapter_name: str = chapter.chapter_name
        self.new_learned_date: date = date.fromisoformat(chapter.learned_date)
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        form = QFormLayout()
        form.setSpacing(10)

        self._no_edit = QLineEdit(self._chapter.chapter_no)
        form.addRow("章節編號：", self._no_edit)

        self._name_edit = QLineEdit(self._chapter.chapter_name)
        form.addRow("章節名稱：", self._name_edit)

        ld = date.fromisoformat(self._chapter.learned_date)
        self._date_edit = QDateEdit(QDate(ld.year, ld.month, ld.day))
        self._date_edit.setCalendarPopup(True)
        self._date_edit.setDisplayFormat("yyyy-MM-dd")
        form.addRow("學習日期：", self._date_edit)

        nr_label = QLabel(self._chapter.next_review)
        nr_label.setStyleSheet(f"color:{T.TEXT_MUTED};")
        form.addRow("下次複習（唯讀）：", nr_label)

        iv_label = QLabel(str(self._chapter.interval_days) + " 天")
        iv_label.setStyleSheet(f"color:{T.TEXT_MUTED};")
        form.addRow("間隔天數（唯讀）：", iv_label)

        layout.addLayout(form)
        layout.addSpacing(12)

        btn_row = QHBoxLayout()
        save_btn = QPushButton("儲存")
        save_btn.setStyleSheet(T.btn_small(T.GREEN))
        save_btn.clicked.connect(self._save)
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        btn_row.addWidget(save_btn)
        btn_row.addWidget(cancel_btn)
        layout.addLayout(btn_row)

    def _save(self) -> None:
        no = self._no_edit.text().strip()
        name = self._name_edit.text().strip()
        if not no:
            show_error("章節編號不可空白。", self)
            return
        if not name:
            show_error("章節名稱不可空白。", self)
            return
        self.new_chapter_no = no
        self.new_chapter_name = name
        qd = self._date_edit.date()
        self.new_learned_date = date(qd.year(), qd.month(), qd.day())
        self.accept()


class ChapterListTab(QWidget):
    def __init__(self, chapter_ctrl: ChapterController,
                 settings_ctrl: SettingsController, parent=None):
        super().__init__(parent)
        self._chapter_ctrl = chapter_ctrl
        self._settings_ctrl = settings_ctrl
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)

        self._table = QTableWidget()
        self._table.setColumnCount(7)
        self._table.setHorizontalHeaderLabels(
            ["科目", "章節編號", "章節名稱", "學習日期", "下次複習", "間隔天數", "操作"]
        )
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._table.verticalHeader().setVisible(False)
        self._table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self._table)

    def refresh(self) -> None:
        chapters = self._chapter_ctrl.get_all_chapters()
        subject_colors = {s.name: s.color for s in self._settings_ctrl.get_subjects()}

        self._table.setRowCount(len(chapters))
        for row, ch in enumerate(chapters):
            subj_color = subject_colors.get(ch.subject, "#999999")
            subj_label = ch.subject if ch.subject in subject_colors else f"{ch.subject}（已刪除）"
            subj_item = QTableWidgetItem(f"  {subj_label}")
            subj_item.setBackground(QBrush(QColor(subj_color + "33")))
            if ch.subject not in subject_colors:
                subj_item.setForeground(QBrush(QColor(T.TEXT_MUTED)))

            items = [
                subj_item,
                QTableWidgetItem(ch.chapter_no),
                QTableWidgetItem(ch.chapter_name),
                QTableWidgetItem(ch.learned_date),
                QTableWidgetItem(ch.next_review),
                QTableWidgetItem(str(ch.interval_days)),
            ]
            for col, item in enumerate(items):
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self._table.setItem(row, col, item)

            edit_btn = QPushButton("編輯")
            edit_btn.setStyleSheet(
                f"background:{T.BLUE};color:#FFFFFF;font-weight:bold;"
                f"padding:2px 10px;border-radius:3px;border:none;"
            )
            edit_btn.clicked.connect(lambda _, c=ch: self._open_edit(c))
            self._table.setCellWidget(row, 6, edit_btn)

        self._table.resizeColumnsToContents()
        self._table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)

    def _open_edit(self, chapter) -> None:
        dlg = _EditChapterDialog(chapter, self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            try:
                self._chapter_ctrl.edit_chapter(
                    chapter.id,
                    dlg.new_chapter_no,
                    dlg.new_chapter_name,
                    dlg.new_learned_date,
                )
                self.refresh()
            except Exception as e:
                show_error(str(e), self)
