import subprocess
import datetime
import time
import logging

#----------------------------------------
# LOG設定
#----------------------------------------
sth = logging.StreamHandler()
flh = logging.FileHandler('../../output/log/debug.log')
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO,
                    handlers=[sth, flh])
logger = logging.getLogger(__name__)
logger.info("処理 main_kabu_launcher 開始")

#----------------------------------------
# 指定の時間帯であれば取引を実行する
#----------------------------------------
dt = datetime.datetime.now()
tm = dt.time()

# 14:00～14：59の間に実行された場合はエントリー処理を行う
if tm >= datetime.time(11,30,0) and tm <= datetime.time(12,00,0):
    logger.info("2-1.kabu_screening_trade.bat開始")
    # 「KABUステーション起動、株価取得、スクリーニング、株購入」バッチファイル実行
    subprocess.run(r"C:\MorinoFolder\Python\KabuRadar\software\bat\2-1.kabu_screening_trade.bat")
    logger.info("2-1.kabu_screening_trade.bat完了")

# 15:00～15：30の間に実行された場合はエントリー処理を行う
elif tm >= datetime.time(14,00,0) and tm <= datetime.time(14,30,0):
    logger.info("2-2.KabuStation_kessai.bat開始")
    # 「KABUステーション起動、株価取得、株決済」バッチファイル実行
    subprocess.run(r"C:\MorinoFolder\Python\KabuRadar\software\bat\2-2.KabuStation_kessai.bat")
    logger.info("2-2.KabuStation_kessai.bat完了")

# 15:00～15：30の間に実行された場合はエントリー処理を行う
elif tm >= datetime.time(15,00,0) and tm <= datetime.time(15,30,0):
    logger.info("2-3.GetKabuka.bat開始")
    # 「KABUステーション起動、株価取得、株決済」バッチファイル実行
    subprocess.run(r"C:\MorinoFolder\Python\KabuRadar\software\bat\2-3.GetKabuka.bat")
    logger.info("2-3.GetKabuka.bat完了")

