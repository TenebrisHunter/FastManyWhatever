// ============================================================
//  FastManyWhatever — Tauri app entry
//  Автор: Ключенко М.А. (Омск, ОмГТУ, ИБа-261)
//  Версия: 0.1.0
// ============================================================

#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

pub mod instruments;

use instruments::add_affix::commands as add_affix_cmd;

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_opener::init())
        .plugin(tauri_plugin_dialog::init())
        .invoke_handler(tauri::generate_handler![
            add_affix_cmd::list_dir,
            add_affix_cmd::preview_affix,
            add_affix_cmd::rename_batch,
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}