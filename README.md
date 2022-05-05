# PointyDrone

## Installation
#### Download repo.  

#### Create start python environment (Windows Command Line):  
`python3 -m venv DroneEnv` 
 
#### Start python environment:  
`DroneEnv\Scripts\activate`

#### Install dependences:
Make sure your pip version is up to date. 
If you are unsure run `python -m pip install --upgrade pip`.  

`python -m pip install -r requirements.txt`  
Running the command `pip list` should list the following packages:
- gdown
- tensorflow (version 2.X)
- numpy
- mediapipe
- opencv

#### Tello Python API:
Someone fill this please (if is just a simple pip install feel free to add it to the requirements.txt file)

#### RealSense Python API:
Someone fill this please (if is just a simple pip install feel free to add it to the requirements.txt file)


## Drone Control  
### Connecting to drone:  
Someone fill this please  

### Running Code:
Navigate to the top level repository folder (<Repo Download Location\PointyDrone>)  
With all the dependences installed and the RealSense camera connected to your computer run the command:  
`python3 DroneControl\realTimeRealsense.py`  

A window showing the RealSense color camera feed should appear.
Present the start/stop hand in the closed position for around 2 seconds.
Once a start/stop hand is determined use your other hand to direct the drone's direction of movement.
The drone will move when presenting an open palm and stop with a closed hand.
Hit <Ctrl>-C to quit the program.

### Gesture Classifier:
The gesture classifier can be retrained using the same data. To retrain run:
`python3 DataCapture\ClassifierTrain.py`  
This should download the data from google drive for you and then train a classifier to the folder NewGestureModel.
If you wish to use it instead of the provided model move and rename <NewGestureModel> to <PointyDrone\DroneControl\GestureModel>.  

## Dataset
[Hand Color and Depth](https://drive.google.com/file/d/1N4l7Ax8bJIYAU9kMngCyPIFolyyoDq0G/view?usp=sharing)  
[Even Gesture Classifier Split](https://drive.google.com/file/d/1LO09E76gO0XLZo1u_siOlfkxZ-gcqmTj/view?usp=sharing)  

