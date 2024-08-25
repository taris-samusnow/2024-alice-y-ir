# 2024年　夢宮ありす夏の自由研究 
# Lチカ スピーカー(Ver. Prototype) 作ってみた
## 実行環境
|||
| ---- | ---- |
| 実機 | Raspberry Pi 2Model B v1.1 |
| OS   | Raspbian GNU/Linux 12 (bookworm) |
| 言語環境 | Python 3.11.2 |
| 音声入力デバイス| ASUSTek Computer, Inc. Xonar U3 sound card |

## 環境構築
### サウンドカードの設定
```bash 

$ cat /proc/asound/modules
  0 snd_bcm2835
  1 vc4
  2 snd_usb_audio

# 以下のようにファイルを生成
$ sudo tee /etc/modprobe.d/alsa-base.conf_ << EOF
options snd slots=snd_usb_audio,snd_bcm2835
options snd_usb_audio index=0
options snd_bcm2835 index=1
EOF

# 端末を再起動し、alsa-base.confが正常に読み込まれることを確認
$ sudo reboot
# snd_usb_audio が 0 番目のデバイスになっていることを確認
$ cat /proc/asound/modules
   0 snd_usb_audio
   1 snd_bcm2835
   2 vc4

# 音声再生、録音のゲイン調整
$ alsamixer

# 実機確認 録音⇒再生 が可能なことを確認
$ arecord -D plughw:0,0 -c 2 -f S16_LE -r 44100  | aplay
 ```

### Python 実行環境構築
```bash 
$ cd ~
$ python -m venv vpyenv
$ source ${PWD}/vpyenv/bin/activate
$ echo "source ${PWD}/vpyenv/bin/activate" >> .bashrc
$ pip install numpy
$ pip install sounddevice
$ pip install RPi.GPIO
$ pip install python-dotenv

# その他 aptで必要なライブラリをインストールする
```

### 自動起動設定
```bash 
$ git clone https://github.com/taris-samusnow/2024-alice-y-ir.git
$ cd 2024-alice-y-ir

$ vi ay_lspeaker.service
  # 以下の例を参考に書き換える
  # Python 仮想環境の python への絶対パスと実行するファイルへの絶対パスを指定する
  ExecStart=/home/taris/vpyenv/bin/python /home/taris/2024-alice-y-ir/ay_lspeaker.py
  # 実行するユーザ名、グループの指定する
  User=taris
  Group=taris

$ sudo cp ay_lspeaker.service /etc/systemd/system/
# serviceの起動と起動状況の確認する
$ sudo systemctl start ay_lspeaker.service
$ sudo systemctl status ay_lspeaker.service
  # Active: active (running) となっていれば OK
# service の自動起動を有効化する
$ sudo systemctl enable ay_lspeaker.service
````

## service の停止
```bash 
$ sudo systemctl stop ay_lspeaker.service
$ sudo systemctl status ay_lspeaker.service
  # Active: inactive (dead)となっていれば OK
````

## パラメーター編集
```bash
# 実機状況やGPIOの配線などに合わせて編集する
vi .env
```

## 参考サイト
