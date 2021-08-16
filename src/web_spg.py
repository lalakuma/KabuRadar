import time
import pandas as pd
import requests
from bs4 import BeautifulSoup
import sqlite3

dbname = ('KabuRadar.db')                       #データベース名.db拡張子で設定
cols_name = ['code', '銘柄名', '市場', '産業']
cols_price = ['日付', '始値', '高値', '安値', '終値', '出来高', '終値調整', 'code']

def get_brand(code):
    """
    証券コードからスクレイピング情報を取得し、Datafrrameにして返す関数
    """

    #確認くんで調べた自分のユーザーエージェント(現在のブラウザー)をコピペ ※環境に応じて書き直す
 #   headers = {"User-Agent": "Chrome/91.0.4472.77"}     # 自宅 PC
    headers = {"User-Agent": "Chrome/91.0.4472.114"}    # GS PC

    #取得する銘柄のURLを取得
    url = 'https://kabuoji3.com/stock/' + str(code) + '/2021/'

    #株価が存在しなければ例外処理でNoneを返す
    try:
        #取得したHTMLからBeautifulSoupオブジェクト作成
        response = requests.get(url, headers = headers)
        soup = BeautifulSoup(response.content, "html.parser")

        #証券コードを取得する
        code_name = soup.findAll("span", {"class":"jp"})[0]
        code_kind = soup.findAll("p", {"class":"dread"})[0]

        #ヘッダー(カラム)情報を取得する
        tag_thead_tr = soup.find('thead').find_all('tr')
        head_price = [h.text for h in tag_thead_tr[0].find_all('th')] 

        #株価データを取得し、Dataframe化する
        table = soup.findAll("table", {"class":"stock_table stock_data_table"})[0]
        tag_tbody_tr = table.findAll("tr")[1:]

        #テキストから銘柄情報を抽出
        head_name = ['code', '銘柄名', '市場', '産業']
        nametext = code_name.get_text()
        getcode =  nametext[:4]                                 # コードを取得
        getshamei =  nametext[4:]                               # 銘柄名を取得
        #取得テキストからカッコの位置を検索して市場と産業を抽出する
        kindtext = code_kind.get_text()                         
        pos_kakko_s = kindtext.find('（')
        pos_kakko_e = kindtext.find('）')
        getsijou =  kindtext[:pos_kakko_s]                      # 市場を取得
        getkind =  kindtext[pos_kakko_s + 1:pos_kakko_e]        # 産業を取得

        #銘柄情報のデータフレームを作成
        name = []
        name.append([getcode, getshamei.strip(), getsijou.strip(), getkind.strip()])
        df_name = pd.DataFrame(name, columns = head_name)

        #価格データを取得
        data = []
        for i in range(len(tag_tbody_tr)):
            data.append([d.text for d in tag_tbody_tr[i].find_all('td')])
        df_price = pd.DataFrame(data, columns = head_price)

        #codeカラムをassignでDataframeに新規追加する ※code_nameの最初の4桁までが証券コード
        df_price = df_price.assign(code=code_name.get_text()[:4])

        #デバッグ用。取得できたページを出力する。※本番コードでは不要
        print(url)

    except (ValueError, IndexError, AttributeError):
        return None, None

    return df_name, df_price

def brands_generator(code):
    """
    証券コードを生成し、取得した情報を結合する関数
    """

    #株価を入れる空のデータフレームを新規作成
    gen_name = pd.DataFrame(index=[], columns=cols_name)
    gen_price = pd.DataFrame(index=[], columns=cols_price)

    #生成した証券コードをスクレイピング関数へ渡す          
    brand_name, brand_price = get_brand(code)

    #情報が取得できていれば、情報を結合していく
    if brand_price is not None:
        gen_name = pd.concat([gen_name, brand_name]).reset_index(drop=True)                                  
        gen_price = pd.concat([gen_price, brand_price]).reset_index(drop=True)                                  

    return gen_name, gen_price

##########################
# 複数コード一括取得
##########################
def get_kabuka_bundle(code_sta, code_end):
    #データベースを作成
    db = sqlite3.connect(dbname, isolation_level=None)
    #株価を入れる空のデータフレームを新規作成
    df_name = pd.DataFrame(index=[], columns=cols_name)
    df_price = pd.DataFrame(index=[], columns=cols_price)
    df_name_all = df_name

    for rng in range(code_sta, code_end):          
        df_name, df_price = brands_generator(rng)
        
        # データあり(有効なコード)の時
        if df_name.empty is False:
            # 名前データを結合
            df_name_all = pd.concat([df_name_all, df_name]).reset_index(drop=True) 
            df_price.to_sql('tbl_' + str(rng), db, if_exists='replace', index=None, method='multi', chunksize=5000)
            
        time.sleep(1)

    # 登録するデータがある場合
    if df_name_all.empty is False:
        df_name_all.to_sql('tbl_name', db, if_exists='replace', index=None, method='multi')

    db.close()

##########################
# 1銘柄(期間)取得
##########################
def get_Kabuka_period():
    #データベースを作成
    db = sqlite3.connect(dbname, isolation_level=None)
    db.close()

##########################
# 1銘柄(最新1日)取得
##########################
def get_Kabuka_oneday():
    #株価を入れる空のデータフレームを新規作成
    df_name = pd.DataFrame(index=[], columns=cols_name)
    df_price = pd.DataFrame(index=[], columns=cols_price)
    # 'code', '銘柄名', '市場', '産業'
    df_name.loc[0] = ['9985', 'softbank', '東証1部', 'なんか']

    return df_name, df_price

