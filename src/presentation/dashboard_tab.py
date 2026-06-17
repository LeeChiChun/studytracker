from datetime import date
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QFrame, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QBrush

from src.control.chapter_controller import ChapterController
from src.control.vocab_controller import VocabController
from src.control.settings_controller import SettingsController
from src.presentation.dialogs import show_error
from src.presentation.chapter_review_widget import ChapterReviewWidget
import src.presentation.theme as T


class DashboardTab(QWidget):
    open_flashcard = pyqtSignal()

    def __init__(self, chapter_ctrl: ChapterController,
                 vocab_ctrl: VocabController,
                 settings_ctrl: SettingsController,
                 parent=None):
        super().__init__(parent)
        self._chapter_ctrl = chapter_ctrl
        self._vocab_ctrl = vocab_ctrl
        self._settings_ctrl = settings_ctrl
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        # Header
        self._header_label = QLabel()
        self._header_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        layout.addWidget(self._header_label)

        # Stats bar
        stats_row = QHBoxLayout()
        self._chapter_stat = QLabel()
        self._vocab_stat = QLabel()
        for lbl in (self._chapter_stat, self._vocab_stat):
            lbl.setStyleSheet(
                f"background:{T.STATS_BG};color:{T.TEXT};padding:4px 10px;border-radius:4px;"
            )
            stats_row.addWidget(lbl)
        stats_row.addStretch()
        layout.addLayout(stats_row)

        # Exam countdown bar
        self._exam_bar = QHBoxLayout()
        self._exam_labels: list[QLabel] = []
        layout.addLayout(self._exam_bar)

        # Body: chapters left, vocab right
        body = QHBoxLayout()
        body.setSpacing(12)

        # Chapters panel
        left = QVBoxLayout()
        section_title = QLabel("<b>章節複習清單</b>")
        section_title.setStyleSheet(f"color:{T.TEXT_SUB};font-size:13px;")
        left.addWidget(section_title)
        self._table = QTableWidget()
        self._table.setColumnCount(6)
        self._table.setHorizontalHeaderLabels(
            ["科目", "章節編號", "章節名稱", "上次複習", "間隔天數", "操作"]
        )
        self._table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._table.verticalHeader().setVisible(False)
        left.addWidget(self._table)
        body.addLayout(left, stretch=3)

        # Vocab panel
        right_frame = QFrame()
        right_frame.setFrameShape(QFrame.Shape.StyledPanel)
        right_frame.setStyleSheet(
            f"background:{T.SURFACE};border:1px solid {T.BORDER};border-radius:4px;"
        )
        right_frame.setMaximumWidth(240)
        right_layout = QVBoxLayout(right_frame)
        right_layout.setContentsMargins(12, 12, 12, 12)
        title = QLabel("<b>單字複習</b>")
        title.setStyleSheet(f"color:{T.TEXT_SUB};background:transparent;border:none;")
        right_layout.addWidget(title)
        self._vocab_info = QLabel()
        self._vocab_info.setWordWrap(True)
        self._vocab_info.setStyleSheet(f"color:{T.TEXT};background:transparent;border:none;")
        right_layout.addWidget(self._vocab_info)
        self._new_vocab_quota = QLabel()
        self._new_vocab_quota.setStyleSheet(
            f"color:{T.TEXT_MUTED};font-size:12px;background:transparent;border:none;"
        )
        right_layout.addWidget(self._new_vocab_quota)
        self._start_btn = QPushButton("開始複習")
        self._start_btn.setStyleSheet(T.btn_primary(T.GREEN))
        self._start_btn.clicked.connect(self.open_flashcard.emit)
        right_layout.addWidget(self._start_btn)
        right_layout.addStretch()
        body.addWidget(right_frame, stretch=1)

        layout.addLayout(body)

    def refresh(self) -> None:
        today = date.today()
        today_str = today.strftime("%Y 年 %m 月 %d 日")
        self._header_label.setText(f"今日日期：{today_str}")

        due_chapters = self._chapter_ctrl.get_due_chapters(today)
        due_vocab = self._vocab_ctrl.get_today_vocab_for_review(today)

        self._chapter_stat.setText(f"到期章節：{len(due_chapters)}")
        self._vocab_stat.setText(f"到期單字：{len(due_vocab)}")

        self._refresh_exam_bar(today)
        self._fill_chapter_table(due_chapters, today)

        new_used, limit = self._vocab_ctrl.get_new_vocab_today_count(today)
        self._new_vocab_quota.setText(f"今日新單字：{new_used} / {limit}")

        if due_vocab:
            self._vocab_info.setText(f"今日有 <b>{len(due_vocab)}</b> 張單字卡待複習")
            self._start_btn.setVisible(True)
        else:
            self._vocab_info.setText("今日單字已全部複習完 ✓")
            self._start_btn.setVisible(False)

    def _refresh_exam_bar(self, today: date) -> None:
        # Clear everything (labels + accumulated stretches) to avoid layout drift
        while self._exam_bar.count():
            item = self._exam_bar.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self._exam_labels.clear()

        exam_dates = self._settings_ctrl.get_exam_dates()
        seen: set[date] = set()
        for raw_date in exam_dates.values():
            if not raw_date:
                continue
            try:
                exam_date = date.fromisoformat(raw_date)
            except ValueError:
                continue
            if exam_date in seen:
                continue
            seen.add(exam_date)
            days = (exam_date - today).days
            if days < 0:
                continue
            lbl = QLabel(f"距離研究所考試 {days} 天")
            lbl.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Preferred)
            is_urgent = days < 30
            lbl.setStyleSheet(
                f"background:{T.OVERDUE_BG if is_urgent else T.STATS_BG};"
                f"color:{T.TEXT};"
                f"padding:4px 10px;border-radius:4px;"
                f"{'font-weight:bold;' if is_urgent else ''}"
            )
            self._exam_bar.addWidget(lbl)
            self._exam_labels.append(lbl)
        self._exam_bar.addStretch()

    def _fill_chapter_table(self, chapters, today: date) -> None:
        subject_colors = {
            s.name: s.color for s in self._settings_ctrl.get_subjects()
        }
        today_str = today.isoformat()

        self._table.setRowCount(len(chapters))
        for row, ch in enumerate(chapters):
            is_overdue = ch.next_review < today_str

            # Subject cell with color indicator
            subj_color = subject_colors.get(ch.subject, "#999999")
            subj_label = ch.subject if ch.subject in subject_colors else f"{ch.subject}（已刪除）"
            subj_item = QTableWidgetItem(f"  {subj_label}")
            subj_item.setForeground(
                QBrush(QColor(T.TEXT_MUTED)) if ch.subject not in subject_colors
                else QBrush(QColor(T.TEXT))
            )
            subj_item.setBackground(QBrush(QColor(subj_color + "66")))

            last_review = ch.reviews[-1]["date"] if ch.reviews else ch.learned_date

            items = [
                subj_item,
                QTableWidgetItem(ch.chapter_no),
                QTableWidgetItem(ch.chapter_name),
                QTableWidgetItem(last_review),
                QTableWidgetItem(str(ch.interval_days)),
            ]

            for col, item in enumerate(items):
                # Keep subject color even when overdue; only tint other columns
                if is_overdue and col > 0:
                    item.setBackground(QBrush(QColor(T.OVERDUE_BG)))
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self._table.setItem(row, col, item)

            rate_btn = QPushButton("開始複習")
            rate_btn.setStyleSheet(
                f"background:{T.GREEN};color:#FFFFFF;font-weight:bold;"
                f"padding:2px 10px;border-radius:3px;border:none;"
            )
            rate_btn.clicked.connect(lambda _, c=ch: self._open_review(c))
            self._table.setCellWidget(row, 5, rate_btn)

        self._table.resizeColumnsToContents()
        self._table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)

    def _open_review(self, chapter) -> None:
        dlg = ChapterReviewWidget(chapter, self._chapter_ctrl, self)
        dlg.review_completed.connect(self.refresh)
        dlg.show()
