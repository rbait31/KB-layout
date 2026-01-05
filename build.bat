@echo off
echo Установка зависимостей...
pip install -r requirements.txt

echo.
echo Создание исполняемого файла...
pyinstaller --onefile --windowed --name "kb-layout" main.py

echo.
echo Готово! Исполняемый файл находится в папке dist\kb-layout.exe
pause
