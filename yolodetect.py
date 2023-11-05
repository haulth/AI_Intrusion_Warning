from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
import cv2
import numpy as np
from telegram_utils import send_telegram
import datetime
import threading
import asyncio
import time
from win_setup import *



def isInside(points, corner):
    if len(points) >= 3:
        polygon = Polygon(points)
        corner = Point(corner)
        # print(polygon.contains(corner))
        return polygon.contains(corner)
    else:
        return False

class YoloDetect():
    def __init__(self, detect_class= detect_class, frame_width=f_width, frame_height=f_height):
        # Parameters
        self.classnames_file = "model/classnames.txt"
        self.weights_file = "model/yolov4-tiny.weights"
        self.config_file = "model/yolov4-tiny.cfg"
        self.conf_threshold = 0.5
        self.nms_threshold = 0.4
        self.detect_class = detect_class
        self.frame_width = frame_width
        self.frame_height = frame_height
        self.scale = 1 / 255
        self.model = cv2.dnn.readNet(self.weights_file, self.config_file)
        self.classes = None
        self.output_layers = None
        self.read_class_file()
        self.get_output_layers()
        self.last_alert_alarm = None
        self.alert_telegram_each = 20  # seconds time delay gửi thông báo
        self.last_alert = None
        self.alert_alarm = 3.5 # seconds
        self.detectFlag = ''
        self.on_Alarm = True

    def read_class_file(self):
        with open(self.classnames_file, 'r') as f:
            self.classes = [line.strip() for line in f.readlines()]

    def get_output_layers(self):
        layer_names = self.model.getLayerNames()
        self.output_layers = [layer_names[i - 1] for i in self.model.getUnconnectedOutLayers()]

    
    #Vẽ detech đối tượng
    def draw_prediction(self, img, class_id, x, y, x_plus_w, y_plus_h, points, win):

        # Lấy nhãn của lớp dự đoán
        label = str(self.classes[class_id])
        color = (0, 255, 0)

        # Tính toán tọa độ các góc của hình chữ nhật
        top_left = (x, y)
        top_right = (x_plus_w, y)
        bottom_left = (x, y_plus_h)
        bottom_right = (x_plus_w, y_plus_h)
        centroid = ((x + x_plus_w) // 2, (y + y_plus_h) // 2)

        cv2.circle(img, centroid, 5, (color), -1)
        cv2.circle(img, top_left, 5, (color), -1)
        cv2.circle(img, top_right, 5, (color), -1)
        cv2.circle(img, bottom_left, 5, (color), -1)
        cv2.circle(img, bottom_right, 5, (color), -1)

        # distance = cv2.norm(np.array(((x, y), (x_plus_w, y))), np.array(((x, y_plus_h),(x_plus_w, y_plus_h))))
        # print(f"distance: {distance}")

        # Vẽ hình chữ nhật bao quanh đối tượng dự đoán
        cv2.rectangle(img, top_left, bottom_right, color, 1) 
        cv2.rectangle(img, (x +65 , y), (x - 5   , y -20 ) , (0, 255, 0), -1) # Lớp đệm
        
        # Hiển thị nhãn của lớp dự đoán trên hình ảnh
        cv2.putText(img, label, (x , y-5 ), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (7 , 7 ,3), 1)


        # Tạo mảng chứa các tọa độ các góc của hình chữ nhật
        corners = [top_left, top_right, bottom_left, bottom_right, centroid]

        # Duyệt qua các góc trong mảng
        for corner in corners:
        # Kiểm tra xem tọa độ góc có nằm trong tập hợp các điểm points không
            if isInside(points, corner):
                # Gọi hàm alert và trả về kết quả của hàm
                self.detectFlag  = win
                img = self.alert(img, win)
                if self.on_Alarm:
                    self.sound_warning(win)
                

        
    def detect_Flag(self):
        return self.detectFlag 

    def ON_Alarm(self, detect):
        self.on_Alarm = not self.on_Alarm
        if detect:
            if self.on_Alarm:
                imgBG[380:380 + ico_h , 1150:1150 + ico_w] =  ico_on_rs
            else:
                imgBG[380:380 + ico_h, 1150:1150 + ico_w] =  ico_off_rs



    def sound_warning(self,win):
        # Delay âm thanh cảnh báo
        if (self.last_alert_alarm is None) or((datetime.datetime.utcnow() - self.last_alert_alarm).total_seconds() > self.alert_alarm):
            self.last_alert_alarm = datetime.datetime.utcnow()

            if win == win_c1:
                alarm1.play()
            elif win == win_c2:
                alarm2.play()
            elif win == win_c3:
                alarm3.play()
            elif win == win_c4:
                alarm4.play()

    def alert(self, img, win):
        
        #Hiện Text Cảnh Báo
        cv2.putText(img, 'ALARM!!!', (5, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
        cv2.putText(img, str(datetime.datetime.utcnow()), (5, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 255), 1)
        
        # Delay Gửi tin nhắn sau 15 giây
        if (self.last_alert is None) or (
                (datetime.datetime.utcnow() - self.last_alert).total_seconds() > self.alert_telegram_each):
            self.last_alert = datetime.datetime.utcnow()
            if win == win_c1:
                cv2.imwrite("detect_file/alert1.png", cv2.resize(img, dsize=None, fx=0.8, fy=0.8))
                imgDetech = cv2.resize(cv2.imread(photo1), (320, 230))
            elif win == win_c2:
                cv2.imwrite("detect_file/alert2.png", cv2.resize(img, dsize=None, fx=0.8, fy=0.8))
                imgDetech = cv2.resize(cv2.imread(photo2), (320, 230))
            elif win == win_c3:
                cv2.imwrite("detect_file/alert3.png", cv2.resize(img, dsize=None, fx=0.8, fy=0.8))
                imgDetech = cv2.resize(cv2.imread(photo3), (320, 230))
            elif win == win_c4:
                cv2.imwrite("detect_file/alert4.png", cv2.resize(img, dsize=None, fx=0.8, fy=0.8))
                imgDetech = cv2.resize(cv2.imread(photo4), (320, 230))
            # thread = threading.Thread(target=send_telegram, args=(win,))
            # thread.start()
            asyncio.run(send_telegram(win))
            imgBG[431:431 + 230, 930:930 + 320] =  imgDetech
        
        return img

    def detect(self, frame, points, win):
        blob = cv2.dnn.blobFromImage(frame, self.scale, (416, 416), (0, 0, 0), True, crop=False)
        self.model.setInput(blob)
        outs = self.model.forward(self.output_layers)

        # Loc cac object trong khung hinh
        class_ids = []
        confidences = []
        boxes = []

        for out in outs:
            for detection in out:
                scores = detection[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]
                if (confidence >= self.conf_threshold) and (self.classes[class_id] == self.detect_class):
                    center_x = int(detection[0] * self.frame_width)
                    center_y = int(detection[1] * self.frame_height)
                    w = int(detection[2] * self.frame_width)
                    h = int(detection[3] * self.frame_height)
                    x = center_x - w / 2
                    y = center_y - h / 2
                    class_ids.append(class_id)
                    confidences.append(float(confidence))
                    boxes.append([x, y, w, h])

        indices = cv2.dnn.NMSBoxes(boxes, confidences, self.conf_threshold, self.nms_threshold)

        for i in indices:
            box = boxes[i]
            x = box[0]
            y = box[1]
            w = box[2]
            h = box[3]
            self.draw_prediction(frame, class_ids[i], round(x), round(y), round(x + w), round(y + h), points, win)
        
        return frame