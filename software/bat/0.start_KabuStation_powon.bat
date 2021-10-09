@echo off

cd C:\Users\morino\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\kabu.com
start kabuステーション.appref-ms
timeout 30

rem 'Windows自動操作ツールを起動して株ステーションにログイン
start C:\tool\uwsc5302\UWSC.exe C:\tool\uwsc5302\kabucom_login.uws
timeout 30

cd C:\MorinoFolder\Python\KabuRadar\software\bat

rem 'APIで最新の株価を取得してデータベースに保存
rem start C:\MorinoFolder\Python\KabuRadar\software\src\main_entry_price_one.py

rem 'スクリーニング開始
call C:\MorinoFolder\Python\KabuRadar\software\src\main_analyze_all.py

rem 'LINE通知 ＆ auカブコム証券で売買
call C:\MorinoFolder\Python\KabuRadar\software\src\main_kabustation_trade.py

timeout 1800

rem 'LINE通知 ＆ auカブコム証券で売買
call C:\MorinoFolder\Python\KabuRadar\software\src\main_kabustation_trade.py

rem '株ステーションを終了
taskkill /IM KabuS.exe /F

timeout 3

rem 'Windowsサスペンド
powercfg -h off
C:\WINDOWS\system32\rundll32.exe PowrProf.dll,SetSuspendState

