from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem,
    QHeaderView, QLabel, QComboBox, QHBoxLayout, QLineEdit, QPushButton
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QBrush, QColor

from src.control.vocab_controller import VocabController


class VocabListTab(QWidget):
    def __init__(self, vocab_ctrl: VocabController, parent=None):
        super().__init__(parent)
        self._vocab_ctrl = vocab_ctrl
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)

        toolbar = QHBoxLayout()
        toolbar.addWidget(QLabel("語言篩選："))
        self._lang_filter = QComboBox()
        self._lang_filter.addItems(["全部", "日文", "英文"])
        self._lang_filter.currentTextChanged.connect(self.refresh)
        toolbar.addWidget(self._lang_filter)

        toolbar.addSpacing(16)
        toolbar.addWidget(QLabel("搜尋："))
        self._search_edit = QLineEdit()
        self._search_edit.setPlaceholderText("輸入單字、讀音或意思...")
        self._search_edit.setMaximumWidth(220)
        self._search_edit.textChanged.connect(self.refresh)
        toolbar.addWidget(self._search_edit)

        self._clear_btn = QPushButton("✕")
        self._clear_btn.setFixedWidth(28)
        self._clear_btn.setToolTip("清除搜尋")
        self._clear_btn.clicked.connect(self._search_edit.clear)
        toolbar.addWidget(self._clear_btn)

        toolbar.addStretch()
        layout.addLayout(toolbar)

        self._table = QTableWidget()
        self._table.setColumnCount(7)
        self._table.setHorizontalHeaderLabels(
            ["語言", "單字", "讀音", "中文意思", "例句", "下次複習", "狀態"]
        )
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._table.verticalHeader().setVisible(False)
        self._table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self._table)

    def refresh(self) -> None:
        lang_filter_map = {"全部": None, "日文": "japanese", "英文": "english"}
        selected_lang = lang_filter_map[self._lang_filter.currentText()]
        query = self._search_edit.text().strip().lower()

        all_vocab = self._vocab_ctrl.get_all_vocab()
        if selected_lang:
            all_vocab = [v for v in all_vocab if v.language == selected_lang]
        if query:
            all_vocab = [
                v for v in all_vocab
                if query in v.word.lower()
                or query in v.reading.lower()
                or query in v.meaning.lower()
            ]

        lang_label = {"japanese": "日文", "english": "英文"}
        state_label = {
            "new": "未複習", "learning": "學習中",
            "review": "複習", "relearning": "重學",
        }

        self._table.setRowCount(len(all_vocab))
        for row, v in enumerate(all_vocab):
            items = [
                QTableWidgetItem(lang_label.get(v.language, v.language)),
                QTableWidgetItem(v.word),
                QTableWidgetItem(v.reading),
                QTableWidgetItem(v.meaning),
                QTableWidgetItem(v.example),
                QTableWidgetItem(v.next_review),
                QTableWidgetItem(state_label.get(v.fsrs_state, v.fsrs_state)),
            ]
            for col, item in enumerate(items):
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self._table.setItem(row, col, item)

        self._table.resizeColumnsToContents()
        self._table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
