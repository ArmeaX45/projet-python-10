@echo off
echo Recherche du navigateur...

:: 1. On essaie avec Chrome (Dossier Standard)
if exist "C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Google Chrome.lnk" (
    echo Chrome trouve ! Lancement...
    taskkill /F /IM chrome.exe >nul 2>&1
    "C:\Program Files\Google\Chrome\Application\chrome.exe" --allow-file-access-from-files "%~dp0index.html"
    exit
)

:: 2. On essaie avec Edge (Car je vois l'icone Edge sur ton image)
if exist "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" (
    echo Edge trouve ! Lancement...
    taskkill /F /IM msedge.exe >nul 2>&1
    "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" --allow-file-access-from-files "%~dp0index.html"
    exit
)

echo.
echo ERREUR : Je ne trouve ni Chrome ni Edge aux endroits habituels.
echo.
pause