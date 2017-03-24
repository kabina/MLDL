"""
python으로 모션 detect하는 로직
"""

import cv2
import datetime, sys

class detectthing:

    originalImg = {}
    filename = ''
    cam = cv2.VideoCapture(0)
    winName = "Movement Indicator"
    cv2.namedWindow(winName)


    def __init__(self, cascadefile):
        self.data = []
        self.filename = cascadefile

    def diffImg(self, t0, t1, t2):
        d1 = cv2.absdiff(t2, t1)
        d2 = cv2.absdiff(t1, t0)
        return cv2.bitwise_and(d1, d2)

    def getImage(self):
        flag, img = self.cam.read()
        self.originalImg[0] = img
        if flag:
            t = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
            return t

    def getThreeSnapShot(self):
        t_dic = {}
        for i in range(0, 3):
            t_dic[i] = self.getImage()
            cv2.waitKey(500)
        return t_dic

    def facedetect(self, img):
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        cascade = cv2.CascadeClassifier(self.filename)
        faces = cascade.detectMultiScale(gray, 1.3, 5)

        for (x, y, w, h) in faces:
            cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
            roi_gray = gray[y:y + h, x:x + w]
            roi_color = img[y:y + h, x:x + w]

        if len(faces) == 0:
            return []
        else:
            for f in faces:
                print(f)
            return faces

    def motionTrack(self):
        t_dic = self.getThreeSnapShot()

        while True:
            dimg = self.diffImg(t_dic[0], t_dic[1], t_dic[2])
            paththumb = ""
            thumbimg = ""

            x = cv2.threshold(dimg, 0, 255, cv2.THRESH_OTSU)
            faces = self.facedetect(self.originalImg[0])
            font = cv2.FONT_HERSHEY_SIMPLEX
            cv2.putText(self.originalImg[0], "Press 'C', If you want capture image.", (10, 420), font, 0.5, (255, 255, 255), 1)

            for (x, y, w, h) in faces:
                print("Found facecs")
                cv2.rectangle(self.originalImg[0], (x, y), (x + w, y + h), (255, 0, 0), 2)

                cv2.putText(self.originalImg[0], datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), (10, 450), font, 0.5, (255, 255, 255), 1)
                paththumb = '/tmp/thumb%s' % (datetime.datetime.now().strftime('%Y%m%d%Hh%Mm%Ss%f') + '.jpg')
                thumbimg = self.originalImg[0][y:y+h, x:x+w]

                cv2.imshow(self.winName, self.originalImg[0])

            if cv2.countNonZero(dimg) > 170000:
                #pathm = '/tmp/%s'%(datetime.datetime.now().strftime('%Y%m%d_%Hh%Mm%Ss%f_motion') + '.jpg')
                #patho = '/tmp/%s' % (datetime.datetime.now().strftime('%Y%m%d_%Hh%Mm%Ss%f_origin') + '.jpg')
                #patho = '/tmp/MotionImage' + '.jpg'
                #print("There is motion!!")
                #cv2.imwrite(patho, dimg)

                #cv2.imwrite(patho, originalImg[0])

                return True, thumbimg;
            else:
                pass
                # print("There is No motion!!.. Tracking...")

            #print("comparing")
            # Read next image
            t_dic[0] = t_dic[1]
            t_dic[1] = t_dic[2]
            t_dic[2] = self.getImage()
            key = cv2.waitKey(500)
            print(key)
            if key == 99 or key==67:
                cv2.imwrite(paththumb, thumbimg )
            if key == 27:
                cv2.destroyWindow(self.winName)
                sys.exit()

def main():
    d = detectthing('haarcascade_frontalface_default.xml')
    #d = detectthing('haarcascade_eye.xml')
    while True:
        d.motionTrack()

if __name__ == '__main__':
    main()

