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
    global gred
    global ggreen
    global gblue
    global gflag_color_palet_end

    # 入力デバイス情報に基づき、サンプリング周波数の情報を取得
    input_device_info = sd.query_devices(kind="input")
    sample_rate = int(input_device_info["default_samplerate"])

    # マイク入力
    mic_stream = MicrophoneStream(sample_rate, chunk_size)
    
    bf_specmax = 0 
    pwm_flag = True
    thread1 = threading.Thread(target=color_palet)
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
        thread1.start()
        with mic_stream.input_stream:  # 入力ストリームから音声取得
            audio_generator = mic_stream.generator()  # 音声データ（のカタマリ）
            for data in audio_generator:  # チャンクごとに情報を表示してモニタリング
                power = mic_stream.compute_power_fo(data)  # 音声パワーと基本周波数を取得
                # print(
                #    "\r" + f"音声パワー {power:5.4f}[dB] ",
                #   end="",
                # )
                
                # デジベルが100を越えた場合は100デジベルとして扱う
                if power > 100:
                    power = 100
                
                # SP以下のデジベルは無音区間として扱う
                if power <= SP:
                  if pwm_flag == True:
                    if FUCN2 == 1:
                      PWM_STANDBY()
                    else:
                      PWM_STOP()
                    pwm_flag = False
                else:
                  if pwm_flag == False:
                    PWM_START()
                    pwm_flag = True
                  if power >= bf_specmax:
                    # (95 - power) で PWMによる光量を補う
                    #if power != 100:
                    #  freq = round(power + (95 - power), -1)
                    #else:
                    #freq = round(power, -1)
                    freq = power
                  elif power < bf_specmax:
                    if (bf_specmax - power) > BA_DIFF:
                      freq = 0
                  freq=freq/100
                  # PWMによりライトの強弱を操作する。
                  #gpin3.write(1.0-freq)
                  #gpin5.write(1.0-freq)
                  #gpin6.write(1.0-freq)
                  if freq == 0:
                    gpin5.write(1)
                    gpin6.write(1)
                    gpin3.write(1)
                  else:
                    gpin5.write(gred)
                    green = ggreen * 1.5
                    if (green) > 1:
                      green = 1
                    gpin6.write(green)
                    gpin3.write(gblue)

                  if FUCN2 == 0:
                    gpin11.write(freq)
                  
                  bf_specmax = power
                continue
    except KeyboardInterrupt:  # Ctrl-C (MacだとCommand-C) で強制終了
        print("\nKeyboardInterrupt")
    except Exception as e:
        print("\nException")
    finally:
        gflag_color_palet_end = False
        PWM_OFF()
        thread1.join()
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
  gflag_color_palet_end = False
  PWM_OFF()
  print("\nDetect handler")
  pass

if __name__ == "__main__":
    # SIGTERM が発生した時の handler の登録
    signal.signal(signal.SIGTERM, handler)
    main()