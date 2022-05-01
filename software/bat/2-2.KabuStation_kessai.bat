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
timeout 20

rem 'Windows自動操作ツールを起動して株ステーションにログイン
start C:\tool\uwsc5302\UWSC.exe C:\tool\uwsc5302\kabucom_login.uws
timeout 30

rem '----------------------------------
rem ' 最新の株価を取得 (決済には関係ないけど15:00以降の終値を取得する為)
rem '----------------------------------
cd C:\MorinoFolder\Python\KabuRadar\software\src
echo 株価取得
rem 'APIで最新の株価を取得してデータベースに保存
call C:\MorinoFolder\Python\KabuRadar\software\src\main_entry_kabukom_price.py

rem '*******************************************************
rem ' 決済処理開始
rem '*******************************************************
echo TRADE実行
rem '----------------------------------
rem '全ての持ち株を翌日の寄り付きで決済注文
rem '----------------------------------
rem 'call C:\MorinoFolder\Python\KabuRadar\software\src\main_kabustation_kessai.py

rem '-------------------------------------------
rem ' 株ステーション終了
rem '-------------------------------------------
timeout 2
rem '株ステーションを終了
taskkill /IM KabuS.exe /F

rem start C:\MorinoFolder\Python\KabuRadar\software\bat\3.suspend.bat


exit

