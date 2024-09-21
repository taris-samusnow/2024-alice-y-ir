# -*- coding: utf-8 -*-
import sys
import os
import time
import math
import queue
import struct

import numpy as np
import sounddevice as sd
from pyfirmata import Arduino, util
import signal
import threading
from dotenv import load_dotenv

#.env ファイルより値を読み込む 
load_dotenv()

DURATION        = float(os.getenv('DURATION'))
BA_DIFF         = float(os.getenv('BA_DIFF'))
SP              = float(os.getenv('SP'))

FUCN2           = int(os.getenv('FUCN2'))
PWM0            = int(os.getenv('PWM0'))
PWM1            = int(os.getenv('PWM1'))
GPIO_PWM0       = int(os.getenv('GPIO_PWM0'))
GPIO_PWM1       = int(os.getenv('GPIO_PWM1'))
GPIO_PWM3       = str(os.getenv('GPIO_PWM3'))
GPIO_PWM5       = str(os.getenv('GPIO_PWM5'))
GPIO_PWM6       = str(os.getenv('GPIO_PWM6'))
GPIO_PWM11      = str(os.getenv('GPIO_PWM11'))
PWM_HZ          = int(os.getenv('PWM_HZ'))
INPUT_CHANNELS  = int(os.getenv('INPUT_CHANNELS'))
OUTPUT_CHANNELS = int(os.getenv('OUTPUT_CHANNELS'))

gboard          = Arduino('COM3')

gpin3           = 0
gpin5           = 0
gpin6           = 0
gpin11          = 0
gred            = 0
ggreen          = 0
gblue           = 0
gthread1        = 0
gflag_color_palet_end = True

glight_list = [
    [1.0,1.0,1.0],
    [0.0,1.0,1.0],
    [0.0,0.9,1.0],
    [0.0,0.8,1.0],
    [0.0,0.7,1.0],
    [0.0,0.6,1.0],
    [0.0,0.5,1.0],
    [0.0,0.4,1.0],
    [0.0,0.3,1.0],
    [0.0,0.2,1.0],
    [0.0,0.1,1.0],
    [0.0,0.0,1.0],
    [0.1,0.0,1.0],
    [0.2,0.0,1.0],
    [0.3,0.0,1.0],
    [0.4,0.0,1.0],
    [0.5,0.0,1.0],
    [0.6,0.0,1.0],
    [0.7,0.0,1.0],
    [0.8,0.0,1.0],
    [0.9,0.0,1.0],
    [1.0,0.0,1.0],
    [1.0,0.0,0.9],
    [1.0,0.0,0.8],
    [1.0,0.0,0.7],
    [1.0,0.0,0.9],
    [1.0,0.0,0.6],
    [1.0,0.0,0.5],
    [1.0,0.0,0.4],
    [1.0,0.0,0.3],
    [1.0,0.0,0.2],
    [1.0,0.0,0.1],
    [1.0,0.0,0.0],
    [1.0,0.1,0.0],
    [1.0,0.2,0.0],
    [1.0,0.3,0.0],
    [1.0,0.4,0.0],
    [1.0,0.5,0.0],
    [1.0,0.6,0.0],
    [1.0,0.7,0.0],
    [1.0,0.8,0.0],
    [1.0,0.9,0.0],
    [1.0,1.0,0.0],
    [0.9,1.0,0.0],
    [0.8,1.0,0.0],
    [0.7,1.0,0.0],
    [0.6,1.0,0.0],
    [0.5,1.0,0.0],
    [0.4,1.0,0.0],
    [0.3,1.0,0.0],
    [0.2,1.0,0.0],
    [0.1,1.0,0.0],
    [0.0,1.0,0.0],
    [0.0,1.0,0.1],
    [0.0,1.0,0.2],
    [0.0,1.0,0.3],
    [0.0,1.0,0.4],
    [0.0,1.0,0.5],
    [0.0,1.0,0.6],
    [0.0,1.0,0.7],
    [0.0,1.0,0.8],
    [0.0,1.0,0.9],
    [0.0,1.0,1.0],
    [0.0,0.0,0.0],
  ]

class MicrophoneStream:
    """マイク音声入力のためのクラス."""

    def __init__(self, rate, chunk):
        """音声入力ストリームを初期化する.
        Args:
           rate (int): サンプリングレート (Hz)
           chunk (int): 音声データを受け取る単位（サンプル数）
        """
        # マイク入力のパラメータ
        self.rate = rate
        self.chunk = chunk

        # 入力された音声データを保持するデータキュー（バッファ）
        self.buff = queue.Queue()

        # マイク音声入力の初期化
        self.input_stream = None

    def open_stream(self):
        """入力ストリームを初期化する."""
        self.input_stream = sd.RawStream(
            samplerate=self.rate,
            blocksize=self.chunk,
            dtype="int16",
            channels=INPUT_CHANNELS,
            callback=self.callback,
        )

    def callback(self, indata, outdata, frames, time, status):
        """音声パワーに基づいて発話区間を判定.
        Args:
           indata: チャンクから取得した音声（バイナリ）データ
           frames: 未使用（取得に成功したチャンクのサイズ）
           time: 未使用
           status: 異常発生時のステータス
        """
        if status:
          print(status)
            
        # 入力された音声データをキューへ保存
        self.buff.put(bytes(indata))
        outdata[:] = indata

    with sd.Stream(channels=OUTPUT_CHANNELS, callback=callback):
        sd.sleep(int(DURATION * 1000))   
    
    def generator(self):
        """音声データを取得するための関数."""
        while True:  # キューに保存されているデータを全て取り出す
            # 先頭のデータを取得
            chunk = self.buff.get()
            if chunk is None:
                return
            data = [chunk]

            # まだキューにデータが残っていれば全て取得する
            while True:
                try:
                    chunk = self.buff.get(block=False)
                    if chunk is None:
                        return
                    data.append(chunk)
                except queue.Empty:
                    break

            # yieldにすることでキューのデータを随時取得できるようにする
            yield b"".join(data)

    def compute_power_fo(self, indata):
        """音声パワーと基本周波数を計算する関数.
        Args:
           indata (Bytes): チャンクから取得した音声データ.
        """
        audio = struct.unpack(f"{len(indata) / 2:.0f}h", indata)  # 2Byte単位でunpackする
        audio = np.array(audio).astype(np.float64)

        # 音声のパワー（音声データの二乗平均）を計算する
        rms = math.sqrt(np.square(audio).mean())
        power = 20 * math.log10(rms) if rms > 0.0 else -math.inf  # RMSからデシベルへ

        return power
def on_light(clr_list):
  global glight_list
  #print("\nlight_list",clr_list)

  light_list2 = [
    [0,1,1],     
    [0,1,1],
    [0,0.9555,1],
    [0,0.655,1],
    [1,0,1],
    [1,1,0],
    [0.1,0.95,0.3],
    [0,1,0.755],
    [0,0,0],
    [0,1,1],
    [0,0.9555,1],
    [0,0.655,1],
    [1,0,1],
    [1,1,0],
    [0.1,0.95,0.3],
    [0,1,0.755],
    [0,0,0]
  ]
  red,tgreen,blue = glight_list[clr_list]
  
  gpin5.write(red)
  green = tgreen * 1.9
  if green > 1:
    green = 1
  gpin6.write(green)
  gpin3.write(blue)

def color_palet():
  global gred
  global ggreen
  global gblue
  global gflag_color_palet_end

  #light_list = [
  #  [0,1,1],
  #  [0,0.9555,1],
  #  [0,0.655,1],
  #  [1,0,1],
  #  [1,1,0],
  #  [0.1,0.95,0.3],
  #  [0,1,0.755]
  #]

  #while gflag_color_palet_end:
  #  for i in range(len(light_list)):      
  #    gred,ggreen,gblue = light_list[i]
  #    time.sleep(0.2)
  #
  #return

  while gflag_color_palet_end:
      while gflag_color_palet_end:
        ggreen = ggreen - 0.0001
        if ggreen <= 0.6550:
          break
      
      while gflag_color_palet_end:
        gred = gred + 0.0001
        ggreen = ggreen - 0.0001
        if ggreen < 0:
          ggreen = 0
        if gred >= 1:
          break
  
      while gflag_color_palet_end:
        ggreen = ggreen + 0.0001
        gblue = gblue - 0.0001
        if gblue <= 0:
          gblue = 0
          break
  
      while gflag_color_palet_end:
        gred = gred - 0.0001
        ggreen = ggreen - 0.0001
        gblue = gblue + 0.0001
        if ggreen < 0.9500:
          ggreen = 0.9500
        if gblue > 0.3000:
          gblue = 0.3000
        if gred <= 0.1000:
          break
  
      while gflag_color_palet_end:
        gred = gred - 0.0001
        ggreen = ggreen + 0.0001
        gblue = gblue + 0.0001
        if gred < 0:
          gred = 0
        if ggreen > 1:
          ggreen = 1
        if gblue >= 0.7550:
          break
  
      while gflag_color_palet_end:
        ggreen = ggreen - 0.0001
        gblue = gblue - 0.0001
        if gblue <= 0:
          gblue = 0
        if ggreen <= 0:
          gblue = 0
          ggreen = 0
          break
    
      while gflag_color_palet_end:
        ggreen = ggreen + 0.0001
        gblue = gblue + 0.0001
        if gblue >= 1:
          gblue = 1
        if ggreen >= 1:
          gblue = 1
          ggreen = 1
          break

def main(chunk_size=8000):
    """音量と基本周波数をモニタリングするデモンストレーションを実行.
    Args:
       chunk_size (int): 音声データを受け取る単位（サンプル数）
    """
    global glight_list
    # 入力デバイス情報に基づき、サンプリング周波数の情報を取得
    input_device_info = sd.query_devices(kind="input")
    sample_rate = int(input_device_info["default_samplerate"])

    # マイク入力
    mic_stream = MicrophoneStream(sample_rate, chunk_size)
    
    level=round((100-SP)/(len(glight_list)-1),2)
    print(level)
    # GPIO 初期化処理
    PWM_INIT()

    # 起動 を LED点灯で示す
    if FUCN2 == 1:
      PWM_STANDBY()
    else:
      gpin5.write(1)
      gpin11.write(1)
      time.sleep(1)
      PWM_STOP()
    PWM_START()

    try:
        #print("＜収録開始＞")
        mic_stream.open_stream()  # 入力ストリームを開く準備
        #thread1.start()
        with mic_stream.input_stream:  # 入力ストリームから音声取得
            audio_generator = mic_stream.generator()  # 音声データ（のカタマリ）
            for data in audio_generator:  # チャンクごとに情報を表示してモニタリング
                power = mic_stream.compute_power_fo(data)  # 音声パワーと基本周波数を取得
                print(
                   "\r" + f"音声パワー {power:5.4f}[dB] ",
                  end="",
                )
                
                # デジベルが100を越えた場合は100デジベルとして扱う
                if power > 100:
                    power = 100
                # SP以下のデジベルは無音区間として扱う
                if power <= SP:
                  on_light(0)
                elif power <= (SP + level * 1):
                  on_light(1)
                elif power <= (SP + level * 2):
                  on_light(2)
                elif power <= (SP + level * 3):
                  on_light(3)
                elif power <= (SP + level * 4):
                  on_light(4)
                elif power <= (SP + level * 5):
                  on_light(5)
                elif power <= (SP + level * 6):
                  on_light(6)
                elif power <= (SP + level * 7):
                  on_light(7)
                elif power <= (SP + level * 8):
                  on_light(8)
                elif power <= (SP + level * 9):
                  on_light(9)
                elif power <= (SP + level * 10):
                  on_light(10)
                elif power <= (SP + level * 11):
                  on_light(11)
                elif power <= (SP + level * 12):
                  on_light(12)
                elif power <= (SP + level * 13):
                  on_light(13)
                elif power <= (SP + level * 14):
                  on_light(14)
                elif power <= (SP + level * 15):
                  on_light(15)
                elif power <= (SP + level * 16):
                  on_light(16)
                elif power <= (SP + level * 17):
                  on_light(17)
                elif power <= (SP + level * 18):
                  on_light(18)
                elif power <= (SP + level * 19):
                  on_light(19)
                elif power <= (SP + level * 20):
                  on_light(20)
                elif power <= (SP + level * 21):
                  on_light(21)
                elif power <= (SP + level * 22):
                  on_light(22)
                elif power <= (SP + level * 23):
                  on_light(23)
                elif power <= (SP + level * 24):
                  on_light(24)
                elif power <= (SP + level * 25):
                  on_light(25)
                elif power <= (SP + level * 26):
                  on_light(26)
                elif power <= (SP + level * 27):
                  on_light(27)
                elif power <= (SP + level * 28):
                  on_light(28)
                elif power <= (SP + level * 29):
                  on_light(29)
                elif power <= (SP + level * 30):
                  on_light(30)
                elif power <= (SP + level * 31):
                  on_light(31)
                elif power <= (SP + level * 32):
                  on_light(32)
                elif power <= (SP + level * 33):
                  on_light(33)
                elif power <= (SP + level * 34):
                  on_light(34)
                elif power <= (SP + level * 35):
                  on_light(35)
                elif power <= (SP + level * 36):
                  on_light(36)
                elif power <= (SP + level * 37):
                  on_light(37)
                elif power <= (SP + level * 38):
                  on_light(38)
                elif power <= (SP + level * 39):
                  on_light(39)
                elif power <= (SP + level * 40):
                  on_light(40)
                elif power <= (SP + level * 41):
                  on_light(41)
                elif power <= (SP + level * 42):
                  on_light(32)
                elif power <= (SP + level * 43):
                  on_light(33)
                elif power <= (SP + level * 44):
                  on_light(34)
                elif power <= (SP + level * 45):
                  on_light(35)
                elif power <= (SP + level * 46):
                  on_light(36)
                elif power <= (SP + level * 47):
                  on_light(37)
                elif power <= (SP + level * 48):
                  on_light(38)
                elif power <= (SP + level * 49):
                  on_light(49)
                elif power <= (SP + level * 50):
                  on_light(50)
                elif power <= (SP + level * 51):
                  on_light(51)
                elif power <= (SP + level * 52):
                  on_light(52)
                elif power <= (SP + level * 53):
                  on_light(53)
                elif power <= (SP + level * 54):
                  on_light(54)
                elif power <= (SP + level * 55):
                  on_light(55)
                elif power <= (SP + level * 56):
                  on_light(56)
                elif power <= (SP + level * 57):
                  on_light(57)
                elif power <= (SP + level * 58):
                  on_light(58)
                elif power <= (SP + level * 59):
                  on_light(59)
                elif power <= (SP + level * 60):
                  on_light(60)
                elif power <= (SP + level * 61):
                  on_light(61)
                elif power <= (SP + level * 62):
                  on_light(62)
                elif power <= (SP + level * 63):
                  on_light(63)
                else:
                  on_light(63)
                continue
    except KeyboardInterrupt:  # Ctrl-C (MacだとCommand-C) で強制終了
        print("\nKeyboardInterrupt")
    except Exception as e:
        print("\nException")
    finally:
        gflag_color_palet_end = False
        PWM_OFF()
        print("\n＜収録終了＞")

def PWM_INIT():
    # print("PWM-INIT")
    global gpin3
    global gpin5
    global gpin6
    global gpin11

    gpin3           = gboard.get_pin(GPIO_PWM3)
    gpin5           = gboard.get_pin(GPIO_PWM5)
    gpin6           = gboard.get_pin(GPIO_PWM6)
    gpin11          = gboard.get_pin(GPIO_PWM11)
    
    #アノードコモンのため 1 で消灯
    gpin3.write(1)
    gpin5.write(1)
    gpin6.write(1)

    if FUCN2 == 1:
      gpin11.write(0)
    PWM_START()
    return

def PWM_START():
    # print("PWM-START")
    gpin3.write(1)
    gpin5.write(1)
    gpin6.write(1)
    if FUCN2 == 1:
      gpin11.write(1)
    else:
      gpin11.write(0)
    return

def PWM_STANDBY():
    #print("PWM-STANDBY")
    gpin3.write(1)
    gpin5.write(1)
    gpin6.write(1)
    gpin11.write(1)
    return

def PWM_STOP():
    #print("PWM-STOP")
    gpin3.write(1)
    gpin5.write(1)
    gpin6.write(1)
    gpin11.write(0)
    return

def PWM_OFF():
    print("PWM-OFF")
    gpin3.write(1)
    gpin5.write(1)
    gpin6.write(1)
    gpin11.write(0)
    gboard.exit()
    return

def handler(signum, frame):
  PWM_OFF()
  print("\nDetect handler")
  pass

if __name__ == "__main__":
    # SIGTERM が発生した時の handler の登録
    signal.signal(signal.SIGTERM, handler)
    main()