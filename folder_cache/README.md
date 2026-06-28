# File Cache App

A portable Python app that caches **one selected file at a time** into local storage. Each cache includes a manifest with the original path, size, modification time, and SHA-256 checksum.

No external dependencies — uses Python 3.10+ and the standard library only.

## Requirements

- **Python 3.10 or newer**
- **tkinter** (included with most Python installs; needed for the GUI)

Check your install:

```powershell
py --version
```

## Quick start

### GUI

```powershell
py app.py
```

This opens a window where you can:

- Select a file with **Browse…**
- Click **Cache File** to copy it into the cache
- View cache details (size, hash, location)
- Click **Open Cache Location** to open the cache folder in Explorer
- Double-click a file in **Previously Cached Files** to load it

### Command line

Cache a specific file:

```powershell
py app.py --cli "C:\path\to\your\file.txt"
```

## Ways to use it

### Option 1 — Run from anywhere (recommended)

Keep the app in one place and pass the file path as an argument:

```powershell
py D:\path\to\folder_cache\app.py --cli "C:\Projects\report.pdf"
```

Or open the GUI with a file pre-selected:

```powershell
py D:\path\to\folder_cache\app.py "C:\Projects\report.pdf"
```

### Option 2 — Drag and drop (Windows)

Drag a file onto **`CacheDroppedFile.bat`**. The app caches that file and shows progress in the terminal.

Run **`CacheDroppedFile.bat`** with no arguments to open the GUI instead.

### Option 3 — Launch from the app directory

- **`CacheFolder.bat`** — opens the GUI (Windows)
- **`cache-folder.sh`** — opens the GUI (Linux/macOS)

## Where caches are stored

Caches are saved outside the source folder so your project directory stays clean:

| Platform | Location |
|----------|----------|
| Windows  | `%LOCALAPPDATA%\FolderCacheApp\caches\` |
| macOS/Linux | `~/FolderCacheApp/caches/` (or `$HOME`) |

Each cached file gets its own subdirectory keyed by the file's full path. Inside you'll find:

```
caches/
  <hash>/
    manifest.json    # metadata for the cached file
    report.pdf       # copy of the original file
```

### manifest.json

The manifest records:

- Original source file path
- File name
- When the cache was created
- File size and last modified time
- SHA-256 hash of the cached copy

Re-caching the same file **replaces** the previous cache for that path.

## File overview

| File | Purpose |
|------|---------|
| `app.py` | GUI and CLI entry point |
| `cache_manager.py` | Copying and manifest logic |
| `CacheDroppedFile.bat` | Drag-and-drop or GUI launcher (Windows) |
| `CacheFolder.bat` | Open GUI from the app directory (Windows) |
| `cache-folder.sh` | Open GUI from the app directory (Linux/macOS) |

## Tips

- **One file at a time** — select or pass a single file path; folders are not supported.
- **Re-cache to refresh** — click **Cache File** again to update the cache with the latest version.
- **History** — the GUI lists previously cached files at the bottom; double-click to load one.
- **Large files** — caching runs in a background thread in the GUI. Use **Cancel** to stop mid-run.

## Troubleshooting

**"Python is not installed or not on PATH"** (batch files)

Install Python from [python.org](https://www.python.org/downloads/) and enable **Add Python to PATH** during setup. On Windows you can also try `py` instead of `python`.

**GUI does not open**

Your Python build may not include tkinter. Reinstall Python and ensure tcl/tk is included, or use `--cli` mode instead.

**"Not a file" error**

You passed a folder or a path that does not exist. Provide the full path to a single file.

**Permission errors**

The source file must be readable and the cache directory must be writable (usually `%LOCALAPPDATA%` on Windows).

## Example

```powershell
py app.py --cli "D:\untitled\folder_cache\README.md"
```

Output:

```
Caching file: D:\untitled\folder_cache\README.md
  README.md (1/1)
Done — README.md, 4.2 KB
Cache location: C:\Users\You\AppData\Local\FolderCacheApp\caches\a1b2c3d4e5f67890
```
