from datetime import date
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem,
    QPushButton, QLabel, QSpinBox, QDoubleSpinBox, QDialog,
    QFormLayout, QLineEdit, QColorDialog, QGroupBox, QDateEdit,
    QCheckBox, QScrollArea
)
from PyQt6.QtCore import Qt, QDate, pyqtSignal
from PyQt6.QtGui import QColor

from src.control.settings_controller import SettingsController
from src.presentation.dialogs import show_error, show_warning, confirm
import src.presentation.theme as T

_DEFAULT_COLORS = [
    "#4A90D9", "#E67E22", "#27AE60", "#8E44AD",
    "#C0392B", "#16A085", "#2980B9", "#D35400",
    "#F39C12", "#1ABC9C",
]
_used_color_idx = [0]


class AddSubjectDialog(QDialog):
    def __init__(self, existing_names: list[str], parent=None):
        super().__init__(parent)
        self.setWindowTitle("新增科目")
        self.subject_name: str = ""
        self.subject_color: str = _DEFAULT_COLORS[_used_color_idx[0] % len(_DEFAULT_COLORS)]
        self._build_ui(existing_names)

    def _build_ui(self, existing_names: list[str]) -> None:
        layout = QVBoxLayout(self)
        form = QFormLayout()

        self._name_edit = QLineEdit()
        form.addRow("科目名稱：", self._name_edit)

        color_row = QHBoxLayout()
        self._color_btn = QPushButton()
        self._color_btn.setFixedSize(36, 26)
        self._set_color_btn(self.subject_color)
        self._color_btn.clicked.connect(self._pick_color)
        color_row.addWidget(self._color_btn)
        color_row.addWidget(QLabel(self.subject_color))
        self._color_label = color_row.itemAt(1).widget()
        color_row.addStretch()
        form.addRow("顏色：", color_row)

        layout.addLayout(form)

        btn_row = QHBoxLayout()
        ok_btn = QPushButton("確認")
        ok_btn.setStyleSheet(T.btn_small(T.GREEN))
        ok_btn.clicked.connect(lambda: self._confirm(existing_names))
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        btn_row.addWidget(ok_btn)
        btn_row.addWidget(cancel_btn)
        layout.addLayout(btn_row)

    def _set_color_btn(self, color: str) -> None:
        self._color_btn.setStyleSheet(T.btn_swatch(color))
        self.subject_color = color

    def _pick_color(self) -> None:
        color = QColorDialog.getColor(QColor(self.subject_color), self)
        if color.isValid():
            self._set_color_btn(color.name())
            self._color_label.setText(color.name())

    def _confirm(self, existing_names: list[str]) -> None:
        name = self._name_edit.text().strip()
        if not name:
            show_error("科目名稱不可空白。", self)
            return
        if name in existing_names:
            show_error("科目名稱已存在。", self)
            return
        self.subject_name = name
        _used_color_idx[0] += 1
        self.accept()


class SettingsTab(QWidget):
    settings_changed = pyqtSignal()

    def __init__(self, settings_ctrl: SettingsController, parent=None):
        super().__init__(parent)
        self._settings_ctrl = settings_ctrl
        self._build_ui()

    def _build_ui(self) -> None:
        outer = QVBoxLayout(self)
        outer.setContentsMargins(20, 20, 20, 20)
        outer.setSpacing(16)

        # Subject management
        subj_box = QGroupBox("科目管理")
        subj_layout = QVBoxLayout(subj_box)

        self._list = QListWidget()
        subj_layout.addWidget(self._list)

        subj_btn_row = QHBoxLayout()
        self._add_subj_btn = QPushButton("新增科目")
        self._add_subj_btn.setStyleSheet(T.btn_small(T.GREEN))
        self._add_subj_btn.clicked.connect(self._add_subject)
        subj_btn_row.addWidget(self._add_subj_btn)

        self._del_subj_btn = QPushButton("刪除科目")
        self._del_subj_btn.setStyleSheet(T.btn_small(T.RED))
        self._del_subj_btn.clicked.connect(self._delete_subject)
        subj_btn_row.addWidget(self._del_subj_btn)
        subj_btn_row.addStretch()
        subj_layout.addLayout(subj_btn_row)
        outer.addWidget(subj_box)

        # Review settings
        review_box = QGroupBox("複習設定")
        review_form = QFormLayout(review_box)

        self._vocab_limit = QSpinBox()
        self._vocab_limit.setRange(1, 100)
        review_form.addRow("每日新單字上限：", self._vocab_limit)

        self._retention = QDoubleSpinBox()
        self._retention.setRange(0.70, 0.99)
        self._retention.setSingleStep(0.01)
        self._retention.setDecimals(2)
        review_form.addRow("目標保留率：", self._retention)

        save_btn = QPushButton("儲存設定")
        save_btn.setStyleSheet(T.btn_small(T.GREEN))
        save_btn.clicked.connect(self._save_review_settings)
        review_form.addRow("", save_btn)
        outer.addWidget(review_box)

        # Exam dates management
        exam_box = QGroupBox("考試日期管理")
        exam_layout = QVBoxLayout(exam_box)
        self._exam_form = QFormLayout()
        self._exam_form.setSpacing(8)
        self._exam_date_widgets: dict[str, QDateEdit] = {}
        exam_layout.addLayout(self._exam_form)
        save_exam_btn = QPushButton("儲存考試日期")
        save_exam_btn.setStyleSheet(T.btn_small(T.GREEN))
        save_exam_btn.clicked.connect(self._save_exam_dates)
        exam_layout.addWidget(save_exam_btn)
        outer.addWidget(exam_box)
        outer.addStretch()

    def refresh(self) -> None:
        subjects = self._settings_ctrl.get_subjects()
        self._list.clear()
        for s in subjects:
            item = QListWidgetItem(f"  {s.name}")
            item.setBackground(QColor(s.color + "44"))
            item.setData(Qt.ItemDataRole.UserRole, s.id)
            self._list.addItem(item)
        self._del_subj_btn.setEnabled(len(subjects) > 1)

        settings = self._settings_ctrl.get_settings()
        self._vocab_limit.setValue(settings.daily_new_vocab_limit)
        self._retention.setValue(settings.target_retention)

        # Rebuild exam date rows
        while self._exam_form.rowCount() > 0:
            self._exam_form.removeRow(0)
        self._exam_date_widgets.clear()

        exam_dates = settings.exam_dates
        for s in subjects:
            raw = exam_dates.get(s.name, "")
            if raw:
                try:
                    d = date.fromisoformat(raw)
                    qd = QDate(d.year, d.month, d.day)
                except ValueError:
                    qd = QDate.currentDate()
            else:
                qd = QDate(2027, 2, 1)
            de = QDateEdit(qd)
            de.setCalendarPopup(True)
            de.setDisplayFormat("yyyy-MM-dd")
            self._exam_date_widgets[s.name] = de
            self._exam_form.addRow(f"{s.name}：", de)

    def _add_subject(self) -> None:
        existing = [s.name for s in self._settings_ctrl.get_subjects()]
        dlg = AddSubjectDialog(existing, self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self._settings_ctrl.add_subject(dlg.subject_name, dlg.subject_color)
            self.refresh()
            self.settings_changed.emit()

    def _delete_subject(self) -> None:
        item = self._list.currentItem()
        if item is None:
            show_warning("請先選取要刪除的科目。", self)
            return
        subject_id = item.data(Qt.ItemDataRole.UserRole)
        subject_name = item.text().strip()

        subjects = self._settings_ctrl.get_subjects()
        if len(subjects) <= 1:
            show_warning("至少需要保留一個科目。", self)
            return

        if self._settings_ctrl.subject_has_chapters(subject_name):
            ok = confirm(
                f"科目「{subject_name}」含有章節資料，刪除科目後章節資料不會消失，"
                f"但科目名稱將從下拉選單中移除，在 Dashboard 顯示為「(已刪除)」。\n\n確認刪除？",
                self,
            )
            if not ok:
                return

        self._settings_ctrl.delete_subject(subject_id)
        self.refresh()
        self.settings_changed.emit()

    def _save_review_settings(self) -> None:
        self._settings_ctrl.update_review_settings(
            self._vocab_limit.value(),
            self._retention.value(),
        )
        self.settings_changed.emit()
        from src.presentation.dialogs import show_info
        show_info("設定已儲存。", self)

    def _save_exam_dates(self) -> None:
        exam_dates = {}
        for subject_name, de in self._exam_date_widgets.items():
            qd = de.date()
            exam_dates[subject_name] = f"{qd.year()}-{qd.month():02d}-{qd.day():02d}"
        self._settings_ctrl.update_exam_dates(exam_dates)
        self.settings_changed.emit()
        from src.presentation.dialogs import show_info
        show_info("考試日期已儲存。", self)
