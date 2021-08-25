import common_def as DEF

#################################################################
# 髭の長さを判定する（上髭が長いときは危険なので購入しないようにする為）
# 買い目線の時、現在値に長い上髭が出ている場合は買いNG（売買シグナルなし）とする
# 売り目線の時に現在値に長い下髭が出ている場合は売りNG（売買シグナルなし）とする
# 引数：mode        (MODE_BUY=買い判定、MODE_SELL=売り判定)
#     : i_open      始値
#     : i_high      高値
#     : i_low       安値
#     : i_close     終値(現在値)
# 戻り値：0=売買シグナルなし, 1=売買シグナルあり
#################################################################
def jdg_beard(sb_mode, i_open, i_high, i_low, i_close):
    sigsw_bread = 1

    # ローソクが陽線か陰線かを判別
    diff = i_close - i_open             # 始値と現在値の差分から実線の長さを設定
    if diff >= 0:
        line_kind = 1                   # ライン種別を陽線に設定
    else:
        line_kind = 0                   # ライン種別を陰線に設定

    # 買いシグナル判定
    if sb_mode == DEF.MODE_BUY:
        # 陽線の時
        if line_kind == 1:
            # 髭の長さを取得    
            line_upper = i_high - i_close          # 高値と現在値の差分を上髭に設定
            # 髭の条件をセット(とりあえず価格の2%とする)
            limit_beard = i_close * 0.02
       # 陰線の時
        else:
            # 髭の長さを取得    
            line_upper = i_high - i_open           # 高値と始値の差分を上髭に設定
            # 髭の条件をセット(とりあえず価格の2%とする)
            limit_beard = i_open * 0.02
        
        # 髭の方が長かったら売買なしとする
        if line_upper > limit_beard:
            sigsw_bread = 0    

    # 売りシグナル判定
    if sb_mode == DEF.MODE_SELL:
        # 陽線の時
        if line_kind == 1:
            # 髭の長さを取得    
            line_lower = i_open - i_low           # 始値と安値の差分を下髭に設定
            # 髭の条件をセット(とりあえず価格の2%とする)
            limit_beard = i_close * 0.02
       # 陰線の時
        else:
            # 髭の長さを取得    
            line_lower = i_close - i_low           # 終値と安値の差分を下髭に設定
            # 髭の条件をセット(とりあえず価格の2%とする)
            limit_beard = i_open * 0.02
        
        # 髭の方が長かったら売買なしとする
        if line_lower > limit_beard:
            sigsw_bread = 0    

    return sigsw_bread


def jdg_beard2(sb_mode, i_open, i_high, i_low, i_close):
    sigsw_bread = 1
    
    # 但し実態の長さが株価の2%以上の時に判定として使う。(2%は要調整)
    line_solid = abs(i_close - i_open)              # 始値と現在値の差分から実線の長さを設定

    # 買いシグナル判定
    if sb_mode == DEF.MODE_BUY:
        # ローソクの実態の大きさが終値の2%以下の時は処理しない。
        if line_solid >= (i_close * 0.02):
            if  i_close >= i_open:                      # 陽線の時
                # 陽線の実態よりも2倍以上の長い上髭がある時は購入しない
                line_upper = i_high - i_close           # 高値と現在値の差分を上髭に設定
                if line_upper > (line_solid * 2):
                    sigsw_bread = 0    
            else:                                       # 陰線の時
                # 陰線の実態よりも上髭が長いときは購入しない
                line_upper = i_high - i_open            # 高値と始値の差分を上髭の設定
                if line_upper > line_solid:
                    sigsw_bread = 0    
    # 売りシグナル判定
    elif sb_mode == DEF.MODE_SELL:
        # ローソクの実態の大きさが終値の2%以下の時は処理しない。
        if line_solid >= (i_close * 0.02):
            if  i_close >= i_open:                      # 陽線の時
                # 陽線の実態よりも2倍以上の長い上髭がある時は購入しない
                line_lower = i_open - i_low           # 高値と現在値の差分を下髭に設定
                if line_lower > line_solid:
                    sigsw_bread = 0    
            else:                                       # 陰線の時
                # 陰線の実態よりも上髭が長いときは購入しない
                line_lower = i_close - i_low            # 高値と始値の差分を上髭の設定
                if line_lower > (line_solid * 2):
                    sigsw_bread = 0    

    return sigsw_bread
