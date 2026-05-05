@echo off
chcp 65001

rem '*******************************************************
rem ' 共通前処理実行
rem '*******************************************************

echo 共通前処理実行
cd C:\share\MorinoFolder\Python\KabuRadar\software\src

rem '----------------------------------
rem ' 最新の株価を取得 (決済には関係ないけど15:00以降の終値を取得する為)
rem '----------------------------------
echo 株価取得
rem 'APIで最新の株価を取得してデータベースに保存
python.exe C:\share\MorinoFolder\Python\KabuRadar\software\src\main_entry_price_replace_1day.py



exit

