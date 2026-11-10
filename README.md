# FastManyWhatever

Массовое создание и переименование файлов и папок — по правилу или по списку,
без регулярок и командной строки.
Bulk creation and renaming of files and folders — by rule or by list,
no regex, no command line.
批量创建和重命名文件和文件夹 — 按规则或按列表,无需正则表达式或命令行。

---

## Что это? / What is it? / 这是什么？

**RU.** Утилита для тех, кому нужно «создать 39 папок по списку из Excel»,
«переименовать партию файлов по шаблону», «убрать лишнее слово из имён».
Одно окно: слева — содержимое папки с фильтрами, справа — параметры
инструмента, предпросмотр и кнопка «Применить». Каждый инструмент можно
запустить и отдельно через PowerShell-скрипт.

**EN.** A tool for those who need to "create 39 folders from an Excel list",
"rename a batch of files by a template", "remove a redundant word from names".
One window: left — folder contents with filters, right — tool parameters,
preview, and an "Apply" button. Every tool can also be run standalone as a
PowerShell script.

**ZH.** 适用于需要"根据 Excel 列表创建 39 个文件夹"、"按模板批量重命名文件"、
"从名称中删除多余单词"的场景。单一窗口:左侧为带过滤器的文件夹内容,
右侧为工具参数、预览和"应用"按钮。每个工具也可通过 PowerShell 脚本独立运行。

---

## Возможности / Features / 功能

**Создать по правилу / Create by rule / 按规则创建**
Префикс + счётчик (от/до/шаг/формат) + суффикс + расширение. Файлы или папки.

**Создать файлы по списку / Create files by list / 按列表创建文件**
Каждая строка = отдельный файл.

**Создать папки по списку / Create folders by list / 按列表创建文件夹**
Каждая строка = отдельная папка.

**Добавить строку или слово / Add prefix/suffix / 添加前缀或后缀**
К выбранным файлам и папкам.

**Удалить подстроку / Remove substring / 删除子串**
Все вхождения из выбранных имён.

**Предпросмотр / Preview / 预览**
Что будет сделано, до применения.

**Лог / Log / 日志**
Результат + копирование.

**Темы и языки / Themes and languages / 主题和语言**
Светлая/тёмная, RU/EN.

---

## Стек / Stack / 技术栈

| Компонент / Component / 组件 | Технология / Technology / 技术 |
|---|---|
| GUI | Python 3.10+ + Tkinter |
| Инструменты / Tools | PowerShell (`.ps1`) |
| Хранение настроек / Config | JSON (`meta.json` на инструмент) |
| Упаковка / Packaging | PyInstaller (portable `.exe`) |
| Лицензия / License | MIT |

---

## Установка / Installation / 安装

- [Русский](INSTALL_RU.txt)
- [English](INSTALL_EN.txt)
- [中文](INSTALL_ZH.txt)

---

## Структура проекта / Project structure / 项目结构

- `gui/app.py` — Tkinter-интерфейс (меню, форма, предпросмотр, лог)
- `instruments/add-affix/` — добавить слово в начало/конец имён
- `instruments/create-by-rule/` — создать файлы/папки по правилу
- `instruments/create-files-list/` — создать файлы по списку
- `instruments/create-folders-list/` — создать папки по списку
- `instruments/remove-substring/` — удалить подстроку из имён
- В каждой папке `instruments/<id>/`:
  - `meta.json` — паспорт инструмента (имя, поля, target)
  - `tool.ps1` — сам инструмент (PowerShell)
- `README.md`, `DESCRIPTION.txt`, `TODO.txt`
- `INSTALL_RU.txt`, `INSTALL_EN.txt`, `INSTALL_ZH.txt`
- `LICENSE`

Новый инструмент = новая папка с `meta.json` и `tool.ps1`.
GUI читает `meta.json` и строит форму сам — код Python менять не нужно.

---

## Запуск / Run / 运行

    python -m gui.app

Отдельный инструмент / Standalone tool / 独立工具:

    powershell -NoProfile -ExecutionPolicy Bypass -Command "& '.\instruments\add-affix\tool.ps1' -Dir 'D:\photos' -Word '_old' -Pos suffix -DryRun"

---

## Лицензия / License / 许可证

MIT. См. [LICENSE](LICENSE).

---

## Авторы / Authors / 作者

Ключенко М.А.
Омск, ОмГТУ, ИБа-261, АНО ЦО ДО «Махаон», 2026

GitHub: [TenebrisHunter/FastManyWhatever](https://github.com/TenebrisHunter/FastManyWhatever)