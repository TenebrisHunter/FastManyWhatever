// ============================================================
//  FastManyWhatever — add_affix: Tauri command wrappers
//  Автор: Ключенко М.А. (Омск, ОмГТУ, ИБа-261)
//  Версия: 0.1.0
// ============================================================
//
// Тонкие обёртки над logic.rs. Никакой бизнес-логики здесь.

use super::logic::{self, AffixPosition, DirEntry, RenameOp, RenameResult};

#[tauri::command]
pub fn list_dir(path: String) -> Result<Vec<DirEntry>, String> {
    logic::list_dir(&path)
}

#[tauri::command]
pub fn preview_affix(
    names: Vec<String>,
    dirs: Vec<bool>,
    word: String,
    position: AffixPosition,
) -> Result<Vec<String>, String> {
    if word.is_empty() {
        return Err("word is empty".to_string());
    }
    let results = names
        .iter()
        .zip(dirs.iter())
        .map(|(name, is_dir)| logic::compute_new_name(name, *is_dir, &word, &position))
        .collect();
    Ok(results)
}

#[tauri::command]
pub fn rename_batch(ops: Vec<RenameOp>) -> RenameResult {
    logic::rename_batch(ops)
}