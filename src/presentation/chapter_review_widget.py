import random
from datetime import date
from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QSpinBox, QStackedWidget, QWidget,
)
from PyQt6.QtCore import Qt, QTimer, QRectF, pyqtSignal
from PyQt6.QtGui import QColor, QFont, QPainter, QPen

from src.control.chapter_controller import ChapterController
from src.presentation.dialogs import show_error
import src.presentation.theme as T

_TIMER_SECONDS = 20 * 60  # 20 minutes


class _ProgressRing(QWidget):
    """Circular progress ring showing remaining-time ratio, with question number in the centre."""

    _RING_W = 12
    _SIZE   = 200

    def __init__(self, parent=None):
        super().__init__(parent)
        self._ratio: float = 1.0
        self._text:  str   = ""
        self.setFixedSize(self._SIZE, self._SIZE)

    def set_ratio(self, ratio: float) -> None:
        self._ratio = max(0.0, min(1.0, ratio))
        self.update()

    def set_text(self, text: str) -> None:
        self._text = text
        self.update()

    def paintEvent(self, _event) -> None:
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = h = self._SIZE
        m = self._RING_W // 2 + 3          # margin so ring isn't clipped
        ring_rect = QRectF(m, m, w - 2*m, h - 2*m)

        # ── Background fill ────────────────────────────────────────────
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor(T.SURFACE))
        p.drawEllipse(0, 0, w, h)

        # ── Track (dim full ring) ──────────────────────────────────────
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.setPen(QPen(QColor(T.SURFACE_ALT), self._RING_W,
                      Qt.PenStyle.SolidLine, Qt.PenCapStyle.FlatCap))
        p.drawEllipse(ring_rect)

        # ── Progress arc (gold, remaining ratio) ───────────────────────
        if self._ratio > 0.001:
            p.setPen(QPen(QColor(T.ACCENT_GOLD), self._RING_W,
                          Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
            # start at 12 o'clock (90°), sweep counter-clockwise (positive span)
            p.drawArc(ring_rect,
                      90 * 16,
                      int(self._ratio * 360 * 16))

        # ── Centre text (question number) ──────────────────────────────
        if self._text:
            p.setPen(QPen(QColor(T.TEXT)))
            f = QFont()
            f.setPointSize(60)
            f.setBold(True)
            p.setFont(f)
            p.drawText(QRectF(0, 0, w, h).toRect(),
                       Qt.AlignmentFlag.AlignCenter, self._text)

        p.end()

_RATINGS = [
    ("Again", "again", T.RED),
    ("Hard",  "hard",  T.ORANGE),
    ("Good",  "good",  T.GREEN),
    ("Easy",  "easy",  T.BLUE),
]


class ChapterReviewWidget(QWidget):
    review_completed = pyqtSignal()

    def __init__(self, chapter, chapter_ctrl: ChapterController, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.Window)
        self._chapter = chapter
        self._chapter_ctrl = chapter_ctrl
        self._remaining = _TIMER_SECONDS
        self._paused = False
        self._pool: list[int] = []
        self._pool_idx = 0
        self._drawn_count = 0
        self._n = 10

        self.setWindowTitle(f"章節複習 — {chapter.chapter_name}")
        self.setMinimumSize(440, 380)

        self._timer = QTimer(self)
        self._timer.setInterval(1000)
        self._timer.timeout.connect(self._tick)

        self._build_ui()

    def _build_ui(self) -> None:
        outer = QVBoxLayout(self)
        self._stack = QStackedWidget()
        outer.addWidget(self._stack)
        self._stack.addWidget(self._build_setup_page())
        self._stack.addWidget(self._build_review_page())
        self._stack.addWidget(self._build_rating_page())
        self._stack.setCurrentIndex(0)

    # ── Phase 0: setup ──────────────────────────────────────────────────────

    def _build_setup_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(28, 28, 28, 28)
        layout.setSpacing(16)

        layout.addWidget(QLabel(
            f"<b style='font-size:15px'>{self._chapter.chapter_name}</b>"
        ))

        spin_row = QHBoxLayout()
        spin_row.addWidget(QLabel("這章共有幾題？"))
        self._spin = QSpinBox()
        self._spin.setRange(1, 10000)
        self._spin.setValue(10)
        self._spin.setFixedWidth(80)
        spin_row.addWidget(self._spin)
        spin_row.addStretch()
        layout.addLayout(spin_row)

        layout.addWidget(QLabel("計時：20 分鐘倒數"))
        layout.addStretch()

        start_btn = QPushButton("開始")
        start_btn.setStyleSheet(T.btn_primary(T.GREEN))
        start_btn.clicked.connect(self._start_review)
        layout.addWidget(start_btn)
        return page

    # ── Phase 1: reviewing ──────────────────────────────────────────────────

    def _build_review_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(20, 20, 20, 16)
        layout.setSpacing(0)

        layout.addStretch(1)

        # Timer — centered, 48pt gold
        self._timer_label = QLabel("20:00")
        self._timer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        timer_font = QFont()
        timer_font.setPointSize(48)
        timer_font.setBold(True)
        self._timer_label.setFont(timer_font)
        self._timer_label.setStyleSheet(f"color:{T.ACCENT_GOLD};background:transparent;border:none;")
        layout.addWidget(self._timer_label)

        # Pause button — small, centered, under timer
        self._pause_btn = QPushButton("暫停")
        self._pause_btn.setFixedWidth(80)
        self._pause_btn.setFixedHeight(28)
        self._pause_btn.setStyleSheet(
            f"background:{T.SURFACE_ALT};color:{T.TEXT_SUB};border:none;"
            f"border-radius:4px;font-size:12px;padding:0;"
        )
        self._pause_btn.clicked.connect(self._toggle_pause)
        layout.addWidget(self._pause_btn, alignment=Qt.AlignmentFlag.AlignHCenter)

        layout.addSpacing(24)

        # Progress ring — shows remaining-time ratio + question number
        self._ring = _ProgressRing()
        layout.addWidget(self._ring, alignment=Qt.AlignmentFlag.AlignHCenter)

        layout.addSpacing(20)

        # 抽題 button
        draw_btn = QPushButton("抽　題")
        draw_btn.setStyleSheet(T.btn_primary(T.BLUE))
        draw_btn.setMinimumHeight(52)
        draw_btn.clicked.connect(self._draw_question)
        layout.addWidget(draw_btn)

        # Progress label
        self._progress_label = QLabel("")
        self._progress_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._progress_label.setStyleSheet(
            f"font-size:14px;color:{T.TEXT_MUTED};margin-top:6px;background:transparent;border:none;"
        )
        layout.addWidget(self._progress_label)

        layout.addStretch(1)

        # Bottom: 結束複習 right-aligned
        bottom_row = QHBoxLayout()
        bottom_row.addStretch()
        end_btn = QPushButton("結束複習")
        end_btn.clicked.connect(self._end_review)
        bottom_row.addWidget(end_btn)
        layout.addLayout(bottom_row)

        return page

    # ── Phase 2: rating ─────────────────────────────────────────────────────

    def _build_rating_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(28, 28, 28, 28)
        layout.setSpacing(16)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(
            QLabel("<b style='font-size:16px'>複習完成！</b>"),
            alignment=Qt.AlignmentFlag.AlignCenter,
        )
        layout.addWidget(
            QLabel("請為本次複習評分："),
            alignment=Qt.AlignmentFlag.AlignCenter,
        )
        layout.addSpacing(12)

        btn_row = QHBoxLayout()
        for label, rating, color in _RATINGS:
            btn = QPushButton(label)
            btn.setStyleSheet(T.btn_primary(color))
            btn.clicked.connect(lambda _, r=rating: self._rate(r))
            btn_row.addWidget(btn)
        layout.addLayout(btn_row)
        return page

    # ── Logic ────────────────────────────────────────────────────────────────

    def _start_review(self) -> None:
        self._n = self._spin.value()
        self._remaining = _TIMER_SECONDS
        self._paused = False
        self._pool = list(range(1, self._n + 1))
        random.shuffle(self._pool)
        self._pool_idx = 0
        self._drawn_count = 0
        self._ring.set_ratio(1.0)
        self._ring.set_text("")
        self._progress_label.setText(f"已抽 0 / {self._n} 題")
        self._stack.setCurrentIndex(1)
        self._timer.start()

    def _draw_question(self) -> None:
        if self._pool_idx >= len(self._pool):
            random.shuffle(self._pool)
            self._pool_idx = 0
        num = self._pool[self._pool_idx]
        self._pool_idx += 1
        self._drawn_count += 1
        self._ring.set_text(str(num))
        position = ((self._drawn_count - 1) % self._n) + 1
        self._progress_label.setText(f"已抽 {position} / {self._n} 題")

    def _toggle_pause(self) -> None:
        if self._paused:
            self._timer.start()
            self._paused = False
            self._pause_btn.setText("暫停")
        else:
            self._timer.stop()
            self._paused = True
            self._pause_btn.setText("繼續")

    def _tick(self) -> None:
        self._remaining -= 1
        mins, secs = divmod(self._remaining, 60)
        self._timer_label.setText(f"{mins:02d}:{secs:02d}")
        color = "#FF453A" if self._remaining < 5 * 60 else T.ACCENT_GOLD
        self._timer_label.setStyleSheet(f"color:{color};background:transparent;border:none;")
        self._ring.set_ratio(self._remaining / _TIMER_SECONDS)
        if self._remaining <= 0:
            self._end_review()

    def _end_review(self) -> None:
        self._timer.stop()
        self._stack.setCurrentIndex(2)

    def _rate(self, rating: str) -> None:
        try:
            self._chapter_ctrl.rate_chapter(self._chapter.id, rating, date.today())
        except Exception as e:
            show_error(str(e), self)
        self.review_completed.emit()
        self.close()
