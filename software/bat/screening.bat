@echo off



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
call C:\MorinoFolder\Python\KabuRadar\software\src\main_param_chg.py LO

rem 'スクリーニング開始
call C:\MorinoFolder\Python\KabuRadar\software\src\main_analyze_all.py LO

rem 'LINE通知 ＆ auカブコム証券で売買
call C:\MorinoFolder\Python\KabuRadar\software\src\main_kabustation_trade.py LO

