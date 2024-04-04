# LINE CTF 2024
Schedule: 2024/03/23 09:00 - 2024/03/24 09:00

<br>

## haki-tako-game
Server接続時に`AES-GCM`で暗号化されたPINコードが与えられる。<br>
これを復号化するChallenge。

Server接続時に下記のResponseが得られる。

```json
{
    "nonce": "961df4fb3ec4cceb9a33236d",
    "ct": "dab3cc288b7a889021dd02db2f2f3fb03ae417d68c6d49439831bd23df86a5f4d369a18292f173a4ae962ad7724fc0140d4d01e1767a56cac97b82604f0bace051ede1d92ad7c7752b9e49399018b5f90642da44bcd15a8c591c2e777ce2271a2b2649dd244d89ce990d1aa2ee51cc7c143503bf7069d5e5948b565263da17a7fe759ad886755edd358f8a232cc3e26fff04c3b7972f3a323c67b3f1e5fed4bc9ba3beab5dfc47665e1a277c697c12d4b811a55c8fd6c05c05667101633f4f7c1d6912978e0f01f650491f3099c0644c5cbc54bb3ddfb8268d9f2f50df3593aae0c886203fed5ae0caa7235fe4779860da5ea518645f6c050d2971aad6af086655672031c6ecf125115070fff0425099c07ecb344b478aded711f9a342454b46ec3972fd75d246eb75a5279a99bb2e231c9e27fe8d3dd1e605d5438e10003f5c1a77fa1358131e4af017ee734e931d2e",
    "tag": "759324cab31b10a69a69ebe7029013f0",
    "msg": "Send me ciphertext(hex) or pin-code.\nNew encrypted msg..."
}
```

`nonce`:<br>
[challenge_server.py](./haki-tako-game/challenge_server.py)に`LIMIT_PER_CONNECTION = 45000`が設定されており、1度の接続でRequest回数が制限されている。<br>
disconnectするまでは不変。

`ct`:<br>
キーにより暗号化された暗号文。

`tag`:<br>
`msg`:<br>
上記のプロパティは無視して良い。

<br>

`ct`を復号化するにあたり、正しいキーを特定したいが、キーは`nonce`と同様にdisconnectすると変更される。<br>
一方で不変である要素が存在する。これらが公開されている事実が脆弱性である。
- [crypto.py](./haki-tako-game/crypto.py)に、`AES_IV_HEX = "5f885849eadbc8c7bce244f8548a443f"`がハードコーディングされている。`IV`は不変。
- 暗号化アルゴリズムは`AES-GCM`で不変
- disconnectしない限りは`nonce`は不変

<br>

下記の順序でブルートフォースを行う。
1. Server接続時に下記のResponseを得る。
```
[Tube#recv] buf=b'{"nonce": "fecd721eadf1f0baaccbe44a", "ct": "b377dcf06558c5f74fd1a2ecf5970540d93bacc903aeb9ca2b5ad4f2ae636c7cc205863af2d89842da3b4ec66f8a14a8de7ba4087f2598b6cde6ae45411a715c7d6f461afdb0ce31cc4a6d8a7c25e2b7aa354d6a5d7af0fcec67aa5e147877ca331255042708a80235bfcdffa48b099f433f672708b95f053a15292827623760ed578dd00ea48aca43d787adc8ca1cca165f0b5e5f359263e4b6f7cdc92261d913e7f74abdf9d28ea9fa40f97f947757aa6a928629e189fe492486a8c04b35bcbb86fbc2030cb788f8ec16d567ff458fa68fdb16dbf31dda9a52ab525905105479958b6e39db8df447324582856c2ec47978d3ee4646cb27ad90d30981b1073a461951d5f3e7ca82f622ed2ad0c30218bc5c65354f09610714ddba136a2e162269679baebf9fa591eb8d070728ad804d6173625e4b3926a53d2c5bac142ff9aab0e712a1f7ba420c81ad7b591f18e383", "tag": "4c5f8897102d69d957189a4ada687171", "msg": "Send me ciphertext(hex) or pin-code.\\nNew encrypted msg..."}\n'
```

2. `"nonce": "fecd721eadf1f0baaccbe44a"`とシーケンス番号(2から始めて逐次増加させる)を組み合わせて、それぞれ16バイトの長さになるようにパディングされた0のバイト列と組み合わせる。<br>
これをServerへ送信し復号化させる。

```
[Tube#send] buf=b'0000000000000000000000000000000000000000000000000000000000000000fecd721eadf1f0baaccbe44a0000000200000000000000000000000000000000fecd721eadf1f0baaccbe44a0000000300000000000000000000000000000000fecd721eadf1f0baaccbe44a0000000400000000000000000000000000000000fecd721eadf1f0baaccbe44a0000000500000000000000000000000000000000fecd721eadf1f0baaccbe44a0000000600000000000000000000000000000000fecd721eadf1f0baaccbe44a0000000700000000000000000000000000000000fecd721eadf1f0baaccbe44a0000000800000000000000000000000000000000fecd721eadf1f0baaccbe44a0000000900000000000000000000000000000000fecd721eadf1f0baaccbe44a0000000a00000000000000000000000000000000fecd721eadf1f0baaccbe44a0000000b00000000000000000000000000000000'
```

3. 復号化されたResponseを受け取る。<br>
これを16Byte毎に分割し、暗号化されたキー候補(`encrypted_key_candidates`)の作成に使用する。<br>
以降この操作を複数回繰り返し、`encrypted_key_candidates`を作成する。

```
[Tube#recv] buf=b'{"ret": "af17bbe3b47193b51d79d8dac4bd00001c6084c26bab041d8a94e076445b0000e2adf6dcc65af4a7265f043c445b0000ea18a9824539b08327b4cc989cf40000e2adf6dcc65af4a7265f043c445b0000b054c2e960c1ddaf0b33a7dc80180000e2adf6dcc65af4a7265f043c445b00006c658c93b2366d3ecded7ce542260000e2adf6dcc65af4a7265f043c445b0000e907ea44a06b860b37b2e36c217e0000e2adf6dcc65af4a7265f043c445b00006b3acd5ed7f318a2a27e7a7b78c50000e2adf6dcc65af4a7265f043c445b0000163421a59984cda7f2bcc5c39c6a0000e2adf6dcc65af4a7265f043c445b0000708bbdcd80734b4e33818016bd8c0000e2adf6dcc65af4a7265f043c445b0000350cc0e494cb88be812ea205ecf80000e2adf6dcc65af4a7265f043c445b00007fee120a7f7b85dc1459bda1113e0000e2adf6dcc65af4a7265f043c445b0000fd0d50141624e50afcd63657b1db0000", "msg": "CFB Decryption"}\n'
```

4. 下記の出力の時点で`encrypted_key_candidates`の作成が完了する。

```
[+] encrypted_key_candidates = [b"\xea\x18\xa9\x82E9\xb0\x83'\xb4\xcc\x98\x9c\xf4\x00\x00", b'\xb0T\xc2\xe9`\xc1\xdd\xaf\x0b3\xa7\xdc\x80\x18\x00\x00', b'le\x8c\x93\xb26m>\xcd\xed|\xe5B&\x00\x00', b'\xe9\x07\xeaD\xa0k\x86\x0b7\xb2\xe3l!~\x00\x00', b'k:\xcd^\xd7\xf3\x18\xa2\xa2~z{x\xc5\x00\x00', b'\x164!\xa5\x99\x84\xcd\xa7\xf2\xbc\xc5\xc3\x9cj\x00\x00', b'p\x8b\xbd\xcd\x80sKN3\x81\x80\x16\xbd\x8c\x00\x00', b'5\x0c\xc0\xe4\x94\xcb\x88\xbe\x81.\xa2\x05\xec\xf8\x00\x00', b'\x7f\xee\x12\n\x7f{\x85\xdc\x14Y\xbd\xa1\x11>\x00\x00', b'\xfd\rP\x14\x16$\xe5\n\xfc\xd66W\xb1\xdb\x00\x00', b'\xc9\x19\xdf\xbe&\x89)A\x15\xf2\xa68\x1d\xf4\x00\x00', b'\x85\x02\xea\xb9\x19\n\x86Rt~\xa0\xec"G\x00\x00', b'h\xde\xb9h\xa3\x7fW~D\xd3\xfcs~\x8f\x00\x00', b'E"\x04\xfd~\x1c:\xecD\x0f\x03\'\x97\xde\x00\x00', b']\xa9!s\xa1\xf1\xb2MU\xea\xfc5\x02\xf4\x00\x00', b'\xc0\x1f;\xd7L\xb9IM\rl\xb9\xa6\xfa\x15\x00\x00', b'\xa2Yug\xd4\x12#OF\x93\xe1\x86z\xc4\x00\x00', b':\xd7@6\x12\xd0\xf5\xb1\xb5\xc2;D\x85\x00\x00\x00', b"\x06G\xf5\xc1\xcb\xbf\xd1\xf4\x87\xe1'fF\xd4\x00\x00", b'\x04S\x030/\x19_\xcaH\x0c(\xc4{Z\x00\x00', b'\x90\x8cw\xc4\x87\x9a+x\xa1\xde\x1e:m}\x00\x00', b'\x1c`\x84\xc2k\xab\x04\x1d\x8a\x94\xe0vD[\x00\x00', b'\x1c`\x84\xc2k\xab\x04\x1d\x8a\x94\xe0vD[\x00\x00', b'\x1c`\x84\xc2k\xab\x04\x1d\x8a\x94\xe0vD[\x00\x00', b'\x1c`\x84\xc2k\xab\x04\x1d\x8a\x94\xe0vD[\x00\x00', b'\x1c`\x84\xc2k\xab\x04\x1d\x8a\x94\xe0vD[\x00\x00', b'\x1c`\x84\xc2k\xab\x04\x1d\x8a\x94\xe0vD[\x00\x00', b'\x1c`\x84\xc2k\xab\x04\x1d\x8a\x94\xe0vD[\x00\x00', b'\x1c`\x84\xc2k\xab\x04\x1d\x8a\x94\xe0vD[\x00\x00', b'\x1c`\x84\xc2k\xab\x04\x1d\x8a\x94\xe0vD[\x00\x00']
```

> [!IMPORTANT]
> `encrypted_key_candidates`は暗号化されたキー候補であり正しいキーではない。<br>
> この後のプロセスにより正しいキーを特定する。

5. 14バイトの0と2バイトのすべての可能な値の組み合わせ(256 * 256 = 65536)でキーのブルートフォース候補リストを生成する。
6. キーのブルートフォース候補を使用して、`encrypted_key_candidates`のブロックをXOR演算し、復号されたデータブロックを生成する。
7. 復号されたデータブロックをCBCモードでさらに復号する。この際、初期化ベクトル（IV）の値を使用する。
8. 復号されたデータブロックから、元のキー（nonceとシーケンス番号の組み合わせ）と一致するものが存在するかどうかをチェックする。<br>
正しいキーが特定されるまでチェックを繰り返す。

```
[Tube#send] buf=b'b054c2e960c1ddaf0b33a7dc80180000b054c2e960c1ddaf0b33a7dc80180001b054c2e960c1ddaf0b33a7dc80180002b054c2e960c1ddaf0b33a7dc80180003b054c2e960c1ddaf0b33a7dc80180004b054c2e960c1ddaf0b33a7dc80180005b054c2e960c1ddaf0b33a7dc80180006b054c2e960c1ddaf0b33a7dc80180007b054c2e960c1ddaf0b33a7dc80180008b054c2e960c1ddaf0b33a7dc80180009b054c2e960c1ddaf0b33a7dc8018000ab054c2e960c1ddaf0b33a7dc8018000bb054c2e960c1ddaf0b33a7dc8018000cb054c2e960c1ddaf0b33a7dc8018000db054c2e960c1ddaf0b33a7dc8018000eb054c2e960c1ddaf0b33a7dc8018000fb054c2e960c1ddaf0b33a7dc80180010b054c2e960c1ddaf0b33a7dc80180011b054c2e960c1ddaf0b33a7dc80180012b054c2e960c1ddaf0b33a7dc80180013b054c2e960c1ddaf0b33a7dc80180014b054c2e960c1ddaf0b33a7dc80180015b054c2e960c1ddaf0b33a7dc80180016b054c2e960c1ddaf0b33a7dc80180017b054c2e960c1ddaf0b33a7dc8018001800000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000'
[Tube#recv] buf=b'{"ret": "3101ceb065dae5787ac147a22ca99570374627f9fac999dfcb1db3ca29182ccf8c9924c37565f259a4210d68579fd3f9ee843edc12bb6317b55ee8bd8c669daf82f7073e79fe52a0e35f5473265161d4638d5a3a9c5a5cc35a83b09ff088adfc6eb02f3a4fe0458fddcbf83e00c7b32aa71a507d847fb86cd6465867581af0c866267fffc28faa8cd92c5d7acfedf2b3caafaaadc23e08a6b7ae67ee8f759ec27cb46411f18410d4d20ecef10fea6d495ae96aae0d356978ddba42e0d16b753fff65ce222bd2ae1c61159478c300293935188dca8d0251bee21521d454ba52b713b9eef2ab5719926f7c13dea3fc35c2a869178d6727d917e8c8987df8785dd9b35b92c659508f5fa82f8b8b98f6991ced6c70662c84f85ac903d7f0e5b002b5127c2646a4dbd163f68077baa09e3300933302d63725605353e4ff9a26a7eee47c3996a35d539740b695b1a8f69abb7aae8819ead93e989945df9274be4904ebd1d5b517e8f0beae1e7b41586a05a9831d47822c7823afa83f27d6a0bab4c387ecc3b488dc5769ecb6567287bcd27730165c6cf51cb34575023541e03cdfc463a608ae1c7c7298da0906e63cbcc7c47ba608ae1c7c7298da0906e63cbcc7c47ba608ae1c7c7298da0906e63cbcc7c47ba608ae1c7c7298da0906e63cbcc7c47ba608ae1c7c7298da0906e63cbcc7c47ba608ae1c7c7298da0906e63cbcc7c47b", "msg": "CBC Decryption"}\n'
[Tube#send] buf=b'b054c2e960c1ddaf0b33a7dc80180019b054c2e960c1ddaf0b33a7dc8018001ab054c2e960c1ddaf0b33a7dc8018001bb054c2e960c1ddaf0b33a7dc8018001cb054c2e960c1ddaf0b33a7dc8018001db054c2e960c1ddaf0b33a7dc8018001eb054c2e960c1ddaf0b33a7dc8018001fb054c2e960c1ddaf0b33a7dc80180020b054c2e960c1ddaf0b33a7dc80180021b054c2e960c1ddaf0b33a7dc80180022b054c2e960c1ddaf0b33a7dc80180023b054c2e960c1ddaf0b33a7dc80180024b054c2e960c1ddaf0b33a7dc80180025b054c2e960c1ddaf0b33a7dc80180026b054c2e960c1ddaf0b33a7dc80180027b054c2e960c1ddaf0b33a7dc80180028b054c2e960c1ddaf0b33a7dc80180029b054c2e960c1ddaf0b33a7dc8018002ab054c2e960c1ddaf0b33a7dc8018002bb054c2e960c1ddaf0b33a7dc8018002cb054c2e960c1ddaf0b33a7dc8018002db054c2e960c1ddaf0b33a7dc8018002eb054c2e960c1ddaf0b33a7dc8018002fb054c2e960c1ddaf0b33a7dc80180030b054c2e960c1ddaf0b33a7dc8018003100000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000'
[Tube#recv] buf=b'{"ret": "1049d791d44c9b66a1cc5359f917da422697806a9c907390154584114faa7811c56eb465fc765a1ada38827c58c87dcf02cea31753bdd2575f1f198b5263e18ea8253942ff70b43e2af15d992d629a7eacbc7d4e3828f581056c5dc75adf42f5b2c4d5947797b24eda447ccac7fa40d34bb8856df6224ca04e25a6df9242c97e8c241029eb80acecbbdb42b622034d653e66735356c90df160cc7a9b983a7ad8e7fa79a341e8ca88bea0bd0b720f4abad4c340d7364c21ad7db7c7a5e944b9e323da06e305bea3457921f74b02923175cb9aed29885498adb46a164c76842519af354c64442b63d989817f60b204175168a7a9860a0e28494b2a7c545fbbff87db2aa65254e1ef7a81cf0eb5096549bdd503b0bab7dacd9f0a414f722154dd606e857c6977a7b326e87b26a3ce3761151eefb34673590da64eb5058c4c4677df86e6303b17236317392d4814ef03e15bf876337fb095ab01af0bbc96b0a41c83b2720f67b31b89f878a39414cc80bd7f8698e930640ec27c1ff363cd31c79bcc59586b09351fc57fbd2fde6505b91017165c6cf51cb34575023541e03cdfc44aa608ae1c7c7298da0906e63cbcc7c47ba608ae1c7c7298da0906e63cbcc7c47ba608ae1c7c7298da0906e63cbcc7c47ba608ae1c7c7298da0906e63cbcc7c47ba608ae1c7c7298da0906e63cbcc7c47ba608ae1c7c7298da0906e63cbcc7c47b", "msg": "CBC Decryption"}\n'
```

9. 下記の出力により、正しいキーが特定され、正しいキーを使用することでFlagが得られる。

```
[b'ion code is..{\x87\xd3', b'\xae`\n\xa9@\xee\xf5|\x17\xd62#-\xac\x85x', b'7|NL\xdfN\x1e\xbd\xfaTM)`d\xd1j', b'\x16U\x8bD*C\xd6\x93n4\x17\xf1\x04\xe0\x189', b'\xbc\x01l\xcf\xc4\xfe=[\x1e\xdbo\x9d\x88\x12\xf4\xb0', b'C\x99\xe8\xc9\xa7{\xe3L\x06>M\xe9\x19\x07\x955', b'v3\xa7\xc3\x9cr\xd7\xbb\xbb;\x8b-\xcb\x9a\xfe#', b'\x92\xb9\x9f\xdaq\xdf\x0f\x16W\x8e:\x0c\xd9\xf4`\xf7', b'\xebR[JI\x11wi\x18`\xc1\x9ax\xf9\xf6\xf9', b'\xda\xfe(\xf4\x9bp\xfb\xcf\xbc\x08\xe6\xc1b`z\xc6', b'/hx?0\xeb\x0f\xac=Z&D\xe2\x0c\xaf\x0b', b'\xd3XB\xaa\xa0s\xe0\xf6\xbc?\xea\xa6\x19p\xc9\xdf', b"\xe3\xad\xdf\xeb\xa5\xef'6\xde]\xa8u\xce\xdb\xd1r", b'$<\xaa\x1d\x98*?\xb9\x12\xd8\xb9\xb7\x87\x98M`', b'\xb9g\xe89\n\xff\x82j\xa0\xfcj\xaf{\xa4\xcd0', b"\xe4@$\xb2'\xf5\xe9\xcd\xb0\xb1\x0c\xac\xaa\x07\x86\xde", b'\x86\x8b%\x03]\xd9\x94\xb6\xa1\x1f\x81W\xef. D']
[Tube#send] buf=b'7b87d3ae600aa940eef57c17d632232dac8578377c4e4cdf4e1ebdfa544d296064d16a16558b442a43d6936e3417f104e01839bc016ccfc4fe3d5b1edb6f9d8812f4b04399e8c9a77be34c063e4de9190795357633a7c39c72d7bbbb3b8b2dcb9afe2392b99fda71df0f16578e3a0cd9f460f7eb525b4a491177691860c19a78f9f6f9dafe28f49b70fbcfbc08e6c162607ac62f68783f30eb0fac3d5a2644e20caf0bd35842aaa073e0f6bc3feaa61970c9dfe3addfeba5ef2736de5da875cedbd172243caa1d982a3fb912d8b9b787984d60b967e8390aff826aa0fc6aaf7ba4cd30e44024b227f5e9cdb0b10cacaa0786de868b25035dd994b6a11f8157ef'
[Tube#recv] buf=b'{"flag": "LINECTF{DUMMY_FLAG}"}\n'
```

> [!TIP]
> 入力したキーが正しくない場合、`'msg': 'Incorrect pin. Bye.\n'`の出力によりdisconnectしてしまうが、<br>
> 暗号の復号化は45000回の回数制限の中でconnectionが維持される。<br>
> connectionが維持されていれば`pin`は不変である為、復号化をブルートフォースする事で正しいキーを取得する事が可能であると理解している。

出典: [elliptic-shiho/solve.py](https://gist.github.com/elliptic-shiho/67778c6447c54d8be8ff066746461bbc)

<br>

## zipviewer-version-citizen
Webサイトが実行されている。<br>
zipファイルをuploadすると解凍されたファイルをDownloadする事ができる。<br>
flagは`/flag`に存在しており、symbolic linkをzip化する事でflagを取得可能であると推察した。<br>
しかし、symbolic linkのチェックが実装されており、解凍したファイルがsymbolic linkである場合、削除される。

<br>

回避方法は大量にuploadとDownloadを繰り返し、symbolic linkが削除される前にダウンロードする。

<br>

> [!IMPORTANT]
> 出典元のwriteupでは[solve.py](./zipviewer-version-citizen/solve.py)を実行するのみでflag取得に至ったようだが、<br>
> ローカル環境ではさらに負荷を掛ける必要があったため、[run.sh](./zipviewer-version-citizen/run.sh)を作成した。<br>
> また、zipファイルを作成するのが煩わしかったので、[solve.py](./zipviewer-version-citizen/solve.py)にzipファイル作成methodを追加した。

成功すると、カレントディレクトリに生成される`exec.log`にflagが出力される。

```
updating: symlink.txt (stored 0%)
Archive:  tmp.zip
    testing: symlink.txt              OK
No errors detected in compressed data of tmp.zip.
updating: symlink.txt (stored 0%)
Archive:  tmp.zip
    testing: symlink.txt              OK
No errors detected in compressed data of tmp.zip.
updating: symlink.txt (stored 0%)
Archive:  tmp.zip
    testing: symlink.txt              OK
No errors detected in compressed data of tmp.zip.
LINECTF{redacted}
```

出典: [4n86rakam1/index.md](https://github.com/4n86rakam1/writeup/blob/main/LINE_CTF_2024/Web/zipviewer-version-citizen/index.md)
