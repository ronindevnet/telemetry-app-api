@echo off
setlocal

rem === API de Telemetria - encerra o servidor ===
rem Encerra o processo que estiver escutando na porta da API (5000).

set "PORT=5000"

echo Procurando o servidor na porta %PORT% ...
set "FOUND="
for /f "tokens=5" %%p in ('netstat -ano ^| findstr ":%PORT% " ^| findstr LISTENING') do (
    echo Encerrando processo PID %%p ...
    taskkill /PID %%p /F >nul 2>&1
    set "FOUND=1"
)

if not defined FOUND (
    echo Nenhum servidor estava rodando na porta %PORT%.
) else (
    echo Servidor encerrado.
)

timeout /t 3 /nobreak >nul
endlocal
