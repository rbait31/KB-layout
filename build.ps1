Write-Host "Установка зависимостей..." -ForegroundColor Green
pip install -r requirements.txt

Write-Host ""
Write-Host "Создание исполняемого файла..." -ForegroundColor Green
pyinstaller --onefile --windowed --name "kb-layout" main.py

Write-Host ""
Write-Host "Готово! Исполняемый файл находится в папке dist\kb-layout.exe" -ForegroundColor Green
Read-Host "Нажмите Enter для выхода"
