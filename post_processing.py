import cv2
import os
from pathlib import Path
#video_name = "IMG_3424_out.avi"
#out_data_path = "../output/IMG_3424_out"

video_name = "IMG_3422_out.avi"
def post_proc(video_name):
    out_data_path = "../output/" + video_name.split('.')[0]
    vidcap = cv2.VideoCapture(os.path.join("../output" , video_name))
    success,image = vidcap.read()
    
    h , w = image.shape[ : 2]
    resized_img = cv2.resize(image , (int(w/5) , int(h/5)) , interpolation=cv2.INTER_AREA)
    
    count = 0
    try:
        Path(out_data_path).mkdir(parents=True, exist_ok=True)
    finally:
        while success:
            
            cv2.imwrite((out_data_path + '/'+ video_name.split('.')[0] +"_frame%d.jpg" % count ), resized_img)     # save frame as JPG file     
            success,image = vidcap.read()
            
            h , w = image.shape[: 2]
            resized_img = cv2.resize(image , (int(w/5) , int(h/5)) , interpolation=cv2.INTER_AREA)
            
            print('Read a new frame: ', success)
            count += 1
            

        print(video_name, " dataset successfully done!")


#post_proc(video_name)
"""sample_img = cv2.imread("../output/IMG_3424_out/IMG_3424_out_frame0.jpg")
print(sample_img.shape)
h , w = sample_img.shape[0] , sample_img.shape[1]
print(h , w)
resized_img = cv2.resize(sample_img , (int(h*0.9) , int(w*0.9)) , interpolation=cv2.INTER_AREA)
cv2.imshow("resized" , resized_img)
cv2.waitKey(-1)"""


for file in os.listdir("../output/IMG_3424_out"):
    image = cv2.imread(os.path.join("../output/IMG_3424_out" , file))
    h , w = image.shape[: 2]
    resized_img = cv2.resize(image , (int(w/5) , int(h/5)) , interpolation=cv2.INTER_AREA)
    cv2.imwrite(os.path.join("../output/IMG_3424_out" , file) , resized_img)