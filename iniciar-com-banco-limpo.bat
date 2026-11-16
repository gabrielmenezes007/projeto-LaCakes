@echo off
rem LaCakes - sobe o sistema com o banco LIMPO (apaga pedidos e contas criadas nos testes).
rem De dois cliques neste arquivo. Para manter os dados, use o iniciar.bat.
cd /d "%~dp0"
echo.
echo  Atencao: os pedidos e contas criados nos testes serao apagados.
echo  O cardapio e as contas de teste voltam ao estado inicial.
echo.
call "%~dp0iniciar.bat" --recriar
