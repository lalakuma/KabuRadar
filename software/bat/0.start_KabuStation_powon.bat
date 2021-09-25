@echo off

cd C:\Users\morino\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\kabu.com
start kabuステーション.appref-ms

timeout 60

rem 'Windows自動操作ツールを起動して株ステーションにログイン
start C:\tool\uwsc5302\UWSC.exe C:\tool\uwsc5302\kabucom_login.uws

timeout 50

rem 'APIで最新の株価を取得してデータベースに保存
call C:\MorinoFolder\Python\KabuRadar\src\main_entry_price.py

rem '株ステーションを終了
start C:\MorinoFolder\Python\KabuRadar\bat\end_KabuStation.bat

timeout 10

rem 'Windowsサスペンド
powercfg -h off
C:\WINDOWS\system32\rundll32.exe PowrProf.dll,SetSuspendState