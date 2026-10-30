
chcp 65001 >nul
cd /d "%~dp0"

for /l %%i in (1,1,10) do (
    <nul set /p="Шифр: " > "Задание %%i.txt"
)

echo Готово! Создано 10 файлов.
pause
