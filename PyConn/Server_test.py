import threading
import sys, time
from socket import *
import pickle
import numpy as np
import cv2
import zlib
'''
Single Port Server Test Version
'''
class Server:
    def __init__(self):
        self.BUFSIZE = 8192
        self.PORT = 5000
        self.s = socket(AF_INET, SOCK_STREAM)


    #TODO: 1. Test the size of each frame, whether can be sent in one buffer,
    #TODO: 2.  if Can, send 4 bit frame size and then receive that amount,
    #tODO: if cannot,
    def serverBegin(self):
        self.s.bind(('', self.PORT))
        self.s.listen(5)
        print("listening...")
        lasttime =  int(round(time.time() * 1000))
        count = 0
        while True:
            if(int(round(time.time() * 1000)) - lasttime > 5000):
                lasttime = int(round(time.time() * 1000))
                print("Average FPS:"+str(count / 5.0))
                count = 0

            conn, (host, remoteport) = self.s.accept()
            arr1 = b""
            while True:
                data = conn.recv(self.BUFSIZE)
                if not data:
                    break
                arr1 += data
            arr1 = self.prepareData(arr1)
                #np.fromstring(zlib.decompress(arr1), dtype=np.uint8).reshape(480, 640, 3)

            ## Distance map print('Center pixel is {} mm away'.format(dmap[119, 159]))
            ## Display the stream
            cv2.waitKey(1) & 255
            cv2.imshow("Depth", arr1)
            count+=1
            conn.close()

    def serverBegin1(self):
        self.s.bind(('', self.PORT))
        self.s.listen(1)
        print("listening...")
        lasttime =  int(round(time.time() * 1000))
        count = 0
        while True:
            if(int(round(time.time() * 1000)) - lasttime > 5000):
                lasttime = int(round(time.time() * 1000))
                print("Average FPS:"+str(count / 5.0))
                count = 0

            conn, (host, remoteport) = self.s.accept()
            arr1 = b""
            while True:
                data = conn.recv(4)
                conn.send(data)
                arr1 = conn.recv(int(data))
                arr1 = self.prepareData(arr1)
                thread = threading.Thread(target=show,kwargs={'img':arr1})
                thread.start()
                #np.fromstring(zlib.decompress(arr1), dtype=np.uint8).reshape(480, 640, 3)

            ## Distance map print('Center pixel is {} mm away'.format(dmap[119, 159]))
            ## Display the stream
            count+=1
            conn.close()

    def show(self,img):
        try:
            cv2.destroyAllWindows()
        except:
            pass
        cv2.imshow("Depth",img)
        cv2.waitKey(1)&255




    def prepareData(self,data):
        data = np.fromstring(zlib.decompress(data), dtype=np.uint16).reshape(480, 640)
        d4d = np.uint8(data.astype(float) *255/ 2**12-1)
        d4d = 255 - cv2.cvtColor(d4d, cv2.COLOR_GRAY2RGB)
        #d4d = np.fromstring(zlib.decompress(data),dtype=np.uint8).reshape(480,640,3)
        return d4d

    def run(self):
        thread = threading.Thread(target=self.serverBegin)
        thread.start()

if __name__ == '__main__':
    server = Server()
    server.run()