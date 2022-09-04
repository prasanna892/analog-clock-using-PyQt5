from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PIL import Image, ImageFilter
from PIL.ImageQt import ImageQt
from datetime import datetime
import math
import json
import sys, os

# reading property.json for getting saved data and store it in data in form of dictionary
with open('./assets/property.json') as file:
    data = json.load(file)
    file.close()

# creating required variables
TOTAL_CLOCK_FACE = len(os.listdir("./assets/clock_face"))


# Creating AnalogClock class
class AnalogClock(QWidget):
    def __init__(self, parent = None):
        super(AnalogClock, self).__init__(parent)

        # Setting window to frameless and transparent
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # Setting getted data to window
        self.screen_resize = self.screen_org_size = data['screen_size']

        self.size_ = self.screen_org_size

        self.pos_x = data['position']["x_pos"]
        self.pos_y = data['position']["y_pos"]

        self.clock_img_count = 1

        self.clock_face_size = data['clock_face_size']
        self.clock_img_count = data['clock_img_count']
        self.clock_img_path = f'./assets/clock_face/clock{self.clock_img_count}.png'
        
        self.dot1 = data['dot_width1']
        self.dot2 = data['dot_width2']

        self.hour_hand_width = data['hour_hand_width']
        self.hour_hand_height = data['hour_hand_height']
        self.hour_hand_pivot_width = data['hour_hand_pivot_width']
        self.hour_hand_pivot_height = data['hour_hand_pivot_height']

        self.minutes_hand_width = data['minutes_hand_width']
        self.minutes_hand_height = data['minutes_hand_height']
        self.minutes_hand_pivot_width = data['minutes_hand_pivot_width']
        self.minutes_hand_pivot_height = data['minutes_hand_pivot_height']

        self.seconds_hand_width = data['seconds_hand_width']
        self.seconds_hand_height = data['seconds_hand_height']
        self.seconds_hand_pivot_width = data['seconds_hand_pivot_width']
        self.seconds_hand_pivot_height = data['seconds_hand_pivot_height']

        # getting time
        self.now = datetime.now()
        self.hour = int(self.now.strftime("%I"))
        self.minute = int(self.now.strftime("%M"))
        self.seconds = int(self.now.strftime("%S"))

        # flag variable
        self.ctrl_pressed = False

        # Setting window position and size
        self.setGeometry(self.pos_x, self.pos_y, self.size_, self.size_)

        # creating timer to update window at each 500ms
        self.timer1 = QTimer()
        self.timer1.timeout.connect(self.update_time)
        self.timer1.start(500)

        # checking window close operation and setting it to closeEvent()
        quit = QAction("Quit", self)
        quit.triggered.connect(self.closeEvent)

    # scaling and smoothing the image
    def scale_sharp_smoothing(self, path, size):
        pilImage = Image.open(path)
        resize_img = pilImage.resize(size)
        sharp_img = resize_img.filter(ImageFilter.SHARPEN)
        final_img = ImageQt(sharp_img)
        return QPixmap.fromImage(final_img)

    # for drawing clock face and hands
    def paintEvent(self, event):
        # loading the image
        clock_face_img = self.scale_sharp_smoothing(self.clock_img_path, (self.clock_face_size, self.clock_face_size))
        h_hand_img = self.scale_sharp_smoothing('./assets/hourpng.png', (self.hour_hand_width, self.hour_hand_height))
        m_hand_img = self.scale_sharp_smoothing('./assets/minutepng.png', (self.minutes_hand_width, self.minutes_hand_height))
        s_hand_img = self.scale_sharp_smoothing('./assets/secpng.png', (self.seconds_hand_width, self.seconds_hand_height))
        
        # setting painter to draw clock face
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setRenderHint(QPainter.HighQualityAntialiasing, True)
        painter.setRenderHint(QPainter.SmoothPixmapTransform, True)
        rect = QRect((self.size_ - clock_face_img.width())//2, (self.size_ - clock_face_img.height())//2, clock_face_img.width(), clock_face_img.height())
        painter.drawPixmap(rect, clock_face_img)

        # drawing clock hour hand
        painter.translate(self.size_//2, self.size_//2)
        painter.rotate(-(360-(int(0.5*self.minute)+(self.hour*30))))
        painter.translate(-self.size_//2, -self.size_//2)
        painter.drawPixmap(self.size_//2-self.hour_hand_pivot_width, self.size_//2-self.hour_hand_pivot_height, h_hand_img)
        painter.end()

        # drawing clock minute's hand
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setRenderHint(QPainter.HighQualityAntialiasing, True)
        painter.setRenderHint(QPainter.SmoothPixmapTransform, True)
        painter.translate(self.size_//2, self.size_//2)
        painter.rotate(-(360-self.minute*6))
        painter.translate(-self.size_//2, -self.size_//2)
        painter.drawPixmap(self.size_//2-self.minutes_hand_pivot_width, self.size_//2-self.minutes_hand_pivot_height, m_hand_img)
        painter.end()

        # drawing clock second's hand
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setRenderHint(QPainter.HighQualityAntialiasing, True)
        painter.setRenderHint(QPainter.SmoothPixmapTransform, True)
        painter.translate(self.size_//2, self.size_//2)
        painter.rotate(-(360-self.seconds*6))
        painter.translate(-self.size_//2, -self.size_//2)
        painter.drawPixmap(self.size_//2-self.seconds_hand_pivot_width, self.size_//2-self.seconds_hand_pivot_height+1, s_hand_img)
        painter.end()
        
        # drawing circle at ceenter of the circle
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setRenderHint(QPainter.HighQualityAntialiasing, True)
        painter.setRenderHint(QPainter.SmoothPixmapTransform, True)
        painter.setBrush(QBrush(Qt.red))
        painter.setPen(QPen(Qt.red, 8))
        painter.drawEllipse((self.size_-self.dot1)//2, (self.size_-self.dot1)//2, self.dot1, self.dot1)
        painter.setBrush(QBrush(Qt.black))
        painter.setPen(QPen(Qt.black, 8))
        painter.drawEllipse((self.size_-self.dot2)//2, (self.size_-self.dot2)//2, self.dot2, self.dot2)
        painter.end()

    # function for dinamically calculating clock hands width, height, change percentage and pivot point
    def clock_hands_size_and_pivot_calculation(self, width_or_height, pivot_width_or_height):
        # calculating width or height
        resized_hands_width_or_height = round(-((self.change_percentage/100)*width_or_height)+width_or_height)
        # calulating width or height change percentage
        hand_pivot_width_change_percent = round((resized_hands_width_or_height/width_or_height)*100)
        # calculating clock hands pivot width and height
        resized_hand_pivot_point = abs(round(-((hand_pivot_width_change_percent/100)*pivot_width_or_height)))
        return resized_hands_width_or_height, resized_hand_pivot_point

    # function for update time
    def update_time(self):
        # getting time
        self.now = datetime.now()
        self.hour = int(self.now.strftime("%I"))
        self.minute = int(self.now.strftime("%M"))
        self.seconds = int(self.now.strftime("%S"))
        self.update()

    # function for updating window on resize
    def update_window(self):
        resized_size = self.screen_resize # setting new width and height
        
        # max and min size
        if resized_size > 350: resized_size = 350
        elif resized_size < 250: resized_size = 250

        # calculation for width or height change percentage
        self.change_percentage = round(((self.screen_org_size-resized_size)/self.screen_org_size)*100)
        
        # calculation for new clock face size
        self.clock_face_size = round(-((self.change_percentage/100)*self.clock_face_size)+self.clock_face_size)
   
        # calculation for dot1 size
        self.dot1 = self.seconds_hand_width-2
        self.dot1 = (self.dot1//2)*2
        
        # calculation for dot2 size
        self.dot2 = math.floor(self.dot1/2)
        self.dot2 = (self.dot2//2)*2

        # seconds hand setting new width and height
        resized_seconds_hand_width, self.seconds_hand_pivot_width = self.clock_hands_size_and_pivot_calculation(self.seconds_hand_width, self.seconds_hand_pivot_width)
        resized_seconds_hand_height, self.seconds_hand_pivot_height = self.clock_hands_size_and_pivot_calculation(self.seconds_hand_height, self.seconds_hand_pivot_height)
        self.seconds_hand_width, self.seconds_hand_height = resized_seconds_hand_width, resized_seconds_hand_height # setting new width and height

        # minutes hand setting new width and height
        resized_minutes_hand_width, self.minutes_hand_pivot_width = self.clock_hands_size_and_pivot_calculation(self.minutes_hand_width, self.minutes_hand_pivot_width)
        resized_minutes_hand_height, self.minutes_hand_pivot_height = self.clock_hands_size_and_pivot_calculation(self.minutes_hand_height, self.minutes_hand_pivot_height)
        self.minutes_hand_width, self.minutes_hand_height = resized_minutes_hand_width, resized_minutes_hand_height # setting new width and height

        # hour hand setting new width and height
        resized_hour_hand_width, self.hour_hand_pivot_width = self.clock_hands_size_and_pivot_calculation(self.hour_hand_width, self.hour_hand_pivot_width)
        resized_hour_hand_height, self.hour_hand_pivot_height = self.clock_hands_size_and_pivot_calculation(self.hour_hand_height, self.hour_hand_pivot_height)
        self.hour_hand_width, self.hour_hand_height = resized_hour_hand_width, resized_hour_hand_height # setting new width and height
        
        # resetting original height, width and pivot point for all the image when window in max size
        if resized_size > 330:
            self.clock_face_size = 300
            self.dot1 = 16
            self.dot2 = 8
            self.hour_hand_width = 26
            self.hour_hand_height = 120
            self.hour_hand_pivot_width = 13
            self.hour_hand_pivot_height = 107
            self.minutes_hand_width = 30
            self.minutes_hand_height = 135
            self.minutes_hand_pivot_width = 15
            self.minutes_hand_pivot_height = 123
            self.seconds_hand_width = 18
            self.seconds_hand_height = 185
            self.seconds_hand_pivot_width = 9
            self.seconds_hand_pivot_height = 139

        # setting new size and position
        self.size_ = self.screen_org_size = resized_size
        self.setGeometry(self.pos_x, self.pos_y, self.size_, self.size_)

    # catch mouse wheel event occure
    def wheelEvent(self, event):
        # for one wheel rotation the width and height will chage by 25
        if event.angleDelta().y() > 0:
            self.screen_resize += 25
            if self.screen_resize > 350: self.screen_resize = 350 # max size
            else: self.pos_x = self.pos().x()-12; self.pos_y = self.pos().y()-12 # new position
        else:
            self.screen_resize -= 25
            if self.screen_resize < 250: self.screen_resize = 250 # min size
            else: self.pos_x = self.pos().x()+12; self.pos_y = self.pos().y()+12 # new position
        self.update_window() # updating window
    
    # catch double click event occure
    def mouseDoubleClickEvent(self, event):
        # changing clock face image
        if event.x() < self.size_//2:
            self.clock_img_count -= 1
        else:
            self.clock_img_count += 1

        if self.clock_img_count == TOTAL_CLOCK_FACE+1:
            self.clock_img_count = 1
        elif self.clock_img_count == 0:
            self.clock_img_count = TOTAL_CLOCK_FACE

        self.clock_img_path = f'./assets/clock_face/clock{self.clock_img_count}.png'

    # catch mouse hold event occure
    def mousePressEvent(self, event):
        self.oldPos = event.globalPos()

    # catch mouse move event occure
    def mouseMoveEvent(self, event):
        delta = QPoint (event.globalPos() - self.oldPos)
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.oldPos = event.globalPos()

    # detect key down event
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Control:
            self.ctrl_pressed = True

        if event.key() == Qt.Key_Escape:
            self.finish()

    # detect key up event
    def keyReleaseEvent(self, event):
        if event.key() == Qt.Key_Control:
            self.ctrl_pressed = False

    # catch window close event
    def closeEvent(self, event):
        self.finish()
    
    # to upadate all changed data to property,josn when close
    def finish(self):
        QCoreApplication.instance().quit()  # quit window
        # assiging new window spawn position and size
        data['position']["x_pos"] = self.pos().x()
        data['position']["y_pos"] = self.pos().y()
        data['screen_size'] = self.screen_org_size
        data['clock_face_size'] = self.clock_face_size
        data['clock_img_count'] = self.clock_img_count
        data['dot_width1'] = self.dot1 
        data['dot_width2'] = self.dot2 
        data['hour_hand_width'] = self.hour_hand_width 
        data['hour_hand_height'] = self.hour_hand_height 
        data['hour_hand_pivot_width'] = self.hour_hand_pivot_width         
        data['hour_hand_pivot_height'] = self.hour_hand_pivot_height       
        data['minutes_hand_width'] = self.minutes_hand_width 
        data['minutes_hand_height'] = self.minutes_hand_height 
        data['minutes_hand_pivot_width'] = self.minutes_hand_pivot_width   
        data['minutes_hand_pivot_height'] = self.minutes_hand_pivot_height 
        data['seconds_hand_width'] = self.seconds_hand_width 
        data['seconds_hand_height'] = self.seconds_hand_height
        data['seconds_hand_pivot_width'] = self.seconds_hand_pivot_width
        data['seconds_hand_pivot_height'] = self.seconds_hand_pivot_height
        # rewriting property.json
        with open('./assets/property.json', 'w') as file:
            json.dump(data, file, indent= 4)
            file.close()

# creating QApplication
def load():
    app = QApplication(sys.argv)  
    analog_clock = AnalogClock()
    app.aboutToQuit.connect(analog_clock.finish) # detect close event by system
    analog_clock.show() 
    app.exec()

# main code
if __name__ == '__main__':
    load()