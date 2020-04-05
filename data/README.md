# Preprocessing
The objective is to prepare the data for RetinaNet. Each instance has to be captured in one row. If an image has multiple objects, it will be broken down into multiple instances. An image with two guns, for example, will become two records (one for each). The desired format is the following: path, xmin, ymin, xmax, ymax, label.

In this context, xmin, ymin, xmax, and ymax define the bounding box around the object.

## Clasess
* Gun
* Knife

## Results
* Gun Instances
  * Train: 5,572
  * Test: 1,356
  
* Knife Instances
  * Train: 5,536
  * Test: 2,559

* Total Instances
  * Train: 11,108
  * Test: 3,915
