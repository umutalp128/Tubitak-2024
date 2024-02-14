import serial1
import os
import argparse
import cv2
import numpy as np
import sys
import time
from threading import Thread
import json
import importlib.util
import datetime

openConfig = open("config.json","r")
configRead = openConfig.read()



configParsed = json.loads(configRead) #ayar dosyasını oku


count  = int(configParsed["trigger"]) #tetik değerini al
count2 = 0
class VideoStream: # çok çekirdekli görüntü aktarımı :
    """Picamera"""
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
# uygulama ayar parametreleri
parser = argparse.ArgumentParser()
parser.add_argument('--modeldir', help='Folder the .tflite file is located in ',default='Sample_TFLite_model'
                    )
parser.add_argument('--graph', help='Name of the .tflite file, if different than detect.tflite',
                    default='detect.tflite')
parser.add_argument('--labels', help='Name of the labelmap file, if different than labelmap.txt',
                    default='labelmap.txt')
parser.add_argument('--threshold', help='Minimum confidence threshold for displaying detected objects',
                    default=0.5)
parser.add_argument('--resolution', help='Desired webcam resolution in WxH. If the webcam does not support the resolution entered, errors may occur.',
                    default='1280x720')

#algılanan parametreleri değişkenlere ata
args = parser.parse_args()

MODEL_NAME = args.modeldir
GRAPH_NAME = args.graph
LABELMAP_NAME = args.labels
min_conf_threshold = float(args.threshold)
resW, resH = args.resolution.split('x')
imW, imH = int(resW), int(resH)

# kurulu olan tensorflow lite modülünü/kütüphenesini tespit et ve import et 
pkg = importlib.util.find_spec('tflite_runtime')
if pkg:
    from tflite_runtime.interpreter import Interpreter
else:
    from tensorflow.lite.python.interpreter import Interpreter
 
#tensorflow lite interpreterine gerekli değerleri ver örneğin tensorflow lite modelinin dosya yolu

CWD_PATH = os.getcwd()

PATH_TO_CKPT = os.path.join(CWD_PATH,MODEL_NAME,GRAPH_NAME)

PATH_TO_LABELS = os.path.join(CWD_PATH,MODEL_NAME,LABELMAP_NAME)

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

floating_model = (input_details[0]['dtype'] == np.float32)

input_mean = 127.5
input_std = 127.5

outname = output_details[0]['name']

if ('StatefulPartitionedCall' in outname): 
    boxes_idx, classes_idx, scores_idx = 1, 3, 0
else:
    boxes_idx, classes_idx, scores_idx = 0, 1, 2
#fps tespiti
frame_rate_calc = 1
freq = cv2.getTickFrequency()

#görüntü aktarımını başlat
videostream = VideoStream(resolution=(imW,imH),framerate=30).start()
time.sleep(1)

#for frame1 in camera.capture_continuous(rawCapture, format="bgr",use_video_port=True):
#anlık olarak görüntüyü al ve işle :
while  True :
    #görüntünün alınması ve yeniden boyutlandırılması
    t1 = cv2.getTickCount()

    frame1 = videostream.read()

    frame = frame1.copy()
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    frame_resized = cv2.resize(frame_rgb, (width, height))
    input_data = np.expand_dims(frame_resized, axis=0)


    if floating_model:
        input_data = (np.float32(input_data) - input_mean) / input_std
    #tensorflow lite'ı hazırla
    interpreter.set_tensor(input_details[0]['index'],input_data)
    interpreter.invoke()

  
    boxes = interpreter.get_tensor(output_details[boxes_idx]['index'])[0] 
    classes = interpreter.get_tensor(output_details[classes_idx]['index'])[0] 
    scores = interpreter.get_tensor(output_details[scores_idx]['index'])[0] 
    #tespit edilen cismleri bul ve ekrana yazdır
    for i in range(len(scores)):
        if ((scores[i] > min_conf_threshold) and (scores[i] <= 1.0)):

            
            ymin = int(max(1,(boxes[i][0] * imH)))
            xmin = int(max(1,(boxes[i][1] * imW)))
            ymax = int(min(imH,(boxes[i][2] * imH)))
            xmax = int(min(imW,(boxes[i][3] * imW)))
            
            

           
            object_name = labels[int(classes[i])]
            #tespit edilen cisim telefon ise tespit edilen sayısını arttır
            print(object_name)
            if object_name == "cell phone":
                count2 = count2 + 1
            print(frame_rate_calc)
     #fps'i hesapla
    t2 = cv2.getTickCount()
    time1 = (t2-t1)/freq
    frame_rate_calc= 1/time1
    #telefon tespitleri ayarlanan değeri geçtiğinde değeri sıfırla ve arduinoya veriyi gönder
    if count == count2:
        print("telefon algilandi")
        serial1.lora()
        time.sleep(300)
        count2 = 0

videostream.stop()
