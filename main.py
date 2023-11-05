import cv2
import numpy as np
from imutils.video import VideoStream
from yolodetect import YoloDetect   
from win_setup import *
import ctypes



# Danh sách các nguồn camera
camera_srcs = [camera_1, camera_2, camera_3, camera_4]

# Mở cửa sổ và luồng video cho mỗi nguồn camera
windows = []
videos = []
list_points = []
list_vwrt = []

for idx, src in enumerate(camera_srcs):
    window_name = "Camera " + str(idx+1)
    cv2.namedWindow(window_name)
    windows.append(window_name)
    video = VideoStream(src=src).start()
    videos.append(video)
    list_points.append([])
    vwrt = cv2.VideoWriter(f'detect_file/video_alarm{idx + 1}.avi', cv2.VideoWriter_fourcc('m', 'p', '4', 'v'), 20.0, (f_width,f_height))
    list_vwrt.append(vwrt)
    


#========================== SETUP ================================
# Chua cac diem nguoi dung chon de tao da giac

win_c1, win_c2, win_c3, win_c4 = windows

# new model Yolo - Khởi tạo model Yolo và khai báo lớp nhận diện
model = YoloDetect(detect_class= detect_class)

detect = False

# #Sự kiện click chuột trái để vẻ điểm 
# def handle_left_click(event, x, y, flags, points):

#     if event == cv2.EVENT_LBUTTONDOWN:
#         points.append([x, y])  
#         click.play()

#Sự kiện click chuột trái để vẻ điểm 
def handle_left_click(event, x, y, flags, param):
    points, window  = param
    if event == cv2.EVENT_LBUTTONDOWN:
        points.append([x, y]) 
        click.play()
        if len(points) == 4:
            if window == win_c1:
                print(f'Nhấn phím 1 để kết thúc vùng detect cho {window}')
                key1.play()
            if window == win_c2:
                print(f'Nhấn phím 2 để kết thúc vùng detect cho {window}')
                key2.play()
            if window == win_c3:
                print(f'Nhấn phím 3 để kết thúc vùng detect cho {window}')
                key3.play()
            if window == win_c4:
                print(f'Nhấn phím 4 để kết thúc vùng detect cho {window}')
                key4.play()
        if len(points) > 4:
            detect_key.play()

#Vẽ các đa giác trên khung hình camera
def draw_polygon (frame, points):
    
    for point in points:
        frame = cv2.circle(frame, (point[0], point[1]), 4, (255, 0, 255), -1) #BGR

    frame = cv2.polylines(frame, [np.int32(points)], False, (0, 0, 224), thickness=2)
    return frame

#========================== ================================

# Vòng lặp chính
start =  1
while True:
    
    # Đọc từng khung hình từ từng luồng video
    frames = []
    
    for idx, (video,window) in enumerate(zip(videos, windows)): 
        if window == 'Camera ' + str(idx+1):
            #Đọc và resize lại kích thước video
            frame = video.read()
            if frame is None:
                continue
            frame = cv2.resize(frame, (f_width, f_height))
            if start==1:
                
                #cv2.moveWindow(window, 370 + (idx % 2) * 470, 110 + (idx // 2) * 390)
                # di chuyển cửa sổ 1
                cv2.moveWindow(win_c1, 370, 110)
                # di chuyển cửa sổ 2
                cv2.moveWindow(win_c2, 840, 110)
                # di chuyển cửa sổ 3
                cv2.moveWindow(win_c3, 370, 500)
                # di chuyển cửa sổ 4
                cv2.moveWindow(win_c4, 840, 500)
                

                start =0
            

            # Ve ploygon
            frame = draw_polygon(frame, list_points[idx])
            # print(list_points)
            if detect:
                frame = model.detect(frame= frame, points= list_points[idx], win= window)
              
            # add frame vào list frames
            frames.append(frame)


        # for frame, vwrt in zip(frames, list_vwrt):
        #     if window == 'Camera ' + str(idx+1):
        #         cv2.setMouseCallback(window, handle_left_click, list_points[idx])
        #         if model.detect_Flag() == window:
        #             vwrt.write(frame)
        #         if idx == 0:
        #             imgBG[73:73 + f_height, 30:30 + f_width] = frame
        #         elif idx == 1:
        #             imgBG[73:73 + f_height, (30 + 440):(30 + 440) + f_width] = frame
        #         elif idx == 2:
        #             imgBG[(73 + 325):(73 + 325) + f_height, 30:30 + f_width] = frame
        #         elif idx == 3:
        #             imgBG[(73 + 325):(73 + 325) + f_height, (30 + 440):(30 + 440) + f_width] = frame

        #     if detect:
        #         cv2.imshow('Intrusion Warning', imgBG)

        #     else:
        #         cv2.imshow('Setting', howToUse) # setting app
        #         cv2.imshow(window, frame)

        for frame, vwrt in zip(frames, list_vwrt):
            if window == 'Camera ' + str(idx+1):
                cv2.setMouseCallback(window, handle_left_click, (list_points[idx], window))
                if model.detect_Flag() == window:
                    vwrt.write(frame)
                if idx == 0:
                    imgBG[8:8 + f_height, 5:5 + f_width] = frame
                elif idx == 1:
                    # imgBG[73:73 + f_height, (30 + 440):(30 + 440) + f_width] = frame
                    imgBG[8:8 + f_height, 470:470 + f_width] = frame

                elif idx == 2:
                    # imgBG[(73 + 325):(73 + 325) + f_height, 30:30 + f_width] = frame
                     imgBG[362 :362 + f_height, 5:5 + f_width] = frame

                elif idx == 3:
                    # imgBG[(73 + 325):(73 + 325) + f_height, (30 + 440):(30 + 440) + f_width] = frame
                    imgBG[362 :362 + f_height, 470:470 + f_width] = frame


            if detect:
                cv2.imshow('Intrusion Warning', imgBG)

            else:
                cv2.imshow('Setting', howToUse) # setting app
                cv2.imshow(window, frame)

    key = cv2.waitKey(1)
    if key == ord('q'):
        break
    elif key == ord('d'):
        detect = True 
        if cv2.getWindowProperty("Setting", cv2.WND_PROP_VISIBLE) != 0:
            #thay đôi kích thước cửa sổ win1
            cv2.resizeWindow(win_c1, 1, 1)
            #cài đặt vị trí cửa sổ
            cv2.moveWindow(win_c1, 1, 1)
            #thay đôi kích thước cửa sổ win2
            cv2.resizeWindow(win_c2, 1, 1)
            cv2.moveWindow(win_c2, 1, 1)
            #thay đôi kích thước cửa sổ win3
            cv2.resizeWindow(win_c3, 1, 1)
            cv2.moveWindow(win_c3, 1, 1)
            #thay đôi kích thước cửa sổ win4
            cv2.resizeWindow(win_c4, 1, 1)
            cv2.moveWindow(win_c4, 1, 1)
            cv2.destroyWindow('Setting')
            start_alarm.play()
    elif key == ord('r'):
        detect = False
        #check cửa sổ
        if cv2.getWindowProperty("Intrusion Warning", cv2.WND_PROP_VISIBLE) != 0:
            cv2.destroyWindow("Intrusion Warning")
            cv2.imshow('Setting', howToUse) # setting app
            #thay đôi kích thước tất cả cửa sổ về mặc định
            cv2.moveWindow(win_c1, 370, 110)
            cv2.moveWindow(win_c2, 840, 110)
            cv2.moveWindow(win_c3, 370, 500)
            cv2.moveWindow(win_c4, 840, 500)
            cv2.resizeWindow(win_c1, 460, 350)
            cv2.resizeWindow(win_c2, 460, 350)
            cv2.resizeWindow(win_c3, 460, 350)
            cv2.resizeWindow(win_c4, 460, 350)


            reset_zone.play()
        #reset vùng cảnh báo
        for idx, points in enumerate(list_points):
           list_points[idx]= []
    elif key == ord('s'):
        model.ON_Alarm(detect)
        ring_sound.play()

    else:
        for idx, points in enumerate(list_points):
            if key == ord(str(idx + 1)):
                if len(points) >= 3:
                    end_detect.play()
                    points.append(points[0])
                else:
                    pass

        

# Dừng luồng video và đóng các cửa sổ

for vwrt in list_vwrt:
    vwrt.release()
for video in videos:
    video.stop()
cv2.destroyAllWindows()
