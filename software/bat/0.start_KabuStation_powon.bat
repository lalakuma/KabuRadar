@echo off

cd C:\Users\morino\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\kabu.com
start kabuステーション.appref-ms
timeout 30

rem 'Windows自動操作ツールを起動して株ステーションにログイン
start C:\tool\uwsc5302\UWSC.exe C:\tool\uwsc5302\kabucom_login.uws
timeout 30

cd C:\MorinoFolder\Python\KabuRadar\software\bat

rem 'APIで最新の株価を取得してデータベースに保存
call C:\MorinoFolder\Python\KabuRadar\software\src\main_entry_price_one.py

rem '----------------------------------
rem ' スクリーニング1回目 高勝率検索
rem '----------------------------------
rem '高勝率低回転パラメータに変更 (勝率は高いがHit数が少ない)
call C:\MorinoFolder\Python\KabuRadar\software\src\main_param_chg.py HI

rem 'スクリーニング開始
call C:\MorinoFolder\Python\KabuRadar\software\src\main_analyze_all.py HI

rem 'LINE通知 ＆ auカブコム証券で売買
call C:\MorinoFolder\Python\KabuRadar\software\src\main_kabustation_trade.py

rem '-------------------------------------------
rem ' スクリーニング2回目 余った資金で低勝率検索
rem '-------------------------------------------
rem '低勝率高回転パラメータに変更 (勝率は低いがHit数が多い)
call C:\MorinoFolder\Python\KabuRadar\software\src\main_param_chg.py LO

rem 'スクリーニング開始
call C:\MorinoFolder\Python\KabuRadar\software\src\main_analyze_all.py LO

rem 'LINE通知 ＆ auカブコム証券で売買
call C:\MorinoFolder\Python\KabuRadar\software\src\main_kabustation_trade.py

timeout 1800

rem '全ての持ち株を翌日の寄り付きで決済注文
call C:\MorinoFolder\Python\KabuRadar\software\src\main_kabustation_kessai.py

rem '株ステーションを終了
taskkill /IM KabuS.exe /F

timeout 3

rem 'Windowsサスペンド
powercfg -h off
C:\WINDOWS\system32\rundll32.exe PowrProf.dll,SetSuspendState

