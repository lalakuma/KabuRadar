@echo off

rem '*******************************************************
rem ' 共通前処理実行
rem '*******************************************************

echo 共通前処理実行

rem '----------------------------------
rem ' kabuステーション起動
rem '----------------------------------
cd C:\Users\morino\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\kabu.com
start kabuステーション.appref-ms
timeout 30

rem 'Windows自動操作ツールを起動して株ステーションにログイン
start C:\tool\uwsc5302\UWSC.exe C:\tool\uwsc5302\kabucom_login.uws

rem '----------------------------------
rem ' 最新の株価を取得
rem '----------------------------------
cd C:\MorinoFolder\Python\KabuRadar\software\src

rem 'APIで最新の株価を取得してデータベースに保存
call C:\MorinoFolder\Python\KabuRadar\software\src\main_entry_price_one.py

rem '*******************************************************
rem ' 購入処理開始
rem '*******************************************************
echo TRADE実行

cd C:\MorinoFolder\Python\KabuRadar\software\src

rem '----------------------------------
rem ' スクリーニング1回目 高勝率検索
rem '----------------------------------
rem '高勝率低回転パラメータに変更 (勝率は高いがHit数が少ない)
call C:\MorinoFolder\Python\KabuRadar\software\src\main_param_chg.py HI

rem 'スクリーニング開始
call C:\MorinoFolder\Python\KabuRadar\software\src\main_analyze_all.py HI

rem 'LINE通知 ＆ auカブコム証券で売買
call C:\MorinoFolder\Python\KabuRadar\software\src\main_kabustation_trade.py HI

rem '-------------------------------------------
rem ' スクリーニング2回目 余った資金で低勝率検索
rem '-------------------------------------------
rem '低勝率高回転パラメータに変更 (勝率は低いがHit数が多い)
rem call C:\MorinoFolder\Python\KabuRadar\software\src\main_param_chg.py LO

rem 'スクリーニング開始
rem call C:\MorinoFolder\Python\KabuRadar\software\src\main_analyze_all.py LO

rem 'LINE通知 ＆ auカブコム証券で売買
rem call C:\MorinoFolder\Python\KabuRadar\software\src\main_kabustation_trade.py LO

rem '-------------------------------------------
rem ' 株ステーション終了
rem '-------------------------------------------
timeout 2
rem '株ステーションを終了
taskkill /IM KabuS.exe /F

rem start C:\MorinoFolder\Python\KabuRadar\software\bat\3.suspend.bat

exit

