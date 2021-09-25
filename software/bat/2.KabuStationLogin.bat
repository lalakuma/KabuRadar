@echo off

timeout 10

rem 'Windows自動操作ツールを起動して株ステーションにログイン
start C:\tool\uwsc5302\UWSC.exe C:\tool\uwsc5302\kabucom_login.uws

timeout 50

rem 'APIで最新の株価を取得してデータベースに保存
rem call C:\MorinoFolder\Python\KabuRadar\src\main_entry_price.py

rem '株ステーションを終了
start C:\MorinoFolder\Python\KabuRadar\bat\end_KabuStation.bat

rem 'PCをシャットダウン 　
rem 'PC通常使用の妨げになるのでシャットダウンはスケジュールに任せる
rem call C:\MorinoFolder\Python\KabuRadar\bat\pc_shutdown.bat

rem 'exit /B