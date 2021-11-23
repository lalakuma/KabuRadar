@echo off
rem '-------------------------------------------
rem ' 終了処理
rem '-------------------------------------------
timeout 2
rem '株ステーションを終了
taskkill /IM KabuS.exe /F

timeout 2
rem 'Windowsサスペンド
powercfg -h off
C:\WINDOWS\system32\rundll32.exe PowrProf.dll,SetSuspendState

exit

