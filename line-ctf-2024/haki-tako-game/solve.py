from socket import create_connection  # ソケットAPIを使ってTCP接続を作成するための関数をインポート
import itertools  # 効率的なループ操作のためのイテレータ生成関数を提供するモジュール
import binascii  # バイナリデータとASCII文字列間の変換を行う関数を提供するモジュール
import struct  # バイト列とPythonのデータ構造とを相互に変換する関数を提供するモジュール
import json  # JSONエンコードおよびデコードのためのモジュール
import math  # 数学的関数を提供するモジュール

# ネットワーク通信を管理するためのクラス
class Tube:
    def __init__(s, host, port, debug=True):  # 初期化メソッド
        s.host = host  # ホストアドレスを設定
        s.port = port  # ポート番号を設定
        s.sock = create_connection((host, port))  # 指定したホストとポートでTCP接続を開始
        s.debug = debug  # デバッグモードの設定

    def recv(s, size=1024) -> bytes:  # 指定サイズのデータを受信するメソッド
        buf = s.sock.recv(size)  # ソケットからデータを受信
        if s.debug:  # デバッグモードが有効な場合
            print(f"[Tube#recv] {buf=}")  # 受信データを表示
        return buf  # 受信したデータを返す

    def recv_until(s, expected: bytes) -> bytes:  # 特定のバイト列が受信されるまでデータを読み続けるメソッド
        buf = b""  # 受信データを格納するためのバイト列を初期化
        while True:  # 無限ループ
            buf += s.sock.recv(1)  # 1バイトずつデータを受信してバッファに追加
            if expected in buf:  # 期待されるバイト列がバッファに含まれているかチェック
                break  # 含まれていればループを抜ける
        if s.debug:  # デバッグモードが有効な場合
            print(f"[Tube#recv_until] {buf=}")  # 受信データを表示
        return buf  # 受信したデータを返す

    def send(s, buf: bytes):  # バイト列データを送信するメソッド
        if s.debug:  # デバッグモードが有効な場合
            print(f"[Tube#send] {buf=}")  # 送信データを表示
        s.sock.send(buf)  # ソケット経由でデータを送信

    def send_line(s, buf: bytes):  # バイト列データに改行を追加して送信するメソッド
        s.send(buf + b"\n")  # 送信データに改行を追加してsendメソッドを呼び出す

    def close(s):  # ソケット接続を閉じるメソッド
        s.sock.close()  # ソケットを閉じる
        if s.debug:  # デバッグモードが有効な場合
            print("[Tube#close] closed")  # 接続閉鎖のメッセージを表示

# 主な処理を実行する関数
def main():
    tube = Tube("0.0.0.0", "11223")  # Tubeインスタンスを作成してサーバーに接続

    def recv():  # サーバーからJSON形式のデータを受信してデコードする関数
        return json.loads(tube.recv(16384).strip())  # 受信データをJSONとしてデコード

    def send(x):  # サーバーにデータを送信する関数
        return tube.send(x)  # Tubeのsendメソッドを呼び出してデータを送信

    def xor(a: bytes, b: bytes) -> bytes:  # 二つのバイト列のXORを計算する関数
        return bytes(x ^ y for x, y in zip(a, b))  # 各バイト同士のXORを計算して新しいバイト列を生成

    def split_16(data: bytes) -> [bytes]:  # バイト列を16バイトのブロックに分割する関数
        return [data[16 * n : 16 * (n + 1)] for n in range(math.ceil(len(data) / 16))]  # 16バイトごとに分割してリストに格納

    def decrypt_cfb(msg: bytes) -> [bytes]:  # CFBモードでメッセージを復号する関数
        # 復号に必要な形式にメッセージを整形
        msg += b"\x00" * max(
            256 - len(msg), (msg_block_len_in_hex + 32) // 2 - len(msg)
        )
        msg = binascii.hexlify(msg)  # メッセージを16進数のASCII文字列に変換

        # メッセージの長さに関するアサーション（条件チェック）
        assert len(msg) <= msg_block_len_in_hex + 32
        assert 512 < len(msg)
        assert len(msg) <= 1024

        send(msg)  # 変換したメッセージをサーバーに送信

        temp = recv()  # サーバーからの応答を受信
        assert temp["msg"] == "CFB Decryption"  # 応答の種類をチェック
        return split_16(binascii.unhexlify(temp["ret"]))  # 復号されたデータを16バイトのブロックに分割して返す

    def decrypt_cbc(msg: bytes) -> [bytes]:  # CBCモードでメッセージを復号する関数
        # 復号に必要な形式にメッセージを整形
        msg += b"\x00" * min(
            max(256 - len(msg), msg_block_len_in_hex + 32 - len(msg)) + 16,
            512 - len(msg),
        )
        msg = binascii.hexlify(msg)  # メッセージを16進数のASCII文字列に変換

        # メッセージの長さに関するアサーション（条件チェック）
        assert msg_block_len_in_hex + 32 < len(msg)
        assert 512 < len(msg)
        assert len(msg) <= 1024

        send(msg)  # 変換したメッセージをサーバーに送信

        temp = recv()  # サーバーからの応答を受信
        assert temp["msg"] == "CBC Decryption"  # 応答の種類をチェック
        return split_16(binascii.unhexlify(temp["ret"]))  # 復号されたデータを16バイトのブロックに分割して返す

    # 初期化ベクトルとサーバーから受信した初期データ（ノンスとターゲットの暗号文）を取得
    iv = binascii.unhexlify("5f885849eadbc8c7bce244f8548a443f")
    initial_data = recv()
    nonce = binascii.unhexlify(initial_data["nonce"])
    target_ciphertext = binascii.unhexlify(initial_data["ct"])

    ct_len_in_byte = len(target_ciphertext)  # ターゲットの暗号文の長さ（バイト単位）
    msg_block_len_in_hex = (16 * (math.ceil(ct_len_in_byte / 16))) * 2  # メッセージブロックの長さ（16進数単位）

    blocks = split_16(target_ciphertext)  # ターゲットの暗号文を16バイトのブロックに分割

    keys = []  # 各ブロックを復号するために使用するキーのリスト
    for i in range(len(blocks)):  # 各ブロックに対して
        keys.append(nonce + struct.pack(">I", i + 2))  # ノンスとブロック番号を組み合わせたキーを生成
        assert len(keys[-1]) == 16  # 生成したキーの長さをチェック

    cts = []  # 復号されたブロックを格納するリスト
    encrypted_key_candidates = []  # 復号されたキーの候補を格納するリスト
    for i in range(0, len(keys), 10):  # キーのリストを10個ずつ処理
        # CFBモードでキーを復号
        cts = decrypt_cfb(
            b"\x00" * 16 + b"".join(b"\x00" * 16 + key for key in keys[i : i + 10])
        )
        encrypted_key_candidates += cts[3::2]  # 復号されたキーの候補をリストに追加
    print(f"[+] {encrypted_key_candidates = }")
    # 暗号化されたキーをブルートフォースで解読するためのリストを生成
    key_bruteforce_list = [
        bytes([0] * 14 + [x, y]) for x, y in itertools.product(range(256), repeat=2)
    ]
    encrypted_keys = []  # 解読されたキーを格納するリスト
    for i in range(1, len(keys) - 3):  # キーのリストを順に処理
        key_cand = encrypted_key_candidates[i]  # 現在のキーの候補
        kp = keys[i]  # 現在のキー
        cur = 0  # 現在のブルートフォースの位置
        while cur < len(key_bruteforce_list):  # ブルートフォースリストを順に処理
            # 現在のキーの候補とブルートフォースリストの要素とのXORを計算
            kci_blocks = [xor(key_cand, b) for b in key_bruteforce_list[cur : cur + 25]]
            # CBCモードで復号
            cand = decrypt_cbc(b"".join(kci_blocks))
            # 復号されたデータとIVまたは他のブロックとのXORを計算
            cand_xored = [xor(x, y) for x, y in zip(cand, [iv] + kci_blocks)]
            # 正しいキーを見つけたかどうかをチェック
            res = [i for i, b in enumerate(cand_xored) if b == kp]
            if len(res) > 0:  # 正しいキーが見つかった場合
                encrypted_keys.append(kci_blocks[res[0]])  # 解読されたキーをリストに追加
                break  # ループを抜ける
            cur += 25  # 次のブルートフォースの位置へ
        print([xor(x, y) for x, y in zip(encrypted_keys, blocks[1:])])
    assert len(encrypted_keys) == 17  # 解読されたキーの数をチェック
    # 復号されたキーとブロックのXORからPINを抽出
    pin = b"".join(xor(x, y) for x, y in zip(encrypted_keys, blocks[1:]))[13:-3]

    tube.send(binascii.hexlify(pin))  # PINを16進数のASCII文字列に変換してサーバーに送信
    print(recv())  # サーバーからの応答を表示

    tube.close()  # 通信を終了

# スクリプトが直接実行された場合にmain関数を呼び出す
if __name__ == "__main__":
    main()
