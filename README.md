# 🌐 Searcher Browser

**Searcher** is a powerful, modern, and lightweight desktop web browser built with Python and PyQt6. Designed with speed, security, and productivity in mind, it offers a sleek user interface and a suite of advanced features, including a built-in AI Assistant, robust Ad Blocker, and a secure Password Manager.

---

## 🚀 Quick Download & Run (No Installation Required!)

Want to try Searcher Browser immediately? You can download the pre-compiled, portable executable for Windows right now.

**📥 [Download Searcher Browser for Windows](https://github.com/Amit123103/Searcher_browser/releases/latest/download/Searcher.zip)**

**How to use:**
1. Download the `Searcher.zip` file from the link above.
2. Extract the ZIP file to any location on your computer.
3. Open the extracted folder and double-click `Searcher.exe`.
4. **Enjoy browsing!** No installation, Python, or dependencies required.

*(Note: If the link above says "Not Found", please ensure you have published a Release on GitHub and uploaded the `Searcher.zip` file to it.)*

---

## ✨ Comprehensive Feature List

### 🤖 Built-in AI Assistant
Searcher comes with an integrated AI sidebar that enhances your browsing experience:
- **Summarize Webpages:** Instantly get the gist of long articles or documents.
- **Smart Q&A:** Ask questions about the content of the current page.
- **Generate Notes:** Automatically create study notes from educational content.
- **Smart Tabs:** Uses AI logic to automatically group and organize your messy tabs by topic.

### 🛡️ Privacy & Security
- **Native Ad Blocker:** Built right into the network interceptor to stop trackers and ads from loading, speeding up page load times.
- **Password Manager:** Securely save, manage, and retrieve your credentials across your favorite websites.
- **Incognito Mode:** Browse without leaving a trace—no history, cookies, or cache are saved during your session.

### 📱 Developer Tools & Mobile Emulation
- **Mobile View Toggle:** With a single click, emulate a mobile device environment to test responsive designs and mobile-friendly websites on the fly.

### 🔌 Seamless Offline Mode
- **Offline Caching:** Searcher caches pages you visit so you can read them even without an internet connection.
- **Offline Search:** If you lose connection, the address bar intelligently searches your local history and bookmarks instead of the web.
- **Offline Mini-Game:** Includes a classic dinosaur-style offline game built right in, so you're never bored when the WiFi drops!

### ⚙️ Ultimate Productivity
- **Custom Start Page:** A blazing-fast, locally hosted new tab page with quick links and an integrated search bar.
- **Full History & Bookmarks:** Easily navigate your past web visits and save your favorite pages.
- **Session Restore:** Searcher remembers where you left off. Re-open the browser to instantly restore your previous tabs.
- **Download Manager:** Track, pause, and manage all your downloaded files in a dedicated interface.
- **Dynamic Theming:** Switch seamlessly between carefully crafted Light and Dark modes.

---

## 🛠️ For Developers: How to Run Locally

### Prerequisites
Ensure you have Python 3.12 or newer installed on your Windows machine.

### Installation
1. **Clone or Download** the repository to your local machine.
2. **Open a terminal** and navigate to the project directory:
   ```bash
   cd path/to/searcher_browser
   ```
3. **Install the required dependencies** using `pip`:
   ```bash
   pip install PyQt6 PyQt6-WebEngine
   ```
4. **Launch the browser** in development mode:
   ```bash
   python main.py
   ```

---

## 📦 How to Deploy (Create a Standalone Executable)

To distribute the Searcher browser so others can run it without installing Python, you can package it into a standalone `.exe` file using **PyInstaller**.

1. **Install PyInstaller**:
   ```bash
   pip install pyinstaller
   ```
2. **Build the Executable**:
   Run the following command from the root of your project directory to build a windowed (no console) standalone application.
   ```bash
   pyinstaller --noconsole --windowed --name "Searcher" --add-data "assets;assets" main.py
   ```
3. **Share Your Browser**:
   - Navigate to the newly created `dist` folder in your project directory.
   - Inside `dist/Searcher/`, you will find `Searcher.exe`.
   - Zip the entire `Searcher` folder.
   - Upload this zip file to your GitHub Releases or any cloud storage, and share the link with others!

---

## 📂 Project Structure

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

---

## 🔮 Future Improvements
- Integrate a live LLM API (e.g., Google Gemini) into `ai_service.py`.
- Integrate `SpeechRecognition` and `PyAudio` into `voice.py` for real microphone input.
- Expand Ad Blocker to support full EasyList parsing.
