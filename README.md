# 習習複習習

![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white)
![PyQt6](https://img.shields.io/badge/PyQt6-6.11-41CD52?logo=qt&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-yellow)
![Platform](https://img.shields.io/badge/Platform-macOS-lightgrey?logo=apple)

A macOS desktop app for spaced-repetition vocabulary review and chapter study, built with PyQt6.

- **Vocabulary**: FSRS v6.3.1 algorithm — Again / Hard / Good / Easy scheduling up to 365 days
- **Chapter review**: SM-2 algorithm — random question draw with 30-minute countdown timer
- **Dark luxury theme**: consistent ACCENT_GOLD design across all screens
- **Data stored locally**: `~/Library/Application Support/習習複習習/data/`

---

## Architecture

```mermaid
graph TD
    subgraph PRES[Presentation]
        MW[MainWindow]
        DT[DashboardTab]
        FW[FlashcardWindow]
        CRW[ChapterReviewWidget]
    end

    subgraph CTRL[Control]
        VC[VocabController]
        CC[ChapterController]
        SC[SettingsController]
    end

    subgraph MED[Mediator]
        Cache[SessionCache]
    end

    subgraph ENT[Entity]
        Vocab[Vocab]
        Chapter[Chapter]
        Subject[Subject]
        Settings[SettingsModel]
    end

    subgraph FOUND[Foundation]
        FSRS[fsrs_engine]
        SM2[scheduler]
        Store[json_store]
    end

    PRES --> CTRL
    CTRL --> MED
    CTRL --> ENT
    MED --> FOUND
    FOUND --> ENT
```

---

## Installation

```bash
git clone https://github.com/LeeChiChun/studytracker.git
cd studytracker
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

## Build macOS App

```bash
pyinstaller --windowed --onedir \
  --name "習習複習習" \
  --icon assets/icon.icns \
  main.py
```

---

## Author

李集雋 (Lee Chichun) — [GitHub](https://github.com/LeeChiChun)
