import cv2
import numpy as np
import glob

files = glob.glob('D:/new_data/img/*.png')

img_array = []
for i in range(len(files)):
  path = 'D:/new_data/img/img.'+str(i)+'.png'
  img = cv2.imread(path)
  height, width, layers = img.shape
  size = (width,height)
  img_array.append(img)
 
 
out = cv2.VideoWriter('CloudDropletVisualization.avi',cv2.VideoWriter_fourcc(*'DIVX'), 5, size)
 
for i in range(len(img_array)):
    out.write(img_array[i])
out.release()