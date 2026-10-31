// ============================================================
//  FastManyWhatever — add_affix: pure logic (no Tauri deps)
//  Автор: Ключенко М.А. (Омск, ОмГТУ, ИБа-261)
//  Версия: 0.1.0
// ============================================================
//
// Чистый Rust: std + serde. Может переиспользоваться из CLI.

use serde::{Deserialize, Serialize};
use std::fs;
use std::path::Path;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DirEntry {
    pub name: String,
    pub path: String,
    pub is_dir: bool,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "lowercase")]
pub enum AffixPosition {
    Prefix,
    Suffix,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct RenameOp {
    pub old_path: String,
    pub new_name: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct RenameResult {
    pub ok: Vec<String>,
    pub skipped: Vec<String>,
    pub errors: Vec<String>,
}

/// Список файлов и папок в директории (не рекурсивно).
pub fn list_dir(dir: &str) -> Result<Vec<DirEntry>, String> {
    let path = Path::new(dir);
    if !path.is_dir() {
        return Err(format!("Not a directory: {}", dir));
    }
    let mut entries = Vec::new();
    let read = fs::read_dir(path).map_err(|e| format!("Cannot read dir: {}", e))?;
    for entry in read {
        let entry = entry.map_err(|e| format!("Dir entry error: {}", e))?;
        let meta = entry.metadata().map_err(|e| format!("Metadata error: {}", e))?;
        let name = entry.file_name().to_string_lossy().to_string();
        let full_path = entry.path().to_string_lossy().to_string();
        entries.push(DirEntry { name, path: full_path, is_dir: meta.is_dir() });
    }
    entries.sort_by(|a, b| {
        b.is_dir.cmp(&a.is_dir)
            .then_with(|| a.name.to_lowercase().cmp(&b.name.to_lowercase()))
    });
    Ok(entries)
}

/// Разделить имя на (stem, ext), корректно для .git, .env, и обычных файлов.
fn split_name(name: &str) -> (&str, &str) {
    if name.starts_with('.') && !name[1..].contains('.') {
        return (name, "");
    }
    match name.rfind('.') {
        Some(idx) if idx > 0 => (&name[..idx], &name[idx..]),
        _ => (name, ""),
    }
}

/// Вычислить новое имя: добавить word в начало или в конец.
pub fn compute_new_name(name: &str, is_dir: bool, word: &str, pos: &AffixPosition) -> String {
    if is_dir {
        return match pos {
            AffixPosition::Prefix => format!("{}{}", word, name),
            AffixPosition::Suffix => format!("{}{}", name, word),
        };
    }
    let (stem, ext) = split_name(name);
    match pos {
        AffixPosition::Prefix => format!("{}{}{}", word, stem, ext),
        AffixPosition::Suffix => format!("{}{}{}", stem, word, ext),
    }
}

/// Проверка на недопустимые в Windows символы.
pub fn validate_name(name: &str) -> Result<(), String> {
    const FORBIDDEN: &[char] = &['\\', '/', ':', '*', '?', '"', '<', '>', '|'];
    if name.is_empty() {
        return Err("empty name".to_string());
    }
    for ch in FORBIDDEN {
        if name.contains(*ch) {
            return Err(format!("forbidden char: {}", ch));
        }
    }
    Ok(())
}

/// Пакетное переименование. Конфликты (цель существует) — пропускаем.
pub fn rename_batch(ops: Vec<RenameOp>) -> RenameResult {
    let mut ok = Vec::new();
    let mut skipped = Vec::new();
    let mut errors = Vec::new();
    for op in ops {
        let old_path = Path::new(&op.old_path);
        if !old_path.exists() {
            errors.push(format!("not found: {}", op.old_path));
            continue;
        }
        if let Err(e) = validate_name(&op.new_name) {
            errors.push(format!("invalid name '{}': {}", op.new_name, e));
            continue;
        }
        let parent = match old_path.parent() {
            Some(p) => p,
            None => {
                errors.push(format!("no parent: {}", op.old_path));
                continue;
            }
        };
        let new_path = parent.join(&op.new_name);
        if new_path.exists() && new_path != old_path {
            skipped.push(format!("exists: {}", new_path.to_string_lossy()));
            continue;
        }
        match fs::rename(old_path, &new_path) {
            Ok(_) => ok.push(op.new_name),
            Err(e) => errors.push(format!("rename '{}': {}", op.old_path, e)),
        }
    }
    RenameResult { ok, skipped, errors }
}