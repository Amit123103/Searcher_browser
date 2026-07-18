# Searcher Browser

**Searcher** is a modern, lightweight, and fast desktop web browser built with Python and PyQt6. It features a sleek UI inspired by modern browsers like Arc and Google Chrome, and comes packed with advanced tools including an AI Assistant, Ad Blocker, and Password Manager.

## Features

- **Modern Interface**: Clean design with dynamic Light and Dark mode themes.
- **AI Assistant**: A built-in sidebar to summarize web pages, generate notes, and answer questions.
- **Smart Tabs**: Automatically organize and group your tabs by topic using AI.
- **Privacy & Security**: Incognito mode, built-in Ad Blocker, and an integrated Password Manager.
- **Productivity**: Browsing history, bookmarks, session restore, and download manager.
- **Custom Start Page**: A fast, local HTML start page with a built-in search bar and quick links.

---

## Prerequisites

Ensure you have Python 3.12 or newer installed on your Windows machine.

## Installation

1. **Clone or Download** the repository to your local machine.
2. **Open a terminal** and navigate to the project directory:
   ```bash
   cd path/to/searcher_browser
   ```
3. **Install the required dependencies** using `pip`:
   ```bash
   pip install PyQt6 PyQt6-WebEngine
   ```

## How to Run Locally

To launch the browser in development mode, simply run the `main.py` script from your terminal:

```bash
python main.py
```

---

## How to Deploy (Create a Standalone Executable)

To distribute the Searcher browser so others can run it without installing Python or any dependencies, you can package it into a standalone `.exe` file using **PyInstaller**.

### 1. Install PyInstaller
In your terminal, run:
```bash
pip install pyinstaller
```

### 2. Build the Executable
Run the following command from the root of your project directory to build a windowed (no console) standalone application. We also need to ensure that the `assets` folder is bundled into the executable.

```bash
pyinstaller --noconsole --windowed --name "Searcher" --add-data "assets;assets" main.py
```

### 3. Locate the Output
Once the build process completes:
- Navigate to the newly created `dist` folder in your project directory.
- Inside `dist/Searcher/`, you will find `Searcher.exe`.
- You can create a shortcut to this `.exe` file and place it on your Desktop, or zip the entire `Searcher` folder to share it with others!

---

## Project Structure

```text
Searcher/
├── main.py                  # Application entry point
├── browser/                 # Core browser components
│   ├── main_window.py       # Main GUI and layout
│   ├── tabs.py              # Custom tab widget logic
│   ├── navigation.py        # Toolbar and address bar
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
│   └── error_page.html      # Custom error page
└── config/
    └── settings.json        # Auto-generated settings file
```

## Future Improvements
- Integrate a live LLM API (e.g., Google Gemini) into `ai_service.py`.
- Integrate `SpeechRecognition` and `PyAudio` into `voice.py` for real microphone input.
- Expand Ad Blocker to support full EasyList parsing.
