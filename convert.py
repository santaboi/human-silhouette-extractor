##################################################
## Deeplabv3 Silhouette Extractor
##################################################
## Takes video file as input, generates silhouette
## mask and saves it.
##################################################
## Author: Jordan Kee
## Date: 2020-07-16
##forked and modified by : santaboi(2021/12/19)
##################################################

from __future__ import print_function
from post_processing import *
import cv2
import torch
import torch.nn.functional as F
from torchvision import transforms
import time
import os
os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"
os.environ["CUDA_VISIBLE_DEVICES"] = "1"
#import pycuda.autoinit

def human_extractor(input_names , output_file):
    # Loads video file into CV2
    video = cv2.VideoCapture(input_names)
    
    # Get video file's dimensions
    frame_width = int(video.get(3))
    frame_height = int(video.get(4))
    
    # Creates output video file
    out = cv2.VideoWriter(output_file,cv2.VideoWriter_fourcc('M','J','P','G'), 30, (frame_width,frame_height))

    prev_frame_time = 0
    new_frame_time = 0

    while (video.isOpened):
        # Read each frame one by one
        success, img = video.read()
        
        # Run if there are still frames left
        if (success):
            
            # Apply background subtraction to extract foreground (silhouette)
            mask = makeSegMask(img)
            
            # Apply thresholding to convert mask to binary map
            ret,thresh = cv2.threshold(mask,127,255,cv2.THRESH_BINARY)
            
            # Write processed frame to output file
            out.write(thresh)
            
            new_frame_time = time.time()
            fps = 1/(new_frame_time-prev_frame_time)
            prev_frame_time = new_frame_time 
            fps = str(fps)
            print(fps)
            # cv2.rectangle(mask, (10, 2), (100,20), (255,255,255), -1)
            # cv2.putText(mask, fps, (15, 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5 , (0,0,0))
            
            # Show extracted silhouette only, by multiplying mask and input frame
            final = cv2.bitwise_and(thresh, img)
            
            # Show current frame
            cv2.imshow('Silhouette Mask', mask)
            cv2.imshow('Extracted Silhouette', final)
            
            # Allow early termination with Esc key
            key = cv2.waitKey(10)
            if key == 27:
                break
        # Break when there are no more frames  
        else:
            break

    # Release resources
    cv2.destroyAllWindows()
    video.release()
    out.release()
    

# Load pretrained model
model = torch.hub.load('pytorch/vision:v0.6.0', 'deeplabv3_resnet101', pretrained=True)
# Segment people only for the purpose of human silhouette extraction
people_class = 15

# Evaluate model
model.eval()
print ("Model has been loaded.")

blur = torch.FloatTensor([[[[1.0, 2.0, 1.0],[2.0, 4.0, 2.0],[1.0, 2.0, 1.0]]]]) / 16.0

# Use GPU if supported, for better performance
if torch.cuda.is_available():
    print("cuda is available")
    model.to('cuda')
    blur=blur.to('cuda')
	
# Apply preprocessing (normalization)
preprocess = transforms.Compose([
	transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])

# Function to create segmentation mask
def makeSegMask(img):
    # Scale input frame
	frame_data = torch.FloatTensor( img ) / 255.0

	input_tensor = preprocess(frame_data.permute(2, 0, 1))
    
    # Create mini-batch to be used by the model
	input_batch = input_tensor.unsqueeze(0)

    # Use GPU if supported, for better performance
	if torch.cuda.is_available():
		input_batch = input_batch.to('cuda')

	with torch.no_grad():
		output = model(input_batch)['out'][0]

	segmentation = output.argmax(0)

	bgOut = output[0:1][:][:]
	a = (1.0 - F.relu(torch.tanh(bgOut * 0.30 - 1.0))).pow(0.5) * 2.0

	people = segmentation.eq( torch.ones_like(segmentation).long().fill_(people_class) ).float()

	people.unsqueeze_(0).unsqueeze_(0)
	
	for i in range(3):
		people = F.conv2d(people, blur, stride=1, padding=1)

	# Activation function to combine masks - F.hardtanh(a * b)
	combined_mask = F.relu(F.hardtanh(a * (people.squeeze().pow(1.5)) ))
	combined_mask = combined_mask.expand(1, 3, -1, -1)

	res = (combined_mask * 255.0).cpu().squeeze().byte().permute(1, 2, 0).numpy()

	return res


##########################################################################################
input_folder = "../input"
output_folder = "../output"
video_name = ""
out_data_path = ""
##########################################################################################

if __name__ == '__main__':
    for input_names in os.listdir(input_folder):
        ######################human extraction###############################
        print(input_names , "'s human extraction start!!!!")
        output_names = "out_" + input_names
        input_names = os.path.join(input_folder , input_names)
        output_file = os.path.join(output_folder , output_names)
        #human_extractor(input_names= input_names , output_file= output_file)
        print(output_file)
        print(input_names , "'s human extraction success!!!!")
        ######################post processing###############################
        print(input_names , "'s post processing start!!!!")
        out_data_path = os.path.join("../output" , video_name.split('.')[0] + "_out")
        #post_proc(video_name , out_data_path)
        print(out_data_path)
        print(input_names , "'s post processing success!!!!")

    


    