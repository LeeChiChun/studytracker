from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QDialogButtonBox, QMessageBox
)
from PyQt6.QtCore import Qt
import src.presentation.theme as T


class RatingDialog(QDialog):
    """4-button rating dialog for chapter review."""

    RATINGS = [
        ("Again", "again", T.RED),
        ("Hard",  "hard",  T.ORANGE),
        ("Good",  "good",  T.GREEN),
        ("Easy",  "easy",  T.BLUE),
    ]

    def __init__(self, chapter_name: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle("章節評分")
        self.setMinimumWidth(320)
        self.selected_rating: str | None = None
        self._build_ui(chapter_name)

    def _build_ui(self, chapter_name: str) -> None:
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(f"<b>{chapter_name}</b>"))
        layout.addWidget(QLabel("這次複習感覺如何？"))
        layout.addSpacing(8)

        btn_row = QHBoxLayout()
        for label, rating, color in self.RATINGS:
            btn = QPushButton(label)
            btn.setStyleSheet(T.btn_primary(color))
            btn.clicked.connect(lambda _, r=rating: self._select(r))
            btn_row.addWidget(btn)
        layout.addLayout(btn_row)

        cancel = QPushButton("取消")
        cancel.clicked.connect(self.reject)
        layout.addWidget(cancel)

    def _select(self, rating: str) -> None:
        self.selected_rating = rating
        self.accept()


class DuplicateChapterDialog(QDialog):
    """Ask user to update or cancel when chapter already exists."""

    def __init__(self, subject: str, chapter_no: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle("章節已存在")
        self.choice: str = "cancel"
        self._build_ui(subject, chapter_no)

    def _build_ui(self, subject: str, chapter_no: str) -> None:
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(
            f"<b>{subject} {chapter_no}</b> 已存在。\n要更新現有資料，還是取消？"
        ))
        layout.addSpacing(8)
        btn_row = QHBoxLayout()

        update_btn = QPushButton("更新現有資料")
        update_btn.setStyleSheet(T.btn_small(T.GREEN))
        update_btn.clicked.connect(self._update)
        btn_row.addWidget(update_btn)

        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        btn_row.addWidget(cancel_btn)

        layout.addLayout(btn_row)

    def _update(self) -> None:
        self.choice = "update"
        self.accept()


def show_error(msg: str, parent=None) -> None:
    QMessageBox.critical(parent, "錯誤", msg)


def show_info(msg: str, parent=None) -> None:
    QMessageBox.information(parent, "提示", msg)


def show_warning(msg: str, parent=None) -> None:
    QMessageBox.warning(parent, "警告", msg)


def confirm(msg: str, parent=None) -> bool:
    result = QMessageBox.question(
        parent, "確認", msg,
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        QMessageBox.StandardButton.No,
    )
    return result == QMessageBox.StandardButton.Yes
