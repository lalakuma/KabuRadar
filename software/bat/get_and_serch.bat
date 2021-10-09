@echo off

rem 'APIで最新の株価を取得してデータベースに保存
call E:\KabuRadar\software\src\main_entry_price_one.py

rem 'APIで最新の株価を取得してデータベースに保存
call E:\KabuRadar\software\src\main_analyze_all.py

rem 'exit /B