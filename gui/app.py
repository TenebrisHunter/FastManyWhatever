# ============================================================
#  FastManyWhatever — Tkinter GUI hub
#  Автор: Ключенко М.А. (Омск, ОмГТУ, ИБа-261)
#  Версия: 0.2.0
# ============================================================

import json
import subprocess
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

ROOT = Path(__file__).resolve().parent.parent
INSTRUMENTS_DIR = ROOT / "instruments"

LANG = "ru"

SORT_CHOICES = [
    ("name_asc",  "Имя: А → Я"),
    ("name_desc", "Имя: Я → А"),
    ("date_new",  "Дата: новые сверху"),
    ("date_old",  "Дата: старые сверху"),
]


def load_instruments(log=print) -> list[dict]:
    tools = []
    log(f"[i] instruments dir: {INSTRUMENTS_DIR}")
    if not INSTRUMENTS_DIR.is_dir():
        log(f"[!] directory not found: {INSTRUMENTS_DIR}")
        return tools
    for d in sorted(INSTRUMENTS_DIR.iterdir()):
        if not d.is_dir():
            continue
        meta_path = d / "meta.json"
        if not meta_path.is_file():
            log(f"[!] skip {d.name}: no meta.json")
            continue
        try:
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
            meta["_dir"] = str(d)
            tools.append(meta)
            log(f"[+] loaded {d.name}")
        except (OSError, json.JSONDecodeError) as e:
            log(f"[!] skip {d.name}: {e}")
    return tools


def tr(obj, lang=LANG):
    if isinstance(obj, dict):
        return obj.get(lang) or next(iter(obj.values()), "")
    return obj or ""


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("FastManyWhatever")
        self.geometry("1200x750")
        self.minsize(950, 600)

        self.tools = load_instruments()
        self.current_tool = None
        self.current_dir = ""
        self.all_entries = []       # полный список (с mtime, ext)
        self.visible_entries = []   # после фильтра + сортировки

        self._build_ui()

        if not self.tools:
            messagebox.showwarning(
                "Нет инструментов",
                f"В папке {INSTRUMENTS_DIR} не найдено ни одного meta.json.\n"
                f"Проверь, что файл существует и валидный JSON.")
        else:
            self._select_tool(0)

    # ------------- layout -------------

    def _build_ui(self):
        top = ttk.Frame(self, padding=(8, 8, 8, 4))
        top.pack(fill="x")

        ttk.Label(top, text="Инструмент:").pack(side="left")
        self.tool_var = tk.StringVar()
        self.tool_combo = ttk.Combobox(top, textvariable=self.tool_var,
                                       state="readonly", width=30)
        self.tool_combo["values"] = [tr(t["name"]) for t in self.tools]
        self.tool_combo.pack(side="left", padx=(6, 16))
        self.tool_combo.bind("<<ComboboxSelected>>", self._on_tool_change)

        self.dir_label = ttk.Label(top, text="Папка не выбрана", foreground="#666")
        self.dir_label.pack(side="left", padx=8)

        paned = ttk.PanedWindow(self, orient="horizontal")
        paned.pack(fill="both", expand=True, padx=8, pady=4)

        # ---- left: dir + filter + list ----
        left = ttk.Frame(paned)
        paned.add(left, weight=1)

        row1 = ttk.Frame(left)
        row1.pack(fill="x", pady=(0, 4))
        ttk.Button(row1, text="Выбрать папку...", command=self._pick_dir).pack(side="left")
        ttk.Button(row1, text="Обновить", command=self._reload_dir).pack(side="left", padx=4)

        row2 = ttk.Frame(left)
        row2.pack(fill="x", pady=(0, 4))
        ttk.Label(row2, text="Тип:").pack(side="left")
        self.type_var = tk.StringVar(value="all")
        self.type_combo = ttk.Combobox(row2, textvariable=self.type_var,
                                       state="readonly", width=14)
        self.type_combo["values"] = ["Все", "Только папки", "Только файлы"]
        self.type_combo.current(0)
        self.type_combo.pack(side="left", padx=(4, 8))
        self.type_combo.bind("<<ComboboxSelected>>", lambda e: self._apply_filters())

        ttk.Label(row2, text="Сортировка:").pack(side="left")
        self.sort_var = tk.StringVar(value="name_asc")
        self.sort_combo = ttk.Combobox(row2, textvariable=self.sort_var,
                                       state="readonly", width=20,
                                       values=[label for _, label in SORT_CHOICES])
        self.sort_combo.current(0)
        self.sort_combo.pack(side="left", padx=4)
        self.sort_combo.bind("<<ComboboxSelected>>", lambda e: self._apply_filters())

        row3 = ttk.Frame(left)
        row3.pack(fill="x", pady=(0, 4))
        ttk.Button(row3, text="Все", command=self._check_all).pack(side="left")
        ttk.Button(row3, text="Ничего", command=self._uncheck_all).pack(side="left", padx=4)
        self.count_label = ttk.Label(row3, text="0 / 0", foreground="#666")
        self.count_label.pack(side="right")

        self.files_list = tk.Listbox(left, selectmode="extended", activestyle="none",
                                     font=("Consolas", 10))
        self.files_list.pack(fill="both", expand=True)
        self.files_list.bind("<Button-1>", self._on_list_click)

        # ---- right: form + preview + buttons ----
        right = ttk.Frame(paned)
        paned.add(right, weight=1)

        self.form_frame = ttk.LabelFrame(right, text="Параметры", padding=8)
        self.form_frame.pack(fill="x")
        self.param_widgets = {}

        ttk.Label(right, text="Предпросмотр:").pack(anchor="w", pady=(8, 2))
        self.preview_text = tk.Text(right, height=10, font=("Consolas", 10), wrap="none")
        self.preview_text.pack(fill="both", expand=True)

        btns = ttk.Frame(right)
        btns.pack(fill="x", pady=6)
        ttk.Button(btns, text="Предпросмотр", command=self._on_preview).pack(side="left")
        ttk.Button(btns, text="Применить", command=self._on_apply).pack(side="left", padx=6)

        # ---- log ----
        log_frame = ttk.LabelFrame(self, text="Лог", padding=4)
        log_frame.pack(fill="both", expand=False, padx=8, pady=(0, 8))
        self.log_text = tk.Text(log_frame, height=8, font=("Consolas", 9), wrap="none")
        self.log_text.pack(fill="both", expand=True)

    # ------------- tools -------------

    def _on_tool_change(self, _event=None):
        self._select_tool(self.tool_combo.current())

    def _select_tool(self, idx):
        if not self.tools or idx < 0:
            return
        self.current_tool = self.tools[idx]
        self.form_frame.configure(text=f"Параметры — {tr(self.current_tool['name'])}")
        for w in self.form_frame.winfo_children():
            w.destroy()
        self.param_widgets = {}
        self._build_form(self.current_tool.get("params", []))
        self._clear_preview()
        self._log("")
        self._log(f"[i] {tr(self.current_tool['name'])}: {tr(self.current_tool.get('description'))}")

    def _build_form(self, params):
        row = 0
        for p in params:
            pid = p["id"]
            ttk.Label(self.form_frame, text=tr(p["label"]) + ":").grid(
                row=row, column=0, sticky="w", padx=(0, 6), pady=3)
            if p["type"] == "text":
                var = tk.StringVar(value=str(p.get("default", "")))
                ttk.Entry(self.form_frame, textvariable=var, width=30).grid(
                    row=row, column=1, sticky="we", pady=3)
                self.param_widgets[pid] = ("text", var)
            elif p["type"] == "choice":
                var = tk.StringVar(value=str(p.get("default", "")))
                frame = ttk.Frame(self.form_frame)
                frame.grid(row=row, column=1, sticky="w", pady=3)
                for opt in p.get("options", []):
                    ttk.Radiobutton(frame, text=tr(opt["label"]), value=opt["value"],
                                    variable=var).pack(side="left", padx=(0, 8))
                self.param_widgets[pid] = ("choice", var)
            row += 1
        self.form_frame.columnconfigure(1, weight=1)

    # ------------- dir / files -------------

    def _pick_dir(self):
        d = filedialog.askdirectory(title="Выберите папку")
        if not d:
            return
        self.current_dir = d
        self.dir_label.configure(text=f"Папка: {d}", foreground="#000")
        self._reload_dir()

    def _reload_dir(self):
        self.all_entries = []
        self.visible_entries = []
        if not self.current_dir:
            self._refresh_list()
            return
        try:
            items = list(Path(self.current_dir).iterdir())
        except OSError as e:
            messagebox.showerror("Ошибка", f"Не удалось прочитать папку: {e}")
            return
        for p in items:
            try:
                mtime = p.stat().st_mtime
            except OSError:
                mtime = 0
            self.all_entries.append({
                "name": p.name,
                "path": str(p),
                "is_dir": p.is_dir(),
                "ext": p.suffix.lower() if p.is_file() else "",
                "mtime": mtime,
                "checked": True,
            })
        self._update_type_filter_choices()
        self._apply_filters()

    def _update_type_filter_choices(self):
        exts = sorted({e["ext"] for e in self.all_entries if e["ext"]})
        values = ["Все", "Только папки", "Только файлы"] + [f"Расширение {e}" for e in exts]
        self.type_combo["values"] = values
        if self.type_var.get() not in values:
            self.type_combo.current(0)

    def _apply_filters(self):
        type_choice = self.type_var.get()
        sort_label = self.sort_combo.get()
        sort_key = next((k for k, v in SORT_CHOICES if v == sort_label), "name_asc")

        filtered = []
        for e in self.all_entries:
            if type_choice == "Все":
                pass
            elif type_choice == "Только папки":
                if not e["is_dir"]:
                    continue
            elif type_choice == "Только файлы":
                if e["is_dir"]:
                    continue
            elif type_choice.startswith("Расширение "):
                want = type_choice[len("Расширение "):]
                if e["is_dir"] or e["ext"] != want:
                    continue
            filtered.append(e)

        if sort_key == "name_asc":
            filtered.sort(key=lambda e: (not e["is_dir"], e["name"].lower()))
        elif sort_key == "name_desc":
            filtered.sort(key=lambda e: (not e["is_dir"], e["name"].lower()), reverse=True)
        elif sort_key == "date_new":
            filtered.sort(key=lambda e: e["mtime"], reverse=True)
        elif sort_key == "date_old":
            filtered.sort(key=lambda e: e["mtime"])

        self.visible_entries = filtered
        self._refresh_list()

    def _refresh_list(self):
        self.files_list.delete(0, "end")
        for e in self.visible_entries:
            mark = "☑" if e["checked"] else "☐"
            icon = "📁" if e["is_dir"] else "📄"
            self.files_list.insert("end", f"{mark} {icon} {e['name']}")
        checked = sum(1 for e in self.visible_entries if e["checked"])
        self.count_label.configure(text=f"{checked} / {len(self.visible_entries)}")

    def _on_list_click(self, event):
        idx = self.files_list.nearest(event.y)
        if idx < 0 or idx >= len(self.visible_entries):
            return
        self.visible_entries[idx]["checked"] = not self.visible_entries[idx]["checked"]
        self._refresh_list()

    def _check_all(self):
        for e in self.visible_entries:
            e["checked"] = True
        self._refresh_list()

    def _uncheck_all(self):
        for e in self.visible_entries:
            e["checked"] = False
        self._refresh_list()

    # ------------- run tool -------------

    def _collect_params(self) -> dict:
        return {pid: var.get() for pid, (_, var) in self.param_widgets.items()}

    def _build_cmd(self, dry_run: bool) -> list[str]:
        tool = self.current_tool
        script = Path(tool["_dir"]) / tool["scripts"]["windows"]
        params = self._collect_params()
        cmd = ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass",
               "-File", str(script), "-Dir", self.current_dir]
        for p in tool.get("params", []):
            pid = p["id"]
            if pid in params:
                flag = "-" + pid[0].upper() + pid[1:]
                cmd.extend([flag, params[pid]])
        if dry_run:
            cmd.append("-DryRun")
        return cmd

    def _run_tool(self, dry_run: bool):
        if not self.current_dir:
            messagebox.showwarning("Нет папки", "Сначала выберите папку.")
            return 1, ""
        checked = [e["name"] for e in self.visible_entries if e["checked"]]
        if not checked:
            messagebox.showwarning("Нет выбора", "Отметьте хотя бы один элемент.")
            return 1, ""
        cmd = self._build_cmd(dry_run)
        if len(checked) != len(self.visible_entries):
            cmd.append("-Files")
            cmd.extend(checked)
        self._log("[cmd] " + " ".join(cmd))
        try:
            r = subprocess.run(cmd, capture_output=True, text=True,
                               encoding="utf-8", errors="replace")
        except OSError as e:
            return 1, f"Не удалось запустить: {e}"
        return r.returncode, (r.stdout or "") + (r.stderr or "")

    def _on_preview(self):
        self._clear_preview()
        self._log("— Предпросмотр —")
        code, out = self._run_tool(dry_run=True)
        self.preview_text.insert("end", out)
        last = out.strip().splitlines()[-1] if out.strip() else "(пусто)"
        self._log(last)

    def _on_apply(self):
        checked = [e for e in self.visible_entries if e["checked"]]
        if not checked:
            messagebox.showwarning("Нет выбора", "Отметьте хотя бы один элемент.")
            return
        if not messagebox.askyesno("Подтверждение",
                f"Переименовать {len(checked)} элементов?\n"
                f"Инструмент: {tr(self.current_tool['name'])}"):
            return
        self._log("— Применение —")
        code, out = self._run_tool(dry_run=False)
        self._log(out)
        if code == 0:
            messagebox.showinfo("Готово", "Операция выполнена.")
        else:
            messagebox.showwarning("Завершено с ошибками", "Смотрите лог.")
        self._reload_dir()

    # ------------- misc -------------

    def _clear_preview(self):
        self.preview_text.delete("1.0", "end")

    def _log(self, text: str):
        self.log_text.insert("end", text + "\n")
        self.log_text.see("end")


def main():
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()