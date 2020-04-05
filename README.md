# Waldo
Weapons Detection and Localization

## Background
This project makes use of a Keras implementation of RetinaNet object detection as described in [Focal Loss for Dense Object Detection](https://arxiv.org/abs/1708.02002) by Tsung-Yi Lin, Priya Goyal, Ross Girshick, Kaiming He and Piotr Dollár. The repository for this implementation can be found [here](https://github.com/fizyr/keras-retinanet).

## RetinaNet

RetinaNet was introduced to fill in for the imbalances and inconsistencies of the single shot object detectors like YOLO and SSD while dealing with extreme foreground-background classes. It is designed to accommodate Focal Loss, a method to prevent negatives from clouding the detector. The loss function used in this approach is the loss of the output of the classification subnet.

RetinaNet is a single, unified network composed of a backbone network and two task-specific subnetworks. The backbone is responsible for computing a conv feature map over an entire input image and is an off-the-self convolution network. The first subnet performs classification on the backbones output. The second subnet performs convolution bounding box regression.

In other words:
* Backbone: Computes feature map over an input object.
* Classification Subnet: Predicts the probability of an object being present in a particular location.
* Box Regression Subnet: Outputs the object location with respect to anchor box if an object exists.

The backbone represents the feature pyramid network built on top of ResNet50 or ResNet101. However, other classifiers can be used.

References:
1. [How RetinaNet Fixes The Shortcomings Of SSD With Focal Loss](https://www.analyticsindiamag.com/what-is-retinanet-ssd-focal-loss/)
2. [The intuition behind RetinaNet](https://medium.com/@14prakash/the-intuition-behind-retinanet-eb636755607d) 

## Possible Use Case
Early warning system, or post-processing analysis, of CCTV footage (or images).

Note: This implementation does not provide real-time detection (as some post-processing steps are involved).

## Classes
The model was trained on two classes, gun and knife. Due to poor performance on the knife class, it has been disabled from detection  until a better dataset can be found. However, this can be enabled by updating the [detector](https://github.com/luisra/waldo/blob/master/app/detector.py) file.

Perfomance (AP):
* Gun: 0.85
* Knife: 0.30

Performance was measured on images (not videos). More details on average precision (AP) can be found [here](https://github.com/luisra/waldo/tree/master/model).

## File Formats
The following extensions are allowed:
* images: jpg, jpeg, png, tif, tiff
* videos: avi, flv, mp4, mov, wmv, mkv

Even if the input file can't be displayed, the output file should (as it will have been converted to jpeg/mp4).

## Installation
1. Clone app folder.
2. Copy [model](https://github.com/luisra/waldo/blob/master/model/model50.h5) into app folder.
3. Add GCP bucket and folder details.
4. Add GCP credentials.

More application details can be found [here](https://github.com/luisra/waldo/tree/master/app).

## Flask
To run app locally:
```
python run app.py
```

## Docker
To make docker image:
```
docker build -t wally .
```

## Deploy
To deploy container:
```
docker run -p 8050:5000 --runtime=nvidia --rm wally 
```

## Screenshots

Home:

<img src="https://github.com/luisra/waldo/blob/master/screenshots/ScreenOne.png" width="625">


Output:

<img src="https://github.com/luisra/waldo/blob/master/screenshots/ScreenTwo.png" width="625">
