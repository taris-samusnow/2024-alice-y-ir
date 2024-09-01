# 2024年　夢宮ありす夏の自由研究 
# Lチカ スピーカー(Ver. Prototype) 作ってみた
## 実機動作
### 裏返しQuestion
[裏返しQuestion 実機動作 - youtube](https://youtu.be/WOVJcwIXOF4)

### I'm Home
[I'm Home 実機動作 - youtube](https://youtu.be/4VQbO1dTzNg)

## 第 1 実行環境
|||
| ---- | ---- |
| 実機 | Raspberry Pi 2Model B v1.1 |
| OS   | Raspbian GNU/Linux 12 (bookworm) - RASPBERRY PI OS (LEGACY, 32-BIT) Lite|
| 言語環境 | Python 3.9.2 |
| 音声入力デバイス| ASUSTek Computer, Inc. Xonar U3 sound card |


## 環境構築
### Python 実行用環境構築
```bash
$ sudo apt-get update
$ sudo apt-get -y upgrade
$ sudo apt-get -y install python3-pip git python3-venv vim libopenblas-base portaudio19-dev
```

### サウンドカードの設定
```bash
$ cat /proc/asound/modules
  0 snd_bcm2835
  1 vc4
  2 snd_usb_audio

# 以下のようにファイルを生成
$ sudo tee /etc/modprobe.d/alsa-base.conf << EOF
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

# raspi-config でも USB Advanced Audio Device を改めて選択
$ sudo raspi-config
  1 System Options       Configure system settings ⇒ Enter
    S2 Audio             Select audio out through HDMI or 3.5mm jack ⇒ Enter
      0 USB Advanced Audio Device  ⇒ Enter
  ⇒ Esc で終了

# 音声再生、録音のゲイン調整
$ alsamixer

# 実機確認 録音⇒再生 が可能なことを確認
$ arecord -D plughw:0,0 -c 2 -f S16_LE -r 44100  | aplay
 ```

### Lチカ スピーカー プログラム実行用環境構築
```bash
$ cd ~
$ python -m venv vpyenv
$ source ${PWD}/vpyenv/bin/activate
$ echo "source ${PWD}/vpyenv/bin/activate" >> .bashrc
$ pip install numpy sounddevice RPi.GPIO python-dotenv
```

### 自動起動設定
```bash 
$ git clone https://github.com/taris-samusnow/2024-alice-y-ir.git
$ cd 2024-alice-y-ir
$ vim ay_lspeaker.service
  # 以下の例を参考に書き換える
  # 作業ディレクトリは実行ユーザのホームディレクトリを指定
  WorkingDirectory=/home/taris/
  # Python 仮想環境の python への絶対パスと実行するファイルへの絶対パスを指定する
  ExecStart=/home/taris/vpyenv/bin/python /home/taris/2024-alice-y-ir/ay_lspeaker.py
  # 実行するユーザ名、グループの指定する
  User=taris
  Group=taris

$ sudo cp ay_lspeaker.service /etc/systemd/system/
# serviceの起動と起動状況を確認する
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
$ vim .env
```
-------------------------------------------------------------------------
## 第 2 実行環境
|||
| ---- | ---- |
| 実機 | LattePanda V1 DFR0444|
| OS   | Winows 10 Home |
| 言語環境 | Python 3.7.6(Anaconda 2020.02 for 32-bit Windows) |
| 音声入力デバイス| ASUSTek Computer, Inc. Xonar U3 sound card |

### Windows用 インストールパッケージ
- Git for Windows(2.46.0.windows.1)
- Anaconda 2020.02 for 64-bit Windows with Python 3.7
- オプション設定 : [LattePanda 公式ドキュメント：Remote Desktop](https://docs.lattepanda.com/content/1st_edition/tools/#remote-desktop)

### Lチカ スピーカー プログラム実行用環境構築
- Python ライブラリ
  ```ps
  PS > pip install sounddevice python-dotenv pyFirmata
  ```

- LattePanda V1 の Arduino デバイスセットアップ  
  [LattePanda 公式ドキュメント：Step 2: Set Up the Arduino](https://docs.lattepanda.com/content/1st_edition/vs_programming/#step-2-set-up-the-arduino)

- オプション設定 : SSH Server インストール
  [MicroSoft 公式ドキュメント : Windows 用 OpenSSH の概要](https://learn.microsoft.com/ja-jp/windows-server/administration/openssh/openssh_install_firstuse?tabs=powershell&pivots=windows-server-2019)

- デフォルト起動ターミナル を PowerShell に変更
  ```ps
  PS > Get-Command powershell | Format-Table -AutoSize -Wrap
  
  CommandType Name           Version         Source
  ----------- ----           -------         ------
  Application powershell.exe 10.0.19041.3996 C:\WINDOWS\System32\WindowsPowerShell\v1.0\powershell.exe
  
  # OpenSSH のレジストリーエントリーに DefaultShell=PowerShell を設定
  # PowerShell の PATH は上で確認した PATH を指定する
  PS > New-ItemProperty -Path "HKLM:\SOFTWARE\OpenSSH" -Name DefaultShell -Value "C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe" -PropertyType String -Force
  ```

### 自動起動設定
```ps
PS > git clone https://github.com/taris-samusnow/2024-alice-y-ir.git
PS > cd 2024-alice-y-ir

# 各コマンド結果を用いてタスクスケジューラに必要な情報を入手（以下は例）
PS > Convert-Path ay_lspeaker_lattepandav1.py
  C:\Users\Rei\2024-alice-y-ir\ay_lspeaker_lattepandav1.py
PS > $(Get-Command python).Source
  C:\Users\Rei\anaconda3\python.exe
PS > whoami
  desktop-65f2vce\Rei
# タスクスケジューラを作成
PS > schtasks /create /sc ONSTART /tn "ay_lspeaker" /tr "'C:\Users\Rei\anaconda3\python.exe' 'C:\Users\Rei\2024-alice-y-ir\ay_lspeaker_lattepandav1.py'" /RU desktop-65f2vce\Rei
  成功: スケジュール タスク "ay_lspeaker" は正しく作成されました。

# タスクが作成されたことを確認
PS > schtasks /Query /TN "ay_lspeaker"     
  フォルダー\
  タスク名                                 次回の実行時刻         状態
  ======================================== ====================== ===============
  ay_lspeaker                              N/A                    準備完了 

# デバッグ操作：タスクの開始
PS > schtasks /run /TN "ay_lspeaker"
# デバッグ操作：タスクの停止
PS > schtasks /end /TN "ay_lspeaker"
```
- 一部、GUIにて設定

# サウンド設定で入力/出力デバイスを指定する
デバイス ⇒ 再生／録音　タブにてそれぞれ 既定のデバイスを設定する


## パラメーター編集
`.env`をテキストエディタで編集

## 台座用 LED発光パターンについて
|.env 変数|値|--|
| ---- | ---- | ---- |
|FUCN2 |0|音声同期|
|FUCN2 |1|点灯|

## 参考サイト
[音声パワーと基本周波数をリアルタイムでモニタリングするスクリプトをPythonで書いた話 - 備忘録](https://tam5917.hatenablog.com/entry/2023/12/16/154930)
- [関連プログラム](https://gist.github.com/tam17aki/7a766b263ebc08752539ecdff9514298)
