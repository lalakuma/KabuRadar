########################################################
# エクセルから銘柄コードを読み込む
########################################################
import pandas as pd

df = pd.read_excel('XLS/銘柄コード.xlsx',index_col=0)
#df = pd.read_excel('C:/MorinoFolder/Python/KabuRadar/銘柄コード.xlsx',index_col=0)
print(df)