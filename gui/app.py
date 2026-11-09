# ============================================================
#  FastManyWhatever — Tkinter GUI hub
#  Автор: Ключенко М.А. (Омск, ОмГТУ, ИБа-261)
#  Версия: 0.4.0
# ============================================================

import json
import subprocess
import tkinter as tk
import webbrowser
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

ROOT = Path(__file__).resolve().parent.parent
INSTRUMENTS_DIR = ROOT / "instruments"
APP_VERSION = "0.4.4"
GITHUB_URL = "https://github.com/TenebrisHunter/FastManyWhatever"
AUTHOR = "Ключенко М.А."
ORG = "Омск, ОмГТУ, ИБа-261, АНО ЦО ДО «Махаон»"
LICENSE = "MIT"

STRINGS = {
    "ru": {
        "app_title": "FastManyWhatever",
        "menu_tools": "Инструменты", "menu_settings": "Настройки", "menu_help": "Справка",
        "settings_about": "О проекте", "settings_theme": "Тема", "settings_lang": "Язык",
        "theme_light": "Светлая", "theme_dark": "Тёмная",
        "lang_ru": "Русский", "lang_en": "English",
        "help_placeholder": "Раздел «Помощь» в разработке.",
        "tool_label": "Инструмент:", "dir_not_selected": "Папка не выбрана",
        "pick_dir": "Выбрать папку...", "reload": "Обновить",
        "check_all": "Все", "uncheck_all": "Ничего",
        "type_label": "Тип:", "type_all": "Все", "type_dirs": "Только папки", "type_files": "Только файлы",
        "sort_label": "Сортировка:", "sort_name_asc": "Имя: А → Я", "sort_name_desc": "Имя: Я → А",
        "sort_date_new": "Дата: новые сверху", "sort_date_old": "Дата: старые сверху",
        "preview": "Предпросмотр", "apply": "Применить",
        "params": "Параметры", "preview_label": "Предпросмотр:",
        "log": "Лог", "copy_log": "Копировать лог",
        "no_tools": "Нет инструментов", "no_tools_msg": "В папке {dir} не найдено ни одного meta.json.",
        "confirm": "Подтверждение", "confirm_msg": "Выполнить для {n} элементов?\nИнструмент: {name}",
        "confirm_create": "Создать элементы по правилу?\nИнструмент: {name}",
        "done": "Готово", "done_msg": "Операция выполнена.",
        "error": "Ошибка", "warn_no_dir": "Сначала выберите папку.",
        "warn_no_sel": "Отметьте хотя бы один элемент.",
        "about_title": "О проекте", "copy": "Копировать", "select_all": "Выделить всё",
        "copy_link": "Копировать ссылку", "open_github": "Открыть на GitHub", "close": "Закрыть",
        "ext_prefix": "Расширение ",
    },
    "en": {
        "app_title": "FastManyWhatever",
        "menu_tools": "Tools", "menu_settings": "Settings", "menu_help": "Help",
        "settings_about": "About", "settings_theme": "Theme", "settings_lang": "Language",
        "theme_light": "Light", "theme_dark": "Dark",
        "lang_ru": "Русский", "lang_en": "English",
        "help_placeholder": "Help section is under construction.",
        "tool_label": "Tool:", "dir_not_selected": "No folder selected",
        "pick_dir": "Choose folder...", "reload": "Refresh",
        "check_all": "All", "uncheck_all": "None",
        "type_label": "Type:", "type_all": "All", "type_dirs": "Folders only", "type_files": "Files only",
        "sort_label": "Sort:", "sort_name_asc": "Name: A → Z", "sort_name_desc": "Name: Z → A",
        "sort_date_new": "Date: newest first", "sort_date_old": "Date: oldest first",
        "preview": "Preview", "apply": "Apply",
        "params": "Parameters", "preview_label": "Preview:",
        "log": "Log", "copy_log": "Copy log",
        "no_tools": "No tools", "no_tools_msg": "No meta.json found in {dir}.",
        "confirm": "Confirm", "confirm_msg": "Run for {n} items?\nTool: {name}",
        "confirm_create": "Create items by rule?\nTool: {name}",
        "done": "Done", "done_msg": "Operation completed.",
        "error": "Error", "warn_no_dir": "Choose a folder first.",
        "warn_no_sel": "Select at least one item.",
        "about_title": "About", "copy": "Copy", "select_all": "Select all",
        "copy_link": "Copy link", "open_github": "Open on GitHub", "close": "Close",
        "ext_prefix": "Extension ",
    },
}

THEMES = {
    "light": {"bg": "#fafafa", "bg_card": "#ffffff", "text": "#333333",
              "accent": "#4a90d9", "danger": "#d9534f", "success": "#2e7d32"},
    "dark":  {"bg": "#1a1a1a", "bg_card": "#2a2a2a", "text": "#e0e0e0",
              "accent": "#5ba0e3", "danger": "#e57373", "success": "#66bb6a"},
}

SORT_CHOICES = [
    ("name_asc", "sort_name_asc"), ("name_desc", "sort_name_desc"),
    ("date_new", "sort_date_new"), ("date_old", "sort_date_old"),
]


def load_instruments(log=print):
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
            log(f"[+] loaded {d.name} (target={meta.get('target', 'items')})")
        except (OSError, json.JSONDecodeError) as e:
            log(f"[!] skip {d.name}: {e}")
    return tools


def tr(obj, lang="ru"):
    if isinstance(obj, dict):
        return obj.get(lang) or next(iter(obj.values()), "")
    return obj or ""


def _ps_quote(s) -> str:
    return "'" + str(s).replace("'", "''") + "'"


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.lang = "ru"
        self.theme = "light"
        self._t = STRINGS[self.lang]

        self.title(f"{self._t['app_title']} {APP_VERSION}")
        self.geometry("1200x750")
        self.minsize(950, 600)

        self.tools = load_instruments()
        self.current_tool = None
        self.current_dir = ""
        self.all_entries = []
        self.visible_entries = []
        self.param_widgets = {}

        self.style = ttk.Style(self)
        self.style.theme_use("clam")

        self._build_menu()
        self._build_ui()
        self._apply_theme()

        if not self.tools:
            messagebox.showwarning(self._t["no_tools"],
                                   self._t["no_tools_msg"].format(dir=INSTRUMENTS_DIR))
        else:
            self._select_tool(0)

    # ------------- menu -------------

    def _build_menu(self):
        menubar = tk.Menu(self)
        self.configure(menu=menubar)
        self._menubar = menubar

        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label=self._t["menu_tools"], menu=tools_menu)
        self.tools_menu = tools_menu
        self._populate_tools_menu()

        settings_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label=self._t["menu_settings"], menu=settings_menu)
        settings_menu.add_command(label=self._t["settings_about"], command=self._show_about)
        theme_menu = tk.Menu(settings_menu, tearoff=0)
        theme_menu.add_command(label=self._t["theme_light"], command=lambda: self._set_theme("light"))
        theme_menu.add_command(label=self._t["theme_dark"], command=lambda: self._set_theme("dark"))
        settings_menu.add_cascade(label=self._t["settings_theme"], menu=theme_menu)
        lang_menu = tk.Menu(settings_menu, tearoff=0)
        lang_menu.add_command(label=self._t["lang_ru"], command=lambda: self._set_lang("ru"))
        lang_menu.add_command(label=self._t["lang_en"], command=lambda: self._set_lang("en"))
        settings_menu.add_cascade(label=self._t["settings_lang"], menu=lang_menu)

        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label=self._t["menu_help"], menu=help_menu)
        help_menu.add_command(label=self._t["menu_help"], command=self._show_help)

    def _populate_tools_menu(self):
        self.tools_menu.delete(0, "end")
        for i, tool in enumerate(self.tools):
            self.tools_menu.add_command(label=tr(tool["name"], self.lang),
                                        command=lambda idx=i: self._select_tool(idx))

    # ------------- ui -------------

    def _build_ui(self):
        self.main_frame = ttk.Frame(self, padding=8)
        self.main_frame.pack(fill="both", expand=True)

        top = ttk.Frame(self.main_frame)
        top.pack(fill="x", pady=(0, 6))

        self.tool_label_widget = ttk.Label(top, text=self._t["tool_label"])
        self.tool_label_widget.pack(side="left")

        self.tool_var = tk.StringVar()
        self.tool_combo = ttk.Combobox(top, textvariable=self.tool_var, state="readonly", width=32)
        self.tool_combo["values"] = [tr(t["name"], self.lang) for t in self.tools]
        if self.tools:
            self.tool_combo.current(0)
        self.tool_combo.pack(side="left", padx=(6, 16))
        self.tool_combo.bind("<<ComboboxSelected>>", self._on_tool_change)

        self.dir_label = ttk.Label(top, text=self._t["dir_not_selected"])
        self.dir_label.pack(side="left", padx=8)

        paned = ttk.PanedWindow(self.main_frame, orient="horizontal")
        paned.pack(fill="both", expand=True)

        left = ttk.Frame(paned)
        paned.add(left, weight=1)

        row1 = ttk.Frame(left)
        row1.pack(fill="x", pady=(0, 4))
        self.pick_btn = ttk.Button(row1, text=self._t["pick_dir"], command=self._pick_dir)
        self.pick_btn.pack(side="left")
        self.reload_btn = ttk.Button(row1, text=self._t["reload"], command=self._reload_dir)
        self.reload_btn.pack(side="left", padx=4)

        self.items_panel = ttk.Frame(left)
        self.items_panel.pack(fill="both", expand=True)

        row2 = ttk.Frame(self.items_panel)
        row2.pack(fill="x", pady=(0, 4))
        ttk.Label(row2, text=self._t["type_label"]).pack(side="left")
        self.type_var = tk.StringVar(value=self._t["type_all"])
        self.type_combo = ttk.Combobox(row2, textvariable=self.type_var, state="readonly", width=16)
        self.type_combo["values"] = [self._t["type_all"], self._t["type_dirs"], self._t["type_files"]]
        self.type_combo.current(0)
        self.type_combo.pack(side="left", padx=(4, 8))
        self.type_combo.bind("<<ComboboxSelected>>", lambda e: self._apply_filters())

        ttk.Label(row2, text=self._t["sort_label"]).pack(side="left")
        self.sort_var = tk.StringVar(value=self._t["sort_name_asc"])
        self.sort_combo = ttk.Combobox(row2, textvariable=self.sort_var, state="readonly", width=20,
                                       values=[self._t[k] for _, k in SORT_CHOICES])
        self.sort_combo.current(0)
        self.sort_combo.pack(side="left", padx=4)
        self.sort_combo.bind("<<ComboboxSelected>>", lambda e: self._apply_filters())

        self.checkbox_row = ttk.Frame(self.items_panel)
        self.checkbox_row.pack(fill="x", pady=(0, 4))
        self.check_all_btn = ttk.Button(self.checkbox_row, text=self._t["check_all"], command=self._check_all)
        self.check_all_btn.pack(side="left")
        self.uncheck_all_btn = ttk.Button(self.checkbox_row, text=self._t["uncheck_all"], command=self._uncheck_all)
        self.uncheck_all_btn.pack(side="left", padx=4)
        self.count_label = ttk.Label(self.checkbox_row, text="0 / 0")
        self.count_label.pack(side="right")

        list_frame = ttk.Frame(self.items_panel)
        list_frame.pack(fill="both", expand=True)
        self.files_list = tk.Listbox(list_frame, selectmode="extended", activestyle="none",
                                     font=("Consolas", 10), exportselection=False)
        self.files_list.pack(side="left", fill="both", expand=True)
        files_vscroll = ttk.Scrollbar(list_frame, orient="vertical", command=self.files_list.yview)
        files_vscroll.pack(side="right", fill="y")
        files_hscroll = ttk.Scrollbar(self.items_panel, orient="horizontal", command=self.files_list.xview)
        files_hscroll.pack(fill="x")
        self.files_list.configure(yscrollcommand=files_vscroll.set, xscrollcommand=files_hscroll.set)
        self.files_list.bind("<Button-1>", self._on_list_click)

        right = ttk.Frame(paned)
        paned.add(right, weight=1)

        self.form_frame = ttk.LabelFrame(right, text=self._t["params"], padding=8)
        self.form_frame.pack(fill="x")

        self.preview_label = ttk.Label(right, text=self._t["preview_label"])
        self.preview_label.pack(anchor="w", pady=(8, 2))
        preview_wrap = ttk.Frame(right)
        preview_wrap.pack(fill="both", expand=True)
        self.preview_text = tk.Text(preview_wrap, height=10, font=("Consolas", 10), wrap="none")
        self.preview_text.grid(row=0, column=0, sticky="nsew")
        preview_vscroll = ttk.Scrollbar(preview_wrap, orient="vertical", command=self.preview_text.yview)
        preview_vscroll.grid(row=0, column=1, sticky="ns")
        preview_hscroll = ttk.Scrollbar(preview_wrap, orient="horizontal", command=self.preview_text.xview)
        preview_hscroll.grid(row=1, column=0, sticky="ew")
        preview_wrap.grid_rowconfigure(0, weight=1)
        preview_wrap.grid_columnconfigure(0, weight=1)
        self.preview_text.configure(yscrollcommand=preview_vscroll.set, xscrollcommand=preview_hscroll.set)

        btns = ttk.Frame(right)
        btns.pack(fill="x", pady=6)
        self.preview_btn = ttk.Button(btns, text=self._t["preview"], command=self._on_preview)
        self.preview_btn.pack(side="left")
        self.apply_btn = ttk.Button(btns, text=self._t["apply"], command=self._on_apply)
        self.apply_btn.pack(side="left", padx=6)

        log_frame = ttk.LabelFrame(self.main_frame, text=self._t["log"], padding=4)
        log_frame.pack(fill="both", expand=False, pady=(6, 0))
        log_header = ttk.Frame(log_frame)
        log_header.pack(fill="x", pady=(0, 2))
        self.copy_log_btn = ttk.Button(log_header, text=self._t["copy_log"], command=self._copy_log)
        self.copy_log_btn.pack(side="right")
        log_body = ttk.Frame(log_frame)
        log_body.pack(fill="both", expand=True)
        self.log_text = tk.Text(log_body, height=8, font=("Consolas", 9), wrap="word")
        self.log_text.pack(fill="both", expand=True, side="left")
        log_scroll = ttk.Scrollbar(log_body, orient="vertical", command=self.log_text.yview)
        log_scroll.pack(side="right", fill="y")
        self.log_text.configure(yscrollcommand=log_scroll.set)

        self._bind_log_context_menu()

    def _bind_log_context_menu(self):
        self.log_menu = tk.Menu(self, tearoff=0)
        self.log_menu.add_command(label=self._t["copy"], command=self._copy_log_selection)
        self.log_menu.add_command(label=self._t["select_all"],
                                  command=lambda: self.log_text.tag_add("sel", "1.0", "end"))
        self.log_text.bind("<Button-3>", self._show_log_menu)

    def _show_log_menu(self, event):
        try:
            self.log_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.log_menu.grab_release()

    def _copy_log_selection(self):
        try:
            sel = self.log_text.get("sel.first", "sel.last")
        except tk.TclError:
            sel = self.log_text.get("1.0", "end-1c")
        self._copy_to_clipboard(sel)

    def _copy_log(self):
        self._copy_to_clipboard(self.log_text.get("1.0", "end-1c"))

    def _copy_to_clipboard(self, text):
        self.clipboard_clear()
        self.clipboard_append(text)

    # ------------- theme / lang -------------

    def _apply_theme(self):
        t = THEMES[self.theme]
        self.configure(bg=t["bg"])
        self.style.configure("TFrame", background=t["bg"])
        self.style.configure("TLabel", background=t["bg"], foreground=t["text"])
        self.style.configure("TButton", background=t["bg_card"], foreground=t["text"])
        self.style.configure("TLabelframe", background=t["bg"], foreground=t["text"])
        self.style.configure("TLabelframe.Label", background=t["bg"], foreground=t["text"])
        self.style.configure("TCombobox", fieldbackground=t["bg_card"], foreground=t["text"])
        self.log_text.configure(bg=t["bg_card"], fg=t["text"], insertbackground=t["text"])
        self.preview_text.configure(bg=t["bg_card"], fg=t["text"], insertbackground=t["text"])
        self.files_list.configure(bg=t["bg_card"], fg=t["text"],
                                  selectbackground=t["accent"], selectforeground="#ffffff")

    def _set_theme(self, name):
        self.theme = name
        self._apply_theme()

    def _set_lang(self, lang):
        self.lang = lang
        self._t = STRINGS[lang]
        self._refresh_texts()

    def _refresh_texts(self):
        self.title(f"{self._t['app_title']} {APP_VERSION}")
        self._menubar.entryconfigure(0, label=self._t["menu_tools"])
        self._menubar.entryconfigure(1, label=self._t["menu_settings"])
        self._menubar.entryconfigure(2, label=self._t["menu_help"])
        self._populate_tools_menu()
        self.tool_label_widget.configure(text=self._t["tool_label"])
        self.pick_btn.configure(text=self._t["pick_dir"])
        self.reload_btn.configure(text=self._t["reload"])
        self.check_all_btn.configure(text=self._t["check_all"])
        self.uncheck_all_btn.configure(text=self._t["uncheck_all"])
        self.preview_btn.configure(text=self._t["preview"])
        self.apply_btn.configure(text=self._t["apply"])
        self.copy_log_btn.configure(text=self._t["copy_log"])
        self.form_frame.configure(text=self._t["params"])
        self.preview_label.configure(text=self._t["preview_label"])
        self.type_combo["values"] = [self._t["type_all"], self._t["type_dirs"], self._t["type_files"]]
        self.sort_combo["values"] = [self._t[k] for _, k in SORT_CHOICES]
        self.tool_combo["values"] = [tr(t["name"], self.lang) for t in self.tools]
        if self.current_tool:
            self.tool_combo.current(self.tools.index(self.current_tool))
        self.log_menu.delete(0, "end")
        self.log_menu.add_command(label=self._t["copy"], command=self._copy_log_selection)
        self.log_menu.add_command(label=self._t["select_all"],
                                  command=lambda: self.log_text.tag_add("sel", "1.0", "end"))
        if self.current_tool:
            self._select_tool(self.tools.index(self.current_tool))

    def _show_about(self):
        dlg = tk.Toplevel(self)
        dlg.title(self._t["about_title"])
        dlg.geometry("560x360")
        dlg.transient(self); dlg.grab_set()
        t = THEMES[self.theme]
        dlg.configure(bg=t["bg"])
        text = tk.Text(dlg, wrap="word", height=12, padx=10, pady=10,
                       bg=t["bg_card"], fg=t["text"], insertbackground=t["text"])
        text.pack(fill="both", expand=True, padx=10, pady=(10, 4))
        info = (f"FastManyWhatever\n"
                f"{'Версия' if self.lang == 'ru' else 'Version'}: {APP_VERSION}\n\n"
                f"{'Автор' if self.lang == 'ru' else 'Author'}: {AUTHOR}\n"
                f"{'Организация' if self.lang == 'ru' else 'Organization'}: {ORG}\n"
                f"{'Лицензия' if self.lang == 'ru' else 'License'}: {LICENSE}\n\n"
                f"GitHub: {GITHUB_URL}")
        text.insert("1.0", info)
        text.configure(state="disabled")
        btn_row = ttk.Frame(dlg); btn_row.pack(fill="x", padx=10, pady=(0, 10))
        ttk.Button(btn_row, text=self._t["copy_link"],
                   command=lambda: self._copy_to_clipboard(GITHUB_URL)).pack(side="left")
        ttk.Button(btn_row, text=self._t["open_github"],
                   command=lambda: webbrowser.open(GITHUB_URL)).pack(side="left", padx=4)
        ttk.Button(btn_row, text=self._t["close"], command=dlg.destroy).pack(side="right")

    def _show_help(self):
        messagebox.showinfo(self._t["menu_help"], self._t["help_placeholder"])

    # ------------- tools -------------

    def _on_tool_change(self, _event=None):
        self._select_tool(self.tool_combo.current())

    def _select_tool(self, idx):
        if not self.tools or idx < 0:
            return
        self.current_tool = self.tools[idx]
        target = self.current_tool.get("target", "items")
        name = tr(self.current_tool["name"], self.lang)
        self.form_frame.configure(text=f"{self._t['params']} — {name}")
        for w in self.form_frame.winfo_children():
            w.destroy()
        self.param_widgets = {}
        self._build_form(self.current_tool.get("params", []))
        self._clear_preview()
        self._log("")
        self._log(f"[i] {name}: {tr(self.current_tool.get('description'), self.lang)}")
        hint = tr(self.current_tool.get("hint"), self.lang)
        if hint:
            self._log(f"[i] {hint}")

    def _build_form(self, params):
        row = 0
        for p in params:
            pid = p["id"]
            ttk.Label(self.form_frame, text=tr(p["label"], self.lang) + ":").grid(
                row=row, column=0, sticky="w", padx=(0, 6), pady=3)
            if p["type"] == "text":
                var = tk.StringVar(value=str(p.get("default", "")))
                ttk.Entry(self.form_frame, textvariable=var, width=30).grid(
                    row=row, column=1, sticky="we", pady=3)
                self.param_widgets[pid] = ("text", var)
            elif p["type"] == "textarea":
                txt = tk.Text(self.form_frame, height=8, width=40, font=("Consolas", 10))
                txt.insert("1.0", str(p.get("default", "")))
                txt.grid(row=row, column=1, sticky="nsew", pady=3)
                self.param_widgets[pid] = ("textarea", txt)
            elif p["type"] == "choice":
                var = tk.StringVar(value=str(p.get("default", "")))
                frame = ttk.Frame(self.form_frame)
                frame.grid(row=row, column=1, sticky="w", pady=3)
                for opt in p.get("options", []):
                    ttk.Radiobutton(frame, text=tr(opt["label"], self.lang),
                                    value=opt["value"], variable=var).pack(side="left", padx=(0, 8))
                self.param_widgets[pid] = ("choice", var)
            row += 1
        self.form_frame.columnconfigure(1, weight=1)

    # ------------- dir / files -------------

    def _pick_dir(self):
        d = filedialog.askdirectory(title=self._t["pick_dir"])
        if not d:
            return
        self.current_dir = d
        self.dir_label.configure(text=f"{self._t['pick_dir'].rstrip('.')}: {d}")
        self._reload_dir()
        self._refresh_list()

    def _reload_dir(self):
        self.all_entries = []
        self.visible_entries = []
        if not self.current_dir:
            self._refresh_list()
            return
        try:
            items = list(Path(self.current_dir).iterdir())
        except OSError as e:
            messagebox.showerror(self._t["error"], str(e))
            return
        for p in items:
            try: mtime = p.stat().st_mtime
            except OSError: mtime = 0
            self.all_entries.append({
                "name": p.name, "path": str(p), "is_dir": p.is_dir(),
                "ext": p.suffix.lower() if p.is_file() else "",
                "mtime": mtime, "checked": True,
            })
        self._update_type_filter_choices()
        self._apply_filters()

    def _update_type_filter_choices(self):
        exts = sorted({e["ext"] for e in self.all_entries if e["ext"]})
        values = [self._t["type_all"], self._t["type_dirs"], self._t["type_files"]]
        values += [f"{self._t['ext_prefix']}{e}" for e in exts]
        self.type_combo["values"] = values
        if self.type_var.get() not in values:
            self.type_combo.current(0)

    def _apply_filters(self):
        type_choice = self.type_var.get()
        sort_label = self.sort_combo.get()
        sort_key = next((k for k, v in SORT_CHOICES if self._t[v] == sort_label), "name_asc")
        filtered = []
        ext_prefix = self._t["ext_prefix"]
        for e in self.all_entries:
            if type_choice == self._t["type_all"]:
                pass
            elif type_choice == self._t["type_dirs"]:
                if not e["is_dir"]: continue
            elif type_choice == self._t["type_files"]:
                if e["is_dir"]: continue
            elif type_choice.startswith(ext_prefix):
                want = type_choice[len(ext_prefix):]
                if e["is_dir"] or e["ext"] != want: continue
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
        show_checks = self.current_tool and self.current_tool.get("target", "items") == "items"
        if not self.visible_entries:
            if not self.current_dir:
                self.files_list.insert("end", "(папка не выбрана)")
            else:
                self.files_list.insert("end", "(папка пуста)")
            self.count_label.configure(text="0 / 0")
            return
        for e in self.visible_entries:
            if show_checks:
                mark = "☑" if e["checked"] else "☐"
                self.files_list.insert("end", f"{mark} {e['name']}")
            else:
                self.files_list.insert("end", f"  {e['name']}")
        checked = sum(1 for e in self.visible_entries if e["checked"])
        self.count_label.configure(text=f"{checked} / {len(self.visible_entries)}")

    def _on_list_click(self, event):
        if self.current_tool and self.current_tool.get("target", "items") != "items":
            return
        idx = self.files_list.nearest(event.y)
        if idx < 0 or idx >= len(self.visible_entries): return
        self.visible_entries[idx]["checked"] = not self.visible_entries[idx]["checked"]
        self._refresh_list()

    def _check_all(self):
        for e in self.visible_entries: e["checked"] = True
        self._refresh_list()

    def _uncheck_all(self):
        for e in self.visible_entries: e["checked"] = False
        self._refresh_list()

    # ------------- run tool -------------

    def _collect_params(self):
        out = {}
        for pid, (ptype, widget) in self.param_widgets.items():
            if ptype == "textarea":
                out[pid] = widget.get("1.0", "end-1c")
            else:
                out[pid] = widget.get()
        return out

    def _build_ps_command(self, dry_run):
        tool = self.current_tool
        script = Path(tool["_dir"]) / tool["scripts"]["windows"]
        params = self._collect_params()
        parts = [f"& {_ps_quote(str(script))}"]
        parts.append(f"-Dir {_ps_quote(self.current_dir)}")
        for p in tool.get("params", []):
            pid = p["id"]
            if pid in params:
                flag = "-" + pid[0].upper() + pid[1:]
                parts.append(f"{flag} {_ps_quote(params[pid])}")
        target = tool.get("target", "items")
        if target != "folder":
            checked = [e["name"] for e in self.visible_entries if e["checked"]]
            if len(checked) != len(self.all_entries):
                files_part = ", ".join(_ps_quote(c) for c in checked)
                parts.append(f"-Files {files_part}")
        if dry_run:
            parts.append("-DryRun")
        return ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass",
                "-Command", " ".join(parts)]

    def _run_tool(self, dry_run):
        if not self.current_dir:
            messagebox.showwarning(self._t["error"], self._t["warn_no_dir"])
            return 1, ""
        target = self.current_tool.get("target", "items")
        if target != "folder":
            checked = [e for e in self.visible_entries if e["checked"]]
            if not checked:
                messagebox.showwarning(self._t["error"], self._t["warn_no_sel"])
                return 1, ""
        cmd = self._build_ps_command(dry_run)
        self._log("[cmd] " + cmd[-1])
        try:
            r = subprocess.run(cmd, capture_output=True, text=True,
                               encoding="utf-8", errors="replace")
        except OSError as e:
            return 1, f"(launch error) {e}"
        out = (r.stdout or "") + (r.stderr or "")
        if not out.strip():
            out = f"(no output, exit code {r.returncode})"
        return r.returncode, out

    def _on_preview(self):
        self._clear_preview()
        self._log("— " + self._t["preview"] + " —")
        code, out = self._run_tool(dry_run=True)
        self.preview_text.insert("end", out)
        last = out.strip().splitlines()[-1] if out.strip() else "(пусто)"
        self._log(f"[exit {code}] {last}")

    def _on_apply(self):
        target = self.current_tool.get("target", "items")
        name = tr(self.current_tool["name"], self.lang)
        if target == "folder":
            if not self.current_dir:
                messagebox.showwarning(self._t["error"], self._t["warn_no_dir"])
                return
            if not messagebox.askyesno(self._t["confirm"],
                    self._t["confirm_create"].format(name=name)):
                return
        else:
            checked = [e for e in self.visible_entries if e["checked"]]
            if not checked:
                messagebox.showwarning(self._t["error"], self._t["warn_no_sel"])
                return
            if not messagebox.askyesno(self._t["confirm"],
                    self._t["confirm_msg"].format(n=len(checked), name=name)):
                return
        self._log("— " + self._t["apply"] + " —")
        code, out = self._run_tool(dry_run=False)
        self._log(out)
        if code == 0:
            messagebox.showinfo(self._t["done"], self._t["done_msg"])
        else:
            messagebox.showwarning(self._t["error"], "Смотрите лог ниже.")
        self._reload_dir()

    # ------------- misc -------------

    def _clear_preview(self):
        self.preview_text.delete("1.0", "end")

    def _log(self, text):
        self.log_text.insert("end", text + "\n")
        self.log_text.see("end")


def main():
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()