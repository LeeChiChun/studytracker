# 習習複習習 (StudyTracker) — PROJECT.md

## 專案概覽

| 項目 | 內容 |
|------|------|
| 平台 | Python 桌面 App（PyQt6） |
| 根目錄 | `~/Desktop/習習複習習/` |
| 原始碼 | `~/Desktop/習習複習習/src/` |
| 資料目錄 | `~/Library/Application Support/習習複習習/data/` |
| 編譯後 App | `~/Desktop/習習複習習.app` |
| 進入點 | `~/Desktop/習習複習習/main.py` |
| Python venv | `~/Desktop/習習複習習/venv/` （Python 3.13） |

## 常用指令

```bash
# 進入 venv
cd ~/Desktop/習習複習習 && source venv/bin/activate

# 直接執行（開發用，不需 rebuild）
cd ~/Desktop/習習複習習 && source venv/bin/activate && python main.py

# 重新建置 .app 並部署到 Desktop
cd ~/Desktop/習習複習習 && source venv/bin/activate && \
  pyinstaller --windowed --name "習習複習習" --onedir --noconfirm main.py && \
  mv ~/Desktop/習習複習習.app ~/.Trash/ 2>/dev/null && \
  cp -R dist/習習複習習.app ~/Desktop/習習複習習.app
```

> **注意**：直接修改 `src/` 原始碼後，執行 `python main.py` 即可測試，不需 rebuild。
> 確認沒問題後才需要 rebuild `.app`。

## 專案結構

```
~/Desktop/習習複習習/
├── main.py                          # 進入點：啟動 QApplication + MainWindow
├── PROJECT.md                       # 本文件
├── data/
│   ├── settings.json                # 科目清單、每日上限、考試日期
│   ├── chapters.json                # 所有章節資料
│   ├── vocab.json                   # 所有單字資料
│   └── backup/                      # 每次寫入前自動備份
└── src/
    ├── entity/
    │   ├── chapter.py               # Chapter dataclass
    │   ├── vocab.py                 # Vocab dataclass
    │   ├── subject.py               # Subject dataclass
    │   └── settings_model.py        # Settings dataclass（含 exam_dates）
    ├── foundation/
    │   ├── json_store.py            # 唯一與 JSON 檔案讀寫的層
    │   ├── scheduler.py             # SM-2 演算法（章節層）
    │   └── fsrs_engine.py           # FSRS v4 演算法（單字層）
    ├── mediator/
    │   └── session_cache.py         # 記憶體快取（due_chapters）
    ├── control/
    │   ├── chapter_controller.py    # 章節 CRUD + 評分 + exam_date cap
    │   ├── vocab_controller.py      # 單字 CRUD + 每日上限
    │   ├── review_controller.py     # 字卡複習 session 管理
    │   └── settings_controller.py   # 科目管理 + 複習設定 + 考試日期
    └── presentation/
        ├── main_window.py           # QMainWindow + QTabWidget（6 個 Tab）
        ├── theme.py                 # 全域 QSS 主題（和風配色）
        ├── dashboard_tab.py         # Tab 1：今日到期清單 + 考試倒數
        ├── add_chapter_tab.py       # Tab 2：新增章節
        ├── add_vocab_tab.py         # Tab 3：新增單字（含字典查詢）
        ├── vocab_list_tab.py        # Tab 4：單字列表
        ├── chapter_list_tab.py      # Tab 5：章節列表（可編輯）
        ├── settings_tab.py          # Tab 6：科目管理 + 複習設定 + 考試日期
        ├── flashcard_window.py      # 字卡複習視窗（獨立 Widget）
        └── dialogs.py               # RatingDialog、DuplicateChapterDialog、helpers
```

## 各檔案職責

| 檔案 | 職責 |
|------|------|
| `main.py` | QApplication 初始化、套用主題、顯示 MainWindow |
| `json_store.py` | 讀寫 settings / chapters / vocab JSON，寫入前自動備份 |
| `scheduler.py` | SM-2：apply_sm2（含考試日期 cap）、initial_chapter_schedule |
| `fsrs_engine.py` | FSRS v4：apply_fsrs、get_fsrs_preview（含 365 cap、學習階段分鐘顯示）|
| `session_cache.py` | 快取 due_chapters，invalidate() 清空 |
| `chapter_controller.py` | get_due / get_all / add / update / edit / rate_chapter（傳 exam_date）|
| `vocab_controller.py` | get_all / get_today_for_review / add_vocab（每日上限）|
| `review_controller.py` | 字卡 session：start / current / rate_current / get_preview |
| `settings_controller.py` | get_settings / add_subject / delete_subject / update_review_settings / update_exam_dates |
| `main_window.py` | 組裝 6 個 Tab，處理 tab_changed / data_changed / flashcard 開關 |
| `dashboard_tab.py` | 章節複習表格（評分按鈕）+ 單字複習面板 + 考試倒數 bar |
| `add_vocab_tab.py` | 新增單字表單 + 字典查詢（QThread 非同步）|
| `chapter_list_tab.py` | 所有章節表格 + 編輯 Dialog（chapter_no / name / learned_date 可改）|
| `settings_tab.py` | 科目 CRUD + 複習設定 + 考試日期管理（每科 QDateEdit）|
| `flashcard_window.py` | 翻面流程 + 4 鍵評分 + preview 標示 |
| `dialogs.py` | RatingDialog、DuplicateChapterDialog、show_error/info/warning/confirm |

## 資料模型

### settings.json
```json
{
  "subjects": [{"id": "s-001", "name": "線性代數", "color": "#4A90D9"}],
  "daily_new_vocab_limit": 20,
  "target_retention": 0.90,
  "fsrs_weights": [],
  "exam_dates": {"線性代數": "2027-02-01"}
}
```

### chapters.json 單筆
```json
{
  "id": "uuid", "subject": "線性代數", "chapter_no": "1.1",
  "chapter_name": "矩陣基本代數運算", "learned_date": "2026-05-15",
  "reviews": [{"date": "2026-05-16", "rating": "good"}],
  "next_review": "2026-05-23", "interval_days": 7, "ease": 2.5
}
```

### vocab.json 單筆
```json
{
  "id": "uuid", "language": "japanese", "word": "勉強",
  "reading": "べんきょう", "meaning": "讀書；學習", "example": "...",
  "learned_date": "2026-05-15",
  "reviews": [{"date": "2026-05-16", "rating": "good"}],
  "next_review": "2026-05-20", "fsrs_state": "review",
  "fsrs_stability": 4.07, "fsrs_difficulty": 5.0, "fsrs_due": "2026-05-20"
}
```

## 已完成功能

- [x] M1 章節管理：新增、評分（SM-2）、重複登記警告（完成於 2026-05）
- [x] M2 單字管理：新增英文／日文單字，每日上限（完成於 2026-05）
- [x] M3 排程引擎：SM-2（章節）+ FSRS v4（單字）（完成於 2026-05）
- [x] M4 Dashboard：今日到期清單、overdue 標紅（完成於 2026-05）
- [x] M5 字卡複習 UI：翻面、4 鍵評分、preview 標示（完成於 2026-05）
- [x] M6 科目管理：新增／刪除科目、動態色塊（完成於 2026-05）
- [x] M7 資料 I/O：JSON 讀寫 + 自動備份（完成於 2026-05）
- [x] M8 章節列表 Tab：瀏覽所有章節、行內編輯（v1.1，完成於 2026-05-23）
- [x] M9 字典查詢：新增單字時查詢 EN/JP API 自動填入、中文翻譯、例句抓取（v1.2，完成於 2026-05-24）
- [x] M10 考試模式：考試日期管理 UI、interval cap、Dashboard 倒數（v1.1，完成於 2026-05-23）
- [x] FSRS bug fix：last_review=None 修正（5000天bug）、cap 180天、learning_steps=[1min,1day]、fsrs_due 改存 UTC datetime、時間鎖篩選（v1.3，完成於 2026-05-28）
- [x] 字卡字體：單字 48px、讀音 24px、意思 28px、例句 18px（v1.1，完成於 2026-05-23）

## 尚未完成 / 已知問題

- [ ] 字典查詢：中文翻譯來自 Google Translate 非官方 API，偶爾可能 timeout（已有 fallback 回英文）
- [ ] 考試模式：英文／日文科目無考試日期，不受 interval cap 影響（符合設計，但未來可能需要）
- [ ] 統計頁面：無歷史複習紀錄圖表
- [ ] 匯出功能：無 CSV / Anki 匯出

## 版本紀錄

| 版本 | 日期 | 摘要 |
|------|------|------|
| v1.0 | 2026-05 | 初版：M1–M7 全部完成 |
| v1.1 | 2026-05-23 | M8 章節列表、M9 字典查詢、M10 考試模式、FSRS bug fix、字體調整 |
| v1.2 | 2026-05-24 | 字典中文翻譯、例句抓取、Dashboard 考試倒數合併為一個、字典 403 修正 |
| v1.3 | 2026-05-28 | FSRS last_review bug 修正、cap 180天、時間鎖、字卡字體調整 |
| v1.4 | 2026-05-29 | 排程引擎重寫（時區修正、SM-2 cap）、Easy 按鈕隱藏、Dashboard 色塊、新單字配額顯示 |
| v1.5 | 2026-05-29 | 專案目錄搬移：`~/.studytracker/` → `~/Desktop/習習複習習/`，venv 重建 |
