#!/usr/bin/env python
'''
Pure python socket solution for realsense camera

The code will run on the Transmitter side (Joule)
will stream the video data from the camera
Pure Python Socket program, without using ROS platform
Purpose: To test the transmission rate and latency vs runing on ROS
'''
from realsense_device import visionsensor
import time
from socket import *
import numpy as np
import zlib
from threading import Thread
from PIL import Image
from io import BytesIO

SERVER_IP = "69.91.157.166"
SERVER_PORT = 1080
MAX_NUM_CONNECTIONS = 5


class ConnectionPool():

    def __init__(self):
        self.BUFSIZE = 10000
        self.hostAddr = "173.250.200.8"
        self.PORT = 3030

        self.device = visionsensor()
        self.initDevice()


    def initDevice(self):
        self.device.createColor()
        self.device.createDepth()
        self.device.sync()
        self.device.startColor()
        self.device.startDepth()
        print("Wait for the Camera to Start")
        time.sleep(1)


    def getData(self):
        rgb = self.device.getRgb()
        depth = self.device.getDepth2Int8()
        #tarray = np.dstack((rgb,depth))
        return rgb, depth

    def send(self,data):
        self.s = socket(AF_INET,SOCK_STREAM)
        self.s.connect((self.hostAddr, self.PORT))
        self.s.sendto(data,(self.hostAddr,self.PORT))
        #self.adata = len(data)
        #print("Pre:"+str(self.ndata)+" After: "+str(self.adata)+" rate"+str(round(self.adata*1.0/self.ndata*100)))
        self.s.close()

    def begin(self):
        print("Press Ctr+C to stop the camera")
        while True:

            try:
                #PIL same to JPEG and read the byte array
                rgb, depth = self.getData()
                img = Image.fromarray(rgb)
                #img1 = Image.fromarray(depth)
                fpath = BytesIO()
                img.save(fpath, quality = 75, format = "JPEG")
                #img.save("rgb.jpg",quality = 75)
                fpath.seek(0)
                self.send(zlib.compress(fpath.getvalue()))
                #dpath = BytesIO()
                #img1.save(dpath, quality = 75, format = "JPEG")
                #dpath.seek(0)
                data = depth.tostring()
                cdata = zlib.compress(data)
                self.send(cdata)
                #print("Compression Rate: ",len(cdata)*1.0 / len(data))
                #with open("depth.jpg") as f:
                #    depth = f.read()

                '''
                Intra-Frame Compression
                data = self.getData().tostring()
                self.ndata = len(data)
                data = blosc.compress(data)
                self.send(data)
                '''
            except Exception, e:
                print "[Error] " + str(e.message)
                if(e == KeyboardInterrupt):
                    print("Camera Stop")
                    self.device.rgb_stream.stop()
                    self.device.depth_stream.stop()
                    break
                if(e==timeout):
                    print("Connection Timeout. Will try in 2 Seconds")
                    time.sleep(2)




if __name__ == '__main__':
        c = ConnectionPool()
        c.begin()
