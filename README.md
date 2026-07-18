# 🌐 Searcher Browser

**Searcher** is a powerful, modern, and lightweight desktop web browser built with Python and PyQt6. Designed with speed, security, and productivity in mind, it offers a sleek user interface and a suite of advanced features, including a built-in AI Assistant, robust Ad Blocker, and a secure Password Manager.

---

## 📖 About the Browser

Searcher Browser is a fully functional desktop web browser created as an open-source project. It is built from scratch using Python and the Chromium-based PyQt6-WebEngine rendering engine. The goal of this project is to provide a fast, private, and feature-rich browsing experience — all packaged into a single portable executable that requires no installation.

Whether you want a secondary browser for privacy, a developer tool for testing, or just a lightweight alternative to Chrome/Edge, Searcher Browser has you covered.

---

## 🛠️ Technologies Used

| Technology | Purpose |
|---|---|
| **Python 3.12+** | Core programming language powering all browser logic |
| **PyQt6** | Cross-platform GUI framework for building the desktop interface |
| **PyQt6-WebEngine** | Chromium-based web rendering engine for displaying web pages |
| **SQLite** | Local database for storing history, bookmarks, and passwords |
| **JSON** | Configuration and settings storage |
| **HTML/CSS/JS** | Custom start page, error page, and offline page |
| **PyInstaller** | Packaging the app into a single standalone `.exe` file |

---

## 📥 Download Searcher Browser

> **No installation required!** Just download and double-click to run.

### 🔗 [Download Searcher Browser (Windows)](https://github.com/Amit123103/Searcher_browser/releases/tag/latest1)

Click the link above to go to the releases page and download the latest `.exe` file.

---

## 🚀 How to Use the Browser

1. **Download** — Click the download link above and download the `Searcher.exe` file from the releases page.
2. **Run** — Double-click the downloaded `Searcher.exe` file. No installation, no zip extraction, no Python or dependencies required.
3. **Browse** — The browser opens with a custom start page. Use the address bar at the top to search the web or type any URL.
4. **Open New Tabs** — Click the `+` button next to the tabs to open a new tab, just like any modern browser.
5. **Use AI Assistant** — Click the AI icon in the toolbar to open the AI sidebar. You can summarize pages, ask questions, and generate notes.
6. **Manage Bookmarks** — Click the star icon to bookmark any page. Access all your bookmarks from the menu.
7. **Incognito Mode** — Open a new incognito window from the menu to browse privately without saving history or cookies.
8. **Switch Themes** — Go to Settings to switch between Dark Mode and Light Mode.
9. **Voice Search** — Click the microphone icon to use voice search (simulated).
10. **Download Files** — All downloads are tracked in the built-in Download Manager.

---

## ✨ Features

### 🤖 Built-in AI Assistant
- **Summarize Webpages** — Instantly get the gist of long articles or documents.
- **Smart Q&A** — Ask questions about the content of the current page.
- **Generate Notes** — Automatically create study notes from educational content.
- **Smart Tabs** — Uses AI logic to automatically group and organize your tabs by topic.

### 🛡️ Privacy & Security
- **Native Ad Blocker** — Built right into the network interceptor to stop trackers and ads from loading, speeding up page load times.
- **Password Manager** — Securely save, manage, and retrieve your credentials across your favorite websites.
- **Incognito Mode** — Browse without leaving a trace — no history, cookies, or cache are saved during your session.

### 📱 Developer Tools & Mobile Emulation
- **Mobile View Toggle** — With a single click, emulate a mobile device environment to test responsive designs and mobile-friendly websites.

### 🔌 Seamless Offline Mode
- **Offline Caching** — Searcher caches pages you visit so you can read them even without an internet connection (500 MB disk cache).
- **Offline Search** — If you lose connection, the address bar intelligently searches your local history and bookmarks.
- **Offline Mini-Game** — Includes a classic dinosaur-style offline game built right in, so you're never bored when the WiFi drops!

### ⚙️ Productivity
- **Custom Start Page** — A blazing-fast, locally hosted new tab page with quick links and an integrated search bar.
- **Full History & Bookmarks** — Easily navigate your past web visits and save your favorite pages.
- **Session Restore** — Searcher remembers where you left off. Re-open the browser to instantly restore your previous tabs.
- **Download Manager** — Track, pause, and manage all your downloaded files in a dedicated interface.
- **Dynamic Theming** — Switch seamlessly between carefully crafted Light and Dark modes.
- **Voice Search** — Use voice commands to search the web hands-free.
- **Multiple Search Engines** — Choose from Google, Bing, DuckDuckGo, and more in Settings.

---

## 📂 Project Structure

```
Searcher/
├── main.py                  # Application entry point
├── browser/                 # Core browser components
│   ├── main_window.py       # Main GUI and layout
│   ├── tabs.py              # Custom tab widget logic
│   ├── navigation.py        # Toolbar and address bar
│   ├── search_engine.py     # Search engine integration
│   ├── history.py           # History dialog
│   ├── bookmarks.py         # Bookmarks manager
│   ├── downloads.py         # Download manager
│   ├── settings.py          # Configuration and settings dialog
│   ├── themes.py            # Dark and light QSS styles
│   ├── ai_service.py        # AI logic and simulation
│   ├── ai_sidebar.py        # Dockable AI assistant UI
│   ├── adblocker.py         # Request interceptor for ads
│   ├── passwords.py         # Password manager dialog
│   └── voice.py             # Voice search simulation
├── database/
│   ├── db_manager.py        # SQLite database operations
│   └── searcher.db          # Auto-generated database file
├── assets/
│   ├── start_page.html      # Custom new tab page
│   ├── error_page.html      # Custom error page
│   ├── offline_page.html    # Offline page with mini-game
│   └── logo.png             # Browser logo
└── config/
    └── settings.json        # Auto-generated settings file
```

---

## 🛠️ For Developers: Run Locally

### Prerequisites
- Python 3.12 or newer installed on Windows.

### Installation
```bash
# Clone the repository
git clone https://github.com/Amit123103/Searcher_browser.git
cd Searcher_browser

# Install dependencies
pip install PyQt6 PyQt6-WebEngine

# Run the browser
python main.py
```

---

## 📦 Build Standalone Executable

```bash
# Install PyInstaller
pip install pyinstaller

# Build the .exe
pyinstaller --noconsole --windowed --onefile --name "Searcher" --add-data "assets;assets" main.py

# The output will be in dist/Searcher.exe
```

---

## 🔮 Future Improvements
- Integrate a live LLM API (e.g., Google Gemini) into `ai_service.py`.
- Integrate `SpeechRecognition` and `PyAudio` into `voice.py` for real microphone input.
- Expand Ad Blocker to support full EasyList parsing.
- Add browser extension support.

---

## 📄 License
This project is open source and available for personal and educational use.

---

**Made with ❤️ by [Amit](https://github.com/Amit123103)**
