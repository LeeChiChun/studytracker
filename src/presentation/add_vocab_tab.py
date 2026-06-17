import urllib.parse
import requests
from datetime import date
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QFormLayout, QComboBox, QLineEdit,
    QDateEdit, QPushButton, QHBoxLayout, QLabel, QTextEdit, QCompleter,
)
from PyQt6.QtCore import QDate, QThread, pyqtSignal, Qt

from src.control.vocab_controller import VocabController
from src.presentation.dialogs import show_error, show_info
import src.presentation.theme as T

_LANG_MAP = {"日文": "japanese", "英文": "english"}

_POS_ZH = {
    "noun": "名詞", "verb": "動詞", "adjective": "形容詞",
    "adverb": "副詞", "pronoun": "代名詞", "preposition": "介系詞",
    "conjunction": "連接詞", "interjection": "感嘆詞",
    "exclamation": "感嘆詞", "determiner": "限定詞",
}

_MAX_DEFINITIONS = 6


class _LookupThread(QThread):
    result_ready = pyqtSignal(str, str, str)   # reading, meaning, example
    error = pyqtSignal(str)

    def __init__(self, language: str, word: str):
        super().__init__()
        self._language = language
        self._word = word

    def run(self) -> None:
        try:
            if self._language == "english":
                self._lookup_en()
            else:
                self._lookup_jp()
        except Exception as e:
            self.error.emit(str(e))

    def _translate_to_zh(self, text: str) -> str:
        if not text:
            return text
        try:
            r = requests.get(
                "https://translate.googleapis.com/translate_a/single",
                params={"client": "gtx", "sl": "en", "tl": "zh-TW", "dt": "t", "q": text},
                headers={"User-Agent": "Mozilla/5.0"},
                timeout=8,
            )
            data = r.json()
            return "".join(part[0] for part in data[0] if part[0])
        except Exception:
            return ""

    def _lookup_en(self) -> None:
        r = requests.get(
            f"https://api.dictionaryapi.dev/api/v2/entries/en/{urllib.parse.quote(self._word)}",
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=8,
        )
        r.raise_for_status()
        data = r.json()
        meanings = data[0].get("meanings", [])

        lines = []
        for meaning in meanings:
            pos = _POS_ZH.get(meaning.get("partOfSpeech", ""), meaning.get("partOfSpeech", ""))
            for defn in meaning.get("definitions", [])[:2]:
                if len(lines) >= _MAX_DEFINITIONS:
                    break
                definition_text = defn.get("definition", "")
                if not definition_text:
                    continue
                line = f"[{pos}] {definition_text}"
                example = defn.get("example", "")
                if example:
                    line += f" — {example}"
                lines.append(line)
            if len(lines) >= _MAX_DEFINITIONS:
                break

        if not lines:
            self.error.emit("查無定義")
            return

        example_text = "\n".join(lines)
        meaning_zh = self._translate_to_zh(self._word)
        self.result_ready.emit("", meaning_zh, example_text)

    def _lookup_jp(self) -> None:
        r = requests.get(
            f"https://jisho.org/api/v1/search/words?keyword={urllib.parse.quote(self._word)}",
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=8,
        )
        r.raise_for_status()
        data = r.json()
        items = data.get("data", [])
        if not items:
            self.error.emit("查無結果")
            return
        jp = items[0].get("japanese", [{}])
        reading = jp[0].get("reading", "") if jp else ""
        senses = items[0].get("senses", [{}])
        en_defs = senses[0].get("english_definitions", []) if senses else []
        zh_meaning = self._translate_to_zh("；".join(en_defs[:3]))
        example = self._fetch_jp_example()
        self.result_ready.emit(reading, zh_meaning, example)

    def _fetch_jp_example(self) -> str:
        try:
            r = requests.get(
                "https://tatoeba.org/api_v0/search",
                params={"query": self._word, "from": "jpn", "limit": 1},
                headers={"User-Agent": "Mozilla/5.0"},
                timeout=8,
            )
            results = r.json().get("results", [])
            return results[0].get("text", "") if results else ""
        except Exception:
            return ""


class AddVocabTab(QWidget):
    vocab_added = pyqtSignal()

    def __init__(self, vocab_ctrl: VocabController, parent=None):
        super().__init__(parent)
        self._vocab_ctrl = vocab_ctrl
        self._lookup_thread: _LookupThread | None = None
        self._build_ui()

    def _build_ui(self) -> None:
        outer = QVBoxLayout(self)
        outer.setContentsMargins(40, 30, 40, 30)

        outer.addWidget(QLabel("<b style='font-size:16px'>新增單字</b>"))
        outer.addSpacing(12)

        form = QFormLayout()
        form.setSpacing(10)

        self._lang_cb = QComboBox()
        self._lang_cb.addItems(["英文", "日文"])
        self._lang_cb.currentTextChanged.connect(self._on_lang_changed)
        form.addRow("語言：", self._lang_cb)

        word_row = QHBoxLayout()
        self._word_edit = QLineEdit()
        self._word_edit.setPlaceholderText("單字")
        word_row.addWidget(self._word_edit)
        self._lookup_btn = QPushButton("查詢")
        self._lookup_btn.setStyleSheet(T.btn_small(T.BLUE))
        self._lookup_btn.setFixedWidth(60)
        self._lookup_btn.clicked.connect(self._lookup)
        word_row.addWidget(self._lookup_btn)
        form.addRow("單字：", word_row)

        self._lookup_status = QLabel("")
        self._lookup_status.setStyleSheet(f"color:{T.TEXT_MUTED};font-size:12px;")
        form.addRow("", self._lookup_status)

        self._reading_label = QLabel("讀音：")
        self._reading_edit = QLineEdit()
        self._reading_edit.setPlaceholderText("ひらがな / ふりがな")
        form.addRow(self._reading_label, self._reading_edit)

        self._meaning_edit = QTextEdit()
        self._meaning_edit.setPlaceholderText("中文意思（必填）")
        self._meaning_edit.setFixedHeight(60)
        self._meaning_edit.setAcceptRichText(False)
        form.addRow("中文意思：", self._meaning_edit)

        self._example_edit = QTextEdit()
        self._example_edit.setPlaceholderText("例句（選填）")
        self._example_edit.setFixedHeight(120)
        self._example_edit.setAcceptRichText(False)
        form.addRow("例句：", self._example_edit)

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

        continue_btn = QPushButton("繼續新增")
        continue_btn.clicked.connect(self._submit_and_continue)
        btn_row.addWidget(continue_btn)

        cancel_btn = QPushButton("清空")
        cancel_btn.clicked.connect(self._clear_fields)
        btn_row.addWidget(cancel_btn)
        btn_row.addStretch()

        outer.addLayout(btn_row)
        outer.addStretch()

        self._on_lang_changed("英文")
        self._refresh_completer()

    def _refresh_completer(self) -> None:
        words = [v.word for v in self._vocab_ctrl.get_all_vocab()]
        completer = QCompleter(words, self)
        completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self._word_edit.setCompleter(completer)

    def _on_lang_changed(self, lang: str) -> None:
        is_jp = lang == "日文"
        self._reading_label.setVisible(is_jp)
        self._reading_edit.setVisible(is_jp)
        self._lookup_status.setText("")

    def _lookup(self) -> None:
        word = self._word_edit.text().strip()
        if not word:
            self._lookup_status.setText("請先輸入單字")
            return
        if self._lookup_thread and self._lookup_thread.isRunning():
            return
        language = _LANG_MAP[self._lang_cb.currentText()]
        self._lookup_status.setText("查詢中…")
        self._lookup_btn.setEnabled(False)
        self._lookup_thread = _LookupThread(language, word)
        self._lookup_thread.result_ready.connect(self._on_lookup_result)
        self._lookup_thread.error.connect(self._on_lookup_error)
        self._lookup_thread.finished.connect(lambda: self._lookup_btn.setEnabled(True))
        self._lookup_thread.start()

    def _on_lookup_result(self, reading: str, meaning: str, example: str) -> None:
        if reading:
            self._reading_edit.setText(reading)
        if meaning:
            self._meaning_edit.setPlainText(meaning)
        if example:
            self._example_edit.setPlainText(example)
        self._lookup_status.setText("✓ 已自動填入，可手動修改")

    def _on_lookup_error(self, msg: str) -> None:
        self._lookup_status.setText(f"查詢失敗：{msg}")

    def _collect_fields(self) -> dict | None:
        language = _LANG_MAP[self._lang_cb.currentText()]
        word = self._word_edit.text().strip()
        reading = self._reading_edit.text().strip() if language == "japanese" else ""
        meaning = self._meaning_edit.toPlainText().strip()
        example = self._example_edit.toPlainText().strip()
        qd = self._learned_date.date()
        learned = date(qd.year(), qd.month(), qd.day())

        if not word:
            show_error("單字不可空白。", self)
            return None
        if not meaning:
            show_error("中文意思不可空白。", self)
            return None
        for v in self._vocab_ctrl.get_all_vocab():
            if v.language == language and v.word.lower() == word.lower():
                show_error(f"『{word}』已在單字庫中", self)
                return None
        return dict(language=language, word=word, reading=reading,
                    meaning=meaning, example=example, learned_date=learned)

    def _submit(self) -> None:
        fields = self._collect_fields()
        if fields is None:
            return
        self._vocab_ctrl.add_vocab(**fields)
        show_info(f"已新增：{fields['word']}", self)
        self._clear_fields()
        self._refresh_completer()
        self.vocab_added.emit()

    def _submit_and_continue(self) -> None:
        fields = self._collect_fields()
        if fields is None:
            return
        lang = self._lang_cb.currentText()
        self._vocab_ctrl.add_vocab(**fields)
        self._clear_fields()
        self._lang_cb.setCurrentText(lang)
        self._refresh_completer()
        self.vocab_added.emit()

    def _clear_fields(self) -> None:
        self._word_edit.clear()
        self._reading_edit.clear()
        self._meaning_edit.clear()
        self._example_edit.clear()
        self._learned_date.setDate(QDate.currentDate())
        self._lookup_status.setText("")
