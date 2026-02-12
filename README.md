# Color Catcher Game – OpenCV Python

An interactive computer vision-based game built using Python and OpenCV, where players catch falling objects using a real-world colored object tracked through their webcam.

Move a colored object (like a red marker or ball) in front of your camera to control the game and catch falling shapes before you lose all your lives!

## Features
* Real-time webcam tracking using OpenCV  
* Color-based object detection (HSV masking)  
* Multiple falling object types:
  * Circle  
  * Star  
  * Heart  
* Particle explosion effects on catch  
* Dynamic level progression  
* Life system  
* Score tracking
* color preset switching (Red, Blue, Green, Yellow)  
* Calibration mode with detection preview


## How It Works  
1. Webcam captures real-time video feed.  
2. Frame is converted from BGR → HSV color space.  
3. A color mask is applied to detect a specific colored object.  
4. The largest detected contour is tracked.  
5. Falling objects are spawned randomly.  
6. Collision detection checks if the tracked object touches falling shapes.  
7. Score increases, particles are generated, and levels scale difficulty.

## Tech Stack
* Python 3.x  
* OpenCV (cv2)  
* NumPy  
* Random  
* Time  


