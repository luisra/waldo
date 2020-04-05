# Prototype

Training and Testing will take place in a colab environment with a GPU.

## Train
Parameters used:
* Weights - Initial weights that will be used to fine-tune a custom dataset. This will be set to the recommended weights of a model trained on MS COCO with a backbone of Resnet50.

* Epochs - Number of forward and backward passes for all training samples. This will be set to 50.

* Steps - Total number of training samples. This will be set to 11,108.

The loss and classification loss decreased with each passing epoch. After 50, the classification loss was less than 0.1. This model was then evaluated on the test data to measure its performance.

## Test
Relevant parameters:
* IoU Threshold (default) - Value threshold to classify a prediction as a true positive. This will be 0.5.

* Score Threshold (default) - Score threshold to filter detections. This will be 0.05.

* Backbone (default) - Backbone of the model. This will be Resnet50.

* Model - Model to be used. This will be set to the model after the 50th epoch. ([Download](https://drive.google.com/open?id=1bmxVHPGPt08COTSHaIznXqoxBSbBdJWk))

## Results
Average Precision (AP):
* Gun: 0.86
* Knife: 0.30

Mean Average Precision (mAP): 0.58

Mean Average Precision (Weighted): 0.49

Note: Since the average precision for the knife class is only 0.3, the focus will be on the gun class moving forward.

## Metrics
Mean Average Precision is a popular metric for measuring the accuracy of object detectors. This takes other metrics into account such as precision, recall, and intersection over union.

#### Precision
Precision measures how accurate are the predictions. This translates to

![equation](http://latex.codecogs.com/gif.latex?P%3D%5Cfrac%7BTP%7D%7BTP+FP%7D)  

Where:
  * TP = True Positive
  * FP = False Positive

For example, the number of gun instances correctly identified divided by the predicted total number of gun instances.

#### Recall
Recall measures how good we are at finding the postives

![equation](http://latex.codecogs.com/gif.latex?R%3D%5Cfrac%7BTP%7D%7BTP+FN%7D)  

Where:
  * TP = True Positive
  * FN = False Negative
  
For example, the number of knife instances correctly identified divided by the actual total number of knife instances.

#### IoU
Intersection over Union measures the overlap between two boundaries.

![equation](http://latex.codecogs.com/gif.latex?IoU%3D%5Cfrac%7BAreaOfOverlap%7D%7BAreaOfUnion%7D)  

This value is used to classify a prediction as a true positive.

#### mAP
In this case, mAP refers to the mean of the average precision between the two classes, gun and knife.

So what's happening in the testing phase?

Predictions are made. These are considered correct for IoU values equal to or greater than 0.5. For each class, the average precision is determined by measuring the area under the precision-recall curve. Finally, the mean average precision is calculated.

Is this the best metric for evaluating videos?

Not necessarily. Since the processing of videos will be done frame by frame, it'd be more valuable (at first) to consider the following:
* Was a detection made at all?
* Was the detection accurate?
* How good is the model at tracking a detected object?

## Prototypes

Relevant modules.
```
from keras_retinanet.utils.image import preprocess_image
from keras_retinanet.utils.image import read_image_bgr
from keras_retinanet.utils.image import resize_image
from keras_retinanet import models
import matplotlib.pyplot as plt
from keras import backend as K
import tensorflow as tf
import numpy as np
import cv2`
```

Session settings.
```
config = tf.ConfigProto()
config.gpu_options.allow_growth = True
sess = tf.Session(config=config)
K.set_session(sess)
```

Known variables.
```
images = ['png', 'jpg', 'jpeg', 'tif', 'tiff']
videos = ['avi', 'flv', 'mp4', 'mov', 'wmv', 'mkv']
classes = {0: 'gun', 1: 'knife'}

model = models.load_model("/content/model50.h5", backbone_name="resnet50")
```

Image Prototype:

```
def imgDetect(file, conf): 
  
  ext = file.split('.')[-1]  
  
  if ext in images: #check extension

        # load image and make a copy
        image = read_image_bgr(file)
        image = image[:, :, ::-1].copy()
        output = image.copy()
        
        # prep for network
        image = preprocess_image(image)
        image, scale = resize_image(image)
        image = np.expand_dims(image, axis=0)
        
        # predict
        with sess.as_default():
            with sess.graph.as_default():
                boxes, scores, labels = model.predict_on_batch(image)
                
        # rescale 
        boxes /= scale
        
        for (box, score, label) in zip(boxes[0], scores[0], labels[0]):
            
            if score < float(conf): # check threshold 
                continue
        
            if classes[label] == 'gun': # draw
                
                box = box.astype('int')
                xmin, ymin, xmax, ymax = box
                    
                cv2.rectangle(output, (xmin, ymin), (xmax, ymax), 
                              (0, 255, 0), 2)
                
                cv2.putText(output, classes[label], (xmin, ymin - 10),
                		cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        # show
        plt.figure(figsize=(12,12))
        plt.imshow(output)
        plt.axis('off')
          
  else:
    return "Not a valid image."
```

Video Prototype:

```
def vidDetect(file, conf): 
  
    ext = file.split('.')[-1]
    
    if ext in videos: # check extension
  
        # video prep
        cap = cv2.VideoCapture(file)
        fps = cap.get(cv2.CAP_PROP_FPS)
        writer = None
        c = 0
       
        while True: # process video
            
            ret, frame = cap.read()
           
            if not ret:
                break
           
            c += 1
            bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
       
            # prep for network
            image = preprocess_image(bgr)
            image, scale = resize_image(image)
            image = np.expand_dims(image, axis=0)

            # predict
            with sess.as_default():
                with sess.graph.as_default():
                    boxes, scores, labels = model.predict_on_batch(image)

            # rescale 
            boxes /= scale

            for (box, score, label) in zip(boxes[0], scores[0], labels[0]):

                if score < float(conf): # check threshold 
                    continue

                if classes[label] == 'gun': # draw

                    box = box.astype('int')
                    xmin, ymin, xmax, ymax = box

                    cv2.rectangle(frame, (xmin, ymin), (xmax, ymax), 
                                  (0, 255, 0), 2)

                    cv2.putText(frame, classes[label], (xmin, ymin - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
            # write
            if writer is None:
                fourcc = cv2.VideoWriter_fourcc(*'MP4V')
                writer = cv2.VideoWriter('/content/output.mp4', fourcc, fps,
                                         (frame.shape[1], frame.shape[0]))
   
            if writer is not None:
                writer.write(frame)
        
        # cleanup
        cap.release()
       
        if writer is not None:
            writer.release()
            
    else:
      return "Not a valid video."
```

## Samples

Images:

```
imgDetect('/content/cop.jpg', 0.2)

```
<img src="https://github.com/luisra/waldo/blob/master/screenshots/ScreenThree.png">

```
imgDetect('/content/gunman.jpg', 0.7)

```
<img src="https://github.com/luisra/waldo/blob/master/screenshots/ScreenFour.png">

Video:

```
vidDetect('/content/guns.mp4',0.7)

```

[![Watch the video](https://img.youtube.com/vi/zxenHpdwPuY/hqdefault.jpg
)](https://www.youtube.com/embed/zxenHpdwPuY)

Note the jitter and lack of sound. These two issues will be addressed moving forward.
