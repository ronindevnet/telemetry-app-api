@echo off
setlocal

rem === API de Telemetria - inicializador ===
rem Fica na raiz do back-end (telemetry_app_api), ao lado do app.py.

set "API=%~dp0"
set "PY=%API%.venv\Scripts\python.exe"
set "DOCS=http://127.0.0.1:5000/openapi/swagger"

rem --- Primeira execucao: cria o ambiente virtual e instala as dependencias ---
if not exist "%PY%" (
    echo Primeira execucao: criando o ambiente virtual e instalando as dependencias...
    pushd "%API%"
    python -m venv .venv
    "%PY%" -m pip install -r requirements.txt
    popd
    echo.
)

rem --- Inicia a API em uma janela propria ---
echo Iniciando a API em http://127.0.0.1:5000 ...
start "Telemetria API" /D "%API%" "%PY%" app.py

rem --- Aguarda a API subir e abre a documentacao (Swagger) no navegador ---
echo Aguardando a API iniciar...
timeout /t 4 /nobreak >nul

echo Abrindo a documentacao da API no navegador...
start "" "%DOCS%"

echo.
echo Pronto! Para PARAR o servidor, feche a janela "Telemetria API" ou execute stop.bat.
timeout /t 4 /nobreak >nul
endlocal
