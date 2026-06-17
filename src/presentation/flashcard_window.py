from datetime import date
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QKeyEvent

from src.control.review_controller import ReviewController
from src.presentation.dialogs import show_error
import src.presentation.theme as T

_RATING_COLORS = {
    "again": (T.RED,    "Again"),
    "hard":  (T.ORANGE, "Hard"),
    "good":  (T.GREEN,  "Good"),
    "easy":  (T.BLUE,   "Easy"),
}


class FlashcardWindow(QWidget):
    session_finished = pyqtSignal()

    def __init__(self, review_ctrl: ReviewController, parent=None):
        super().__init__(parent)
        self._ctrl = review_ctrl
        self._showing_back = False
        self.setWindowTitle("習習複習習 — 單字複習")
        self.setMinimumSize(600, 420)
        self._build_ui()

    def _build_ui(self) -> None:
        outer = QVBoxLayout(self)
        outer.setContentsMargins(24, 16, 24, 16)
        outer.setSpacing(12)

        # Progress bar
        self._progress_label = QLabel()
        self._progress_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        outer.addWidget(self._progress_label)

        # Card area
        card_frame = QFrame()
        card_frame.setFrameShape(QFrame.Shape.StyledPanel)
        card_frame.setStyleSheet(
            f"background:{T.SURFACE};border:1px solid {T.BORDER};border-radius:8px;"
        )
        card_frame.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        card_layout = QVBoxLayout(card_frame)
        card_layout.setContentsMargins(40, 32, 40, 32)
        card_layout.setSpacing(8)

        card_layout.addStretch(1)

        self._word_label = QLabel()
        self._word_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._word_label.setStyleSheet(
            f"font-size:80pt; font-weight:bold; color:{T.TEXT}; border:none; background:transparent;"
        )
        card_layout.addWidget(self._word_label)

        self._reading_label = QLabel()
        self._reading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        _rf = QFont(); _rf.setPointSize(22)
        self._reading_label.setFont(_rf)
        self._reading_label.setStyleSheet(f"color:{T.TEXT_SUB};background:transparent;")
        card_layout.addWidget(self._reading_label)

        self._meaning_label = QLabel()
        self._meaning_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        _mf = QFont(); _mf.setPointSize(24)
        self._meaning_label.setFont(_mf)
        self._meaning_label.setStyleSheet(f"color:{T.TEXT};background:transparent;")
        self._meaning_label.setWordWrap(True)
        card_layout.addWidget(self._meaning_label)

        self._example_label = QLabel()
        self._example_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        _ef = QFont(); _ef.setPointSize(16)
        self._example_label.setFont(_ef)
        self._example_label.setStyleSheet(f"color:{T.TEXT_MUTED};background:transparent;")
        self._example_label.setWordWrap(True)
        card_layout.addWidget(self._example_label)

        card_layout.addStretch(1)


        outer.addWidget(card_frame, stretch=1)

        # Flip button
        self._flip_btn = QPushButton("翻面（空白鍵）")
        self._flip_btn.setStyleSheet(
            f"background:{T.SURFACE_ALT};color:{T.TEXT};"
            f"padding:10px;border-radius:4px;font-size:14px;border:1px solid {T.BORDER};"
        )
        self._flip_btn.clicked.connect(self._flip)
        outer.addWidget(self._flip_btn)

        # Rating buttons row
        self._rating_row = QHBoxLayout()
        self._rating_btns = {}
        for rating, (color, label) in _RATING_COLORS.items():
            btn = QPushButton()
            btn.setStyleSheet(T.btn_rating(color))
            btn.clicked.connect(lambda _, r=rating: self._rate(r))
            self._rating_row.addWidget(btn)
            self._rating_btns[rating] = (btn, label)
        outer.addLayout(self._rating_row)

        # Done screen
        self._done_widget = QWidget()
        done_layout = QVBoxLayout(self._done_widget)
        done_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._done_label = QLabel()
        self._done_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._done_label.setStyleSheet(f"font-size:22px;font-weight:bold;color:{T.TEXT};")
        done_layout.addWidget(self._done_label)
        back_btn = QPushButton("回到 Dashboard")
        back_btn.setStyleSheet(T.btn_primary(T.GREEN))
        back_btn.clicked.connect(self._on_back)
        done_layout.addWidget(back_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        self._done_widget.setVisible(False)
        outer.addWidget(self._done_widget)

    def start(self, today: date) -> None:
        total = self._ctrl.start_session(today)
        if total == 0:
            self._show_done()
            return
        self._showing_back = False
        self._done_widget.setVisible(False)
        self._show_front()

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key.Key_Space and not self._showing_back:
            self._flip()
        else:
            super().keyPressEvent(event)

    def _show_front(self) -> None:
        vocab = self._ctrl.current_vocab()
        if vocab is None:
            self._show_done()
            return
        self._showing_back = False
        total = self._ctrl.total()
        pos = self._ctrl.current_position()
        self._progress_label.setText(f"{pos} / {total}")

        self._word_label.setText(vocab.word)
        self._reading_label.setText(vocab.reading if vocab.reading else "")
        self._reading_label.setVisible(bool(vocab.reading))
        self._meaning_label.setVisible(False)
        self._example_label.setVisible(False)
        self._flip_btn.setVisible(True)
        self._set_rating_visible(False)

    def _flip(self) -> None:
        vocab = self._ctrl.current_vocab()
        if vocab is None:
            return
        self._showing_back = True
        self._meaning_label.setText(vocab.meaning)
        self._meaning_label.setVisible(True)
        if vocab.example:
            self._example_label.setText(f"例句：{vocab.example}")
            self._example_label.setVisible(True)
        else:
            self._example_label.setVisible(False)

        preview = self._ctrl.get_preview()
        for rating, (btn, label) in self._rating_btns.items():
            next_str = preview.get(rating, "")
            btn.setText(f"{label}\n{next_str}")

        self._flip_btn.setVisible(False)
        self._set_rating_visible(True)
        self._refresh_easy_btn(vocab)

    def _refresh_easy_btn(self, vocab) -> None:
        show = vocab.fsrs_state in ("review", "relearning")
        self._rating_btns["easy"][0].setVisible(show)

    def _set_rating_visible(self, visible: bool) -> None:
        for btn, _ in self._rating_btns.values():
            btn.setVisible(visible)

    def _rate(self, rating: str) -> None:
        try:
            done = self._ctrl.rate_current(rating, date.today())
        except Exception as e:
            show_error(str(e), self)
            return
        if done:
            self._show_done()
        else:
            self._showing_back = False
            self._show_front()

    def _show_done(self) -> None:
        self._word_label.setVisible(False)
        self._reading_label.setVisible(False)
        self._meaning_label.setVisible(False)
        self._example_label.setVisible(False)
        self._flip_btn.setVisible(False)
        self._set_rating_visible(False)
        self._done_label.setText(
            f"今日完成！\n複習了 {self._ctrl.completed_count()} 張"
        )
        self._done_widget.setVisible(True)
        self._progress_label.setText("")

    def _on_back(self) -> None:
        self._word_label.setVisible(True)
        self._done_widget.setVisible(False)
        self.session_finished.emit()
        self.close()
