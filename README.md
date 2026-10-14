# Omni World AI Super Studio — Python Starter

A responsive, liquid-glass style web workspace built with Python + Flask, HTML, CSS, and JavaScript.

## Included and working
- Account registration and sign-in (passwords stored as one-way hashes)
- Admin dashboard, user listing, and role changes
- Workspace chat with permitted file attachments
- Browser/search page with Brave, Google, and DuckDuckGo search links
- Responsive mobile layout, animated buttons, transparent glass panels, dark/light theme
- Local SQLite database and local upload folder

## Important security note
The admin login is created locally on first run:
- Username: `admin`
- Password: `ChangeMe-123!`

**Change this password before using the project.** The starter does not expose or store plaintext passwords in the admin panel. Never collect a user's Gmail password. If you later add Google sign-in, use Google's official OAuth flow.

For production, set a strong environment variable named `STUDIO_SECRET_KEY`, add CSRF protection, rate limiting, email verification, secure cookies, backups, and malware scanning for uploaded files.

## Run on Windows
1. Install Python 3.11 or newer from python.org and enable “Add Python to PATH”.
2. Extract this ZIP into a folder.
3. Open Command Prompt in that folder.
4. Run:

```bat
python -m venv .venv
.venv\\Scripts\\activate
python -m pip install -r requirements.txt
python app.py
```

5. Open `http://127.0.0.1:5000` in your browser.

## Run on Android
This is a Python web app, not a native APK. It can be tested on a computer first. For Android, host it securely and open it in a browser, or package a separate native app after the backend is ready.

## Current limits / next modules
The photo/video/AI/PDF cards are roadmap placeholders, not completed editors. A full CapCut-style editor, true Brave browser engine, background removal, cloud storage, Gmail sending, realtime private chat, and 2K/4K video export need additional libraries/services and substantial implementation.
- Image crop/resize/A4 print sheet: Pillow
- PDF conversion: PyMuPDF, Pillow, openpyxl/reporting tools as appropriate
- Video trim/split/filters/export: FFmpeg, with a UI timeline and export worker
- Background removal: server-side API key stored in environment/config, never in browser JavaScript
- Cloud sync: object storage provider + access controls
- Realtime chat: WebSocket service, private conversations, and authorization
- Google sign-in: official OAuth, never ask users for Gmail passwords

## File safety
Uploads are restricted by extension and maximum request size, but this is only a starter. Before public deployment, validate actual file contents, scan uploads, store files outside the public web root, and apply per-user access controls.
