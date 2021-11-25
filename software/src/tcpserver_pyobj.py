# -*- coding : UTF-8 -*-

# 0.ライブラリのインポートと変数定義
import socket
import pickle

server_ip = "192.168.100.101"
server_port = 15001
listen_num = 5
buffer_size = 1024

# 1.ソケットオブジェクトの作成
tcp_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# 2.作成したソケットオブジェクトにIPアドレスとポートを紐づける
tcp_server.bind((server_ip, server_port))

# 3.作成したオブジェクトを接続可能状態にする
tcp_server.listen(listen_num)

# 4.ループして接続を待ち続ける
while True:
    # 5.クライアントと接続する
    client,address = tcp_server.accept()
    print("[*] Connected!! [ Source : {}]".format(address))

    full_msg = b''
    while True:
        msg = client.recv(1024)
        if len(msg) <= 0:
            break
        full_msg += msg
    d = pickle.loads(full_msg)
    print(d)

    # 8.接続を終了させる
    client.close()