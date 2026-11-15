@echo off
rem LaCakes - sobe o sistema com um comando (Windows). De dois cliques neste arquivo ou rode: iniciar.bat
rem Opcional: iniciar.bat --recriar  (apaga os pedidos e volta o banco ao estado inicial)
setlocal
cd /d "%~dp0"
chcp 65001 >nul

if not defined PORTA set "PORTA=5000"
where py >nul 2>nul && (set "PY=py -3") || (set "PY=python")

if not exist ".venv\Scripts\python.exe" (
  echo [1/3] Criando ambiente virtual...
  %PY% -m venv .venv || goto erro_python
)

echo [2/3] Instalando dependencias...
".venv\Scripts\python.exe" -m pip install -q --disable-pip-version-check -r requirements.txt || goto erro_pip

echo [3/3] Preparando o banco de dados...
".venv\Scripts\python.exe" -m app.seed %1 || goto erro_banco

if not defined LACAKES_SEM_NAVEGADOR start "" "http://127.0.0.1:%PORTA%"
".venv\Scripts\python.exe" run.py
goto fim

:erro_python
echo.
echo ERRO: Python 3.10 ou mais novo nao foi encontrado. Instale em https://www.python.org/downloads/
echo (marque a opcao "Add python.exe to PATH" durante a instalacao) e rode este arquivo de novo.
goto fim
:erro_pip
echo.
echo ERRO: nao foi possivel instalar as dependencias. Verifique a conexao com a internet e tente de novo.
goto fim
:erro_banco
echo.
echo ERRO: nao foi possivel preparar o banco de dados. Veja a mensagem acima.
:fim
pause
