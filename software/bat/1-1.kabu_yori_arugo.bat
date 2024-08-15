@echo off

rem '*******************************************************
rem ' 共通前処理実行
rem '*******************************************************

echo 共通前処理実行

rem '----------------------------------
rem ' kabuステーション起動
rem '----------------------------------
cd C:\Users\morino\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\kabu.com
tasklist /FI "IMAGENAME eq KabuS.exe" 2>NUL | find /I /N "KabuS.exe">NUL
if "%ERRORLEVEL%"=="1" (
    start .\kabuステーション.appref-ms
    timeout 10

    rem 'Windows自動操作ツールを起動して株ステーションにログイン
    start C:\tool\uwsc5302\UWSC.exe C:\tool\uwsc5302\kabucom_login.uws
    timeout 30
)

rem '----------------------------------
rem ' 寄りアルゴを実行
rem '----------------------------------
rem 'KabuRadarアプリ起動
start C:\MorinoFolder\C#\yori_arugo\KabuRadar\KabuRadar\bin\Debug\net8.0-windows\KabuRadar.exe autostart

exit

