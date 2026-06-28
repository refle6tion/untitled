"""File Cache App — GUI and CLI entry point."""

from __future__ import annotations

import argparse
import sys
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from cache_manager import (
    cache_dir_for,
    cache_file,
    format_bytes,
    get_manifest,
    list_cached_files,
)


class FileCacheApp(tk.Tk):
    def __init__(self, initial_file: Path | None = None) -> None:
        super().__init__()
        self.title("File Cache App")
        self.geometry("720x480")
        self.minsize(560, 380)

        self._file: Path | None = initial_file.resolve() if initial_file and initial_file.is_file() else None
        self._cancel_event = threading.Event()
        self._worker: threading.Thread | None = None
        self._busy = False

        self._build_ui()
        if self._file:
            self._set_file(self._file)

    def _build_ui(self) -> None:
        pad = {"padx": 10, "pady": 6}

        top = ttk.Frame(self)
        top.pack(fill=tk.X, **pad)

        ttk.Label(top, text="File:").pack(side=tk.LEFT)
        self._file_var = tk.StringVar(value="No file selected")
        ttk.Entry(top, textvariable=self._file_var, state="readonly").pack(
            side=tk.LEFT, fill=tk.X, expand=True, padx=(6, 6)
        )
        ttk.Button(top, text="Browse…", command=self._browse).pack(side=tk.LEFT)

        info = ttk.LabelFrame(self, text="Status")
        info.pack(fill=tk.X, **pad)

        self._status_var = tk.StringVar(value="Select a file, then click Cache File")
        ttk.Label(info, textvariable=self._status_var).pack(anchor=tk.W, padx=8, pady=4)

        self._cache_info_var = tk.StringVar(value="")
        ttk.Label(info, textvariable=self._cache_info_var, foreground="#555").pack(
            anchor=tk.W, padx=8, pady=(0, 6)
        )

        self._progress = ttk.Progressbar(info, mode="determinate")
        self._progress.pack(fill=tk.X, padx=8, pady=(0, 8))

        actions = ttk.Frame(self)
        actions.pack(fill=tk.X, **pad)
        self._cache_btn = ttk.Button(actions, text="Cache File", command=self._start_cache)
        self._cache_btn.pack(side=tk.LEFT)
        self._cancel_btn = ttk.Button(
            actions, text="Cancel", command=self._cancel, state=tk.DISABLED
        )
        self._cancel_btn.pack(side=tk.LEFT, padx=(8, 0))
        ttk.Button(actions, text="Open Cache Location", command=self._open_cache).pack(
            side=tk.LEFT, padx=(8, 0)
        )

        details = ttk.LabelFrame(self, text="Cache Details")
        details.pack(fill=tk.BOTH, expand=True, **pad)

        self._details = tk.Text(details, height=8, wrap=tk.WORD, state=tk.DISABLED, font=("Consolas", 10))
        self._details.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        bottom = ttk.LabelFrame(self, text="Previously Cached Files")
        bottom.pack(fill=tk.BOTH, expand=False, **pad)
        self._history = tk.Listbox(bottom, height=4)
        self._history.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
        self._history.bind("<Double-Button-1>", self._on_history_select)
        self._load_history()

    def _set_file(self, path: Path) -> None:
        self._file = path.resolve()
        self._file_var.set(str(self._file))
        self._refresh_cache_info()

    def _browse(self) -> None:
        path = filedialog.askopenfilename(
            initialdir=str(self._file.parent if self._file else Path.cwd()),
        )
        if path:
            self._set_file(Path(path))

    def _refresh_cache_info(self) -> None:
        if not self._file:
            self._cache_info_var.set("")
            self._set_details("")
            return

        manifest = get_manifest(self._file)
        if manifest:
            self._cache_info_var.set(
                f"Cached {format_bytes(manifest.size)} at {manifest.cached_at}"
            )
            self._set_details(
                f"Source:   {manifest.source_file}\n"
                f"Name:     {manifest.file_name}\n"
                f"Size:     {format_bytes(manifest.size)}\n"
                f"Modified: {manifest.modified}\n"
                f"Cached:   {manifest.cached_at}\n"
                f"SHA-256:  {manifest.sha256}\n"
                f"Location: {cache_dir_for(self._file)}"
            )
        else:
            self._cache_info_var.set("Not cached yet")
            self._set_details(f"Source: {self._file}\n\nThis file has not been cached.")

    def _set_details(self, text: str) -> None:
        self._details.configure(state=tk.NORMAL)
        self._details.delete("1.0", tk.END)
        self._details.insert("1.0", text)
        self._details.configure(state=tk.DISABLED)

    def _load_history(self) -> None:
        self._history.delete(0, tk.END)
        for item in list_cached_files():
            label = f"{item['source_file']} — {format_bytes(item['size'])}"
            self._history.insert(tk.END, label)

    def _on_history_select(self, _event: tk.Event) -> None:
        sel = self._history.curselection()
        if not sel:
            return
        files = list_cached_files()
        idx = sel[0]
        if idx < len(files):
            self._set_file(Path(files[idx]["source_file"]))

    def _set_busy(self, busy: bool) -> None:
        self._busy = busy
        state = tk.DISABLED if busy else tk.NORMAL
        self._cache_btn.configure(state=state)
        self._cancel_btn.configure(state=tk.NORMAL if busy else tk.DISABLED)

    def _start_cache(self) -> None:
        if self._busy:
            return
        if not self._file or not self._file.is_file():
            messagebox.showerror("Error", "Select a file to cache first.")
            return

        self._cancel_event.clear()
        self._set_busy(True)
        self._progress["value"] = 0
        self._status_var.set("Caching file…")

        def worker() -> None:
            try:
                def on_progress(name: str, done: int, total: int) -> None:
                    pct = (done / total * 100) if total else 0
                    self.after(0, lambda: self._progress.configure(value=pct))
                    if name:
                        self.after(0, lambda n=name: self._status_var.set(f"Caching: {n}"))

                manifest = cache_file(
                    self._file,
                    on_progress=on_progress,
                    cancel_event=self._cancel_event,
                )
                self.after(0, lambda: self._on_cache_done(manifest))
            except InterruptedError:
                self.after(0, self._on_cache_cancelled)
            except Exception as exc:
                self.after(0, lambda: self._on_cache_error(exc))

        self._worker = threading.Thread(target=worker, daemon=True)
        self._worker.start()

    def _cancel(self) -> None:
        self._cancel_event.set()
        self._status_var.set("Cancelling…")

    def _on_cache_done(self, manifest) -> None:
        self._set_busy(False)
        self._progress["value"] = 100
        self._status_var.set(f"Done — cached {manifest.file_name} ({format_bytes(manifest.size)})")
        self._refresh_cache_info()
        self._load_history()

    def _on_cache_cancelled(self) -> None:
        self._set_busy(False)
        self._progress["value"] = 0
        self._status_var.set("Cancelled")
        self._refresh_cache_info()

    def _on_cache_error(self, exc: Exception) -> None:
        self._set_busy(False)
        self._progress["value"] = 0
        self._status_var.set("Error")
        messagebox.showerror("Cache Error", str(exc))

    def _open_cache(self) -> None:
        if not self._file:
            messagebox.showinfo("Cache", "Select a file first.")
            return
        path = cache_dir_for(self._file)
        if not path.exists():
            messagebox.showinfo("Cache", "No cache exists for this file yet.")
            return
        import os
        import subprocess

        if sys.platform == "win32":
            os.startfile(path)  # type: ignore[attr-defined]
        elif sys.platform == "darwin":
            subprocess.run(["open", str(path)], check=False)
        else:
            subprocess.run(["xdg-open", str(path)], check=False)


def _resolve_initial_file(args: argparse.Namespace) -> Path | None:
    if args.file:
        return Path(args.file).resolve()
    if len(sys.argv) >= 2 and not sys.argv[1].startswith("-"):
        candidate = Path(sys.argv[1])
        if candidate.is_file():
            return candidate.resolve()
    return None


def run_cli(source: Path) -> int:
    print(f"Caching file: {source}")

    def on_progress(name: str, done: int, total: int) -> None:
        if name:
            print(f"  {name} ({done}/{total})")

    try:
        manifest = cache_file(source, on_progress=on_progress)
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    print(f"Done — {manifest.file_name}, {format_bytes(manifest.size)}")
    print(f"Cache location: {cache_dir_for(source)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Cache a single file into local storage."
    )
    parser.add_argument(
        "file",
        nargs="?",
        help="File to cache",
    )
    parser.add_argument(
        "--cli",
        action="store_true",
        help="Run in command-line mode without opening the GUI",
    )
    args = parser.parse_args()

    source = _resolve_initial_file(args)

    if args.cli:
        if not source or not source.is_file():
            print("Error: provide a file path to cache.", file=sys.stderr)
            print("Usage: py app.py --cli path\\to\\file.txt", file=sys.stderr)
            return 1
        return run_cli(source)

    app = FileCacheApp(initial_file=source)
    app.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
