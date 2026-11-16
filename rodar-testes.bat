@echo off
rem LaCakes - roda os testes automatizados (pytest) e mostra a cobertura do codigo.
rem De dois cliques neste arquivo. Pode rodar com o sistema aberto: os testes usam um banco temporario.
setlocal
cd /d "%~dp0"
chcp 65001 >nul
if not exist ".venv\Scripts\python.exe" (
  echo.
  echo  O ambiente ainda nao foi criado. Rode primeiro o iniciar.bat ^(ou iniciar-com-banco-limpo.bat^)
  echo  pelo menos uma vez e depois rode este arquivo de novo.
  echo.
  pause
  exit /b 1
)
echo.
echo  Rodando os testes automatizados do LaCakes...
echo.
".venv\Scripts\python.exe" -m pytest --cov=app -o addopts=""
echo.
pause
