@echo off
chcp 65001

rem '*******************************************************
rem ' 共通前処理実行
rem '*******************************************************

echo 共通前処理実行
cd C:\share\MorinoFolder\Python\KabuRadar\software\src

rem '----------------------------------
rem ' 最新の株価を取得
rem '----------------------------------
echo 株価取得
rem 'APIで最新の株価を取得してデータベースに保存
python.exe C:\share\MorinoFolder\Python\KabuRadar\software\src\main_entry_price_replace_1day.py

rem '----------------------------------
rem ' スクリーニング 
rem '----------------------------------
python.exe C:\share\MorinoFolder\Python\KabuRadar\software\src\main_param_chg.py HI

python.exe C:\share\MorinoFolder\Python\KabuRadar\software\src\main_analyze_all.py HI

rem 'LINE通知 ＆ auカブコム証券で売買
python.exe C:\share\MorinoFolder\Python\KabuRadar\software\src\main_kabustation_trade.py HI

exit

