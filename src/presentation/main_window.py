from datetime import date
from PyQt6.QtWidgets import QMainWindow, QTabWidget, QMessageBox
from PyQt6.QtCore import Qt

from src.mediator.session_cache import SessionCache
from src.control.chapter_controller import ChapterController
from src.control.vocab_controller import VocabController
from src.control.settings_controller import SettingsController
from src.control.review_controller import ReviewController
from src.presentation.dashboard_tab import DashboardTab
from src.presentation.add_chapter_tab import AddChapterTab
from src.presentation.add_vocab_tab import AddVocabTab
from src.presentation.vocab_list_tab import VocabListTab
from src.presentation.chapter_list_tab import ChapterListTab
from src.presentation.settings_tab import SettingsTab
from src.presentation.flashcard_window import FlashcardWindow


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("習習複習習")
        self.setMinimumSize(900, 600)

        self._cache = SessionCache()
        self._settings_ctrl = SettingsController()
        self._chapter_ctrl = ChapterController(self._cache, self._settings_ctrl)
        self._vocab_ctrl = VocabController(self._cache, self._settings_ctrl)
        self._review_ctrl = ReviewController(self._vocab_ctrl)

        self._flashcard_win: FlashcardWindow | None = None

        self._tabs = QTabWidget()
        self.setCentralWidget(self._tabs)

        self._dashboard = DashboardTab(
            self._chapter_ctrl, self._vocab_ctrl, self._settings_ctrl
        )
        self._add_chapter = AddChapterTab(self._chapter_ctrl, self._settings_ctrl)
        self._add_vocab = AddVocabTab(self._vocab_ctrl)
        self._vocab_list = VocabListTab(self._vocab_ctrl)
        self._chapter_list = ChapterListTab(self._chapter_ctrl, self._settings_ctrl)
        self._settings = SettingsTab(self._settings_ctrl)

        self._tabs.addTab(self._dashboard, "Dashboard")
        self._tabs.addTab(self._add_chapter, "新增章節")
        self._tabs.addTab(self._add_vocab, "新增單字")
        self._tabs.addTab(self._vocab_list, "單字列表")
        self._tabs.addTab(self._chapter_list, "章節列表")
        self._tabs.addTab(self._settings, "設定")

        self._tabs.currentChanged.connect(self._on_tab_changed)
        self._dashboard.open_flashcard.connect(self._open_flashcard)
        self._add_chapter.chapter_added.connect(self._on_data_changed)
        self._add_vocab.vocab_added.connect(self._on_data_changed)
        self._settings.settings_changed.connect(self._on_settings_changed)

        self._dashboard.refresh()
        self._settings.refresh()
        self._add_chapter.refresh_subjects()

    def _on_tab_changed(self, index: int) -> None:
        tab = self._tabs.widget(index)
        if tab is self._dashboard:
            self._dashboard.refresh()
        elif tab is self._add_chapter:
            self._add_chapter.refresh_subjects()
        elif tab is self._vocab_list:
            self._vocab_list.refresh()
        elif tab is self._chapter_list:
            self._chapter_list.refresh()
        elif tab is self._settings:
            self._settings.refresh()

    def _on_data_changed(self) -> None:
        self._cache.invalidate()
        self._dashboard.refresh()
        self._chapter_list.refresh()

    def _on_settings_changed(self) -> None:
        self._cache.invalidate()
        self._add_chapter.refresh_subjects()
        self._dashboard.refresh()

    def _open_flashcard(self) -> None:
        if self._flashcard_win and self._flashcard_win.isVisible():
            self._flashcard_win.raise_()
            return
        self._flashcard_win = FlashcardWindow(self._review_ctrl)
        self._flashcard_win.session_finished.connect(self._on_flashcard_done)
        self._flashcard_win.show()
        self._flashcard_win.start(date.today())

    def _on_flashcard_done(self) -> None:
        self._cache.invalidate()
        self._dashboard.refresh()
        self._vocab_list.refresh()
