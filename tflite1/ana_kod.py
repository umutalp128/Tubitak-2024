import serial1
import os
import cv2
import numpy as np
import time
from threading import Thread
import json
from tensorflow.lite.python.interpreter import Interpreter
MODEL_ISMI = 'Sample_TFLite_model' #coco_ssd_mobilenet_v1_1.0_quant_2018_06_29
openedConfig = open("config.json","r")#ayar dosyasını oku
configRead = openedConfig.read()
configParsed = json.loads(configRead) 

count  = int(configParsed["trigger"]) #tetik değerini al
count2 = 0

class VideoStream: # çok çekirdekli görüntü aktarımı :
    def __init__(self,resolution=(640,480),framerate=30):
      
        self.stream = cv2.VideoCapture(0)
        ret = self.stream.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
        ret = self.stream.set(3,resolution[0])
        ret = self.stream.set(4,resolution[1])           
   
        (self.grabbed, self.frame) = self.stream.read()

        self.stopped = False

    def start(self):
        Thread(target=self.update,args=()).start()
        return self

    def update(self):
        while True:
            if self.stopped:
                self.stream.release()
                return
            
            (self.grabbed, self.frame) = self.stream.read()

    def read(self):
        return self.frame

    def stop(self):
        self.stopped = True

yol = os.getcwd()
PATH_TO_CKPT = os.path.join(yol,MODEL_ISMI,'detect.tflite')
PATH_TO_LABELS = os.path.join(yol,MODEL_ISMI,'labelmap.txt')

with open(PATH_TO_LABELS, 'r') as f:
    labels = [line.strip() for line in f.readlines()]
if labels[0] == '???':
    del(labels[0])

interpreter = Interpreter(model_path=PATH_TO_CKPT)
interpreter.allocate_tensors()

input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()
height = input_details[0]['shape'][1]
width = input_details[0]['shape'][2]

classes_idx, scores_idx = 1, 2
#görüntü aktarımını başlat
videostream = VideoStream(resolution=(1280, 720),framerate=30).start()
time.sleep(1)
#anlık olarak görüntüyü al ve işle :
while  True :
    #görüntünün alınması ve yeniden boyutlandırılması
    frame1 = videostream.read()
    frame = frame1.copy()
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    frame_resized = cv2.resize(frame_rgb, (width, height))
    input_data = np.expand_dims(frame_resized, axis=0)

    #tensorflow lite'ı hazırla
    interpreter.set_tensor(input_details[0]['index'],input_data)
    interpreter.invoke()
  
    classes = interpreter.get_tensor(output_details[classes_idx]['index'])[0] 
    scores = interpreter.get_tensor(output_details[scores_idx]['index'])[0] 
    #tespit edilen cismleri bul ve ekrana yazdır
    for i in range(len(scores)):
        if ((scores[i] > 0.5) and (scores[i] <= 1.0)):       
            cisim_ismi = labels[int(classes[i])]
            #tespit edilen cisim telefon ise tespit edilen sayısını arttır
            print(cisim_ismi)
            if cisim_ismi == "cell phone":
                count2 = count2 + 1
    #telefon tespitleri ayarlanan değeri geçtiğinde değeri sıfırla ve arduinoya veriyi gönder
    if count == count2:
        print("telefon algilandi")
        #serial1.lora()
        time.sleep(30)
        count2 = 0

videostream.stop()
