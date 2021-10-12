# coding: utf-8
import configparser
import os
import errno

config_ini_path = '../../Input/config/config.ini'

# セクション名称定義
CONF_SEC_SCR = 'SCREENING'
CONF_SEC_SHUUKEI = 'SHUUKEI'
CONF_SEC_ENTRY = 'ENTRY'
CONF_SEC_KABUSAPI = 'KABUSAPI'
CONF_SEC_DATABASE = 'DATABASE'

# キー名称定義
CONF_KEY_JDG_CAND = 'SCR_JDG_CAND'
CONF_KEY_JDG_IND = 'SCR_JDG_IND'
CONF_KEY_JDG_MOV = 'SCR_JDG_MOV'
CONF_KEY_JDG_RSI = 'SCR_JDG_RSI'
CONF_KEY_JDG_MACD = 'SCR_JDG_MACD'
CONF_KEY_JDG_BRK = 'SCR_JDG_BRK'
CONF_KEY_JDG_BERD = 'SCR_JDG_BERD'

CONF_KEY_SCR_SELLBUY = 'SCR_SELLBUY'
CONF_KEY_SCR_EXEC_MODE = 'SCR_EXEC_MODE'
CONF_KEY_SCR_PAST_PERIOD = 'SCR_PAST_PERIOD'
CONF_KEY_SCR_SELL_PERIOD = 'SCR_SELL_PERIOD'
CONF_KEY_SCR_BREAK_PERIOD = 'SCR_BREAK_PERIOD'
CONF_KEY_SCR_BREAK_OFSET = 'SCR_BREAK_OFSET'
CONF_KEY_SCR_MACD_OFSET = 'SCR_MACD_OFSET'
CONF_KEY_SCR_LINEAVE = 'SCR_LINEAVE'
CONF_KEY_SCR_RSI_MAX = 'SCR_RSI_MAX'
CONF_KEY_SCR_RSI_BORDER = 'SCR_RSI_BORDER'
CONF_KEY_SCR_RSI_PER = 'SCR_RSI_PER'
CONF_KEY_SCR_RSI_PERIOD = 'SCR_RSI_PERIOD'
CONF_KEY_SCR_IND_CODE = 'SCR_IND_CODE'

CONF_KEY_PATH_SHUUKEI = 'PATH_SHUUKEI'
CONF_KEY_PATH_HONBAN = 'PATH_HONBAN'
CONF_KEY_PATH_CODESET = 'PATH_CODESET'
CONF_KEY_PATH_DB = 'PATH_DB'

CONF_KEY_API_PASSWD = 'API_PASSWD'

CONF_KEY_TRD_PASSWD = 'TRD_PASSWD'
##############################################
#   CODE設定情報登録用のパスを取得
##############################################
def get_config(section, key):
    # iniファイルの読み込み
    config_ini = configparser.ConfigParser()

    # 指定したiniファイルが存在しない場合、エラー発生
    if not os.path.exists(config_ini_path):
        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), config_ini_path)

    config_ini.read(config_ini_path, encoding='utf-8')

    # [ENTRY]の「PATH_CODESET」キーの値を取得
    read_conf = config_ini[section]
    path_pf = read_conf.get(key)

    # 結果表示
    return path_pf


##############################################
#   CODE設定情報登録用のパスを取得
##############################################
def get_codeset_path():
    # iniファイルの読み込み
    config_ini = configparser.ConfigParser()

    # 指定したiniファイルが存在しない場合、エラー発生
    if not os.path.exists(config_ini_path):
        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), config_ini_path)

    config_ini.read(config_ini_path, encoding='utf-8')

    # [ENTRY]の「PATH_CODESET」キーの値を取得
    read_conf = config_ini['ENTRY']
    path_pf = read_conf.get('PATH_CODESET')

    # 結果表示
    return path_pf

##############################################
#   集計ファイル作成用元データのパスを取得
##############################################
def get_shuukei_path():
    # iniファイルの読み込み
    config_ini = configparser.ConfigParser()

    # 指定したiniファイルが存在しない場合、エラー発生
    if not os.path.exists(config_ini_path):
        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), config_ini_path)

    config_ini.read(config_ini_path, encoding='utf-8')

    # [ULTRAMAN]の「Skil」キーの値を取得
    read_ultraman = config_ini['SHUUKEI']
    shuukei_path = read_ultraman.get('PATH')

    # 結果表示
    return shuukei_path

##############################################
#   集計ファイル作成用元データのパスを取得
##############################################
def get_kabukomuApiConfig():
    # iniファイルの読み込み
    config_ini = configparser.ConfigParser()

    # 指定したiniファイルが存在しない場合、エラー発生
    if not os.path.exists(config_ini_path):
        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), config_ini_path)

    config_ini.read(config_ini_path, encoding='utf-8')
    read_kabukomu = config_ini['KABUSAPI']

    # 結果表示
    return read_kabukomu
