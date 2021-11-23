import sys
import glob
import os
import shutil

# バッチファイルから渡された引数を格納したリストの取得
argvs = sys.argv

param_org_path = '../../input/config/config_box/'
param_dst_path = '../../input/config/'

if argvs[1] == 'HI':
    param_org_filename = 'config_hi.ini'
elif argvs[1] == 'LO':
    param_org_filename = 'config_lo.ini'
else:
    print("引数指定エラー")    

if os.path.exists(param_org_path):     # ディレクトリがある場合
    # オリジナルパラメータファイルがあるかを確認
    if os.path.isfile(param_org_path + param_org_filename):
        # パラメータフォルダに既にパラメータファイルがある場合は削除しておく
        if os.path.isfile(param_dst_path + 'config_hi.ini'):
            os.remove(param_dst_path + 'config_hi.ini')
        if os.path.isfile(param_dst_path + 'config_lo.ini'):
            os.remove(param_dst_path + 'config_lo.ini')
        # オリジナルパラメータをパラメータフォルダにコピー
        shutil.copyfile(param_org_path + param_org_filename, param_dst_path + param_org_filename)
    else:
        print("ファイルが見つかりません[" + param_org_path + param_org_filename + "]")        
else:
    print("ディレクトリが見つかりません[" + param_org_path + "]")