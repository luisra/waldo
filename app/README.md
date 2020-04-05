# Application

Web app using Flask and Google Cloud for demonstration purposes.

## Requirements
- Inference model
- Google Cloud

## Input Parameters
- Buffer: Maximum number of frames allowed between two bounding boxes for smoothing. (Use 0 for no smoothing.)
- Confidence: Minimum detection score allowed.

In the case of an image, a buffer of 0 indicates no additional suppression of overlapping bounding boxes.

## Output Metrics
In addtion to the previous two:

- Upload Time: Number of seconds it took to upload the file.
- Detect Time: Number of seconds it took to analyze the file for detections.

## Testing & Coverage
The following 4 tests are available:
* Route check
* HTML content
* Results (UI)
* Results (API)

To execute:
```
coverage run test.py
```
For coverage details:
```
coverage report
```

Testing coverage is at least 75% for [app.py](https://github.com/luisra/waldo/blob/master/app/app.py) and [detector.py](https://github.com/luisra/waldo/blob/master/app/detector.py).

## Monitoring
A log will be kept to help monitor and debug the application. It will track the following actions:
1. Request made
2. Input received
3. Detection in progress
4. Process completed

## API
If the app is running, a request can be made using the following:
```
def send_request(url, conf, buff, file):
   
    import requests
    import magic
    import json
    import os
       
    mime = magic.Magic(mime=True)
    payload =  {'conf':conf,'buff':buff}
   
    f = open(file, 'rb')
   
    files = {
     'json': ('json', json.dumps(payload), 'application/json'),
     'file': (os.path.basename(file), f, mime.from_file(file))
    }
   
    r = requests.post(url, files=files)
    f.close()
    print(str(r.content, 'utf-8'))

send_request( 'IP:8050/api', conf, buff, file)
```
Otherwise, the web UI will be available at: IP:8050/

## Screenshots
Home:

<img src="https://github.com/luisra/waldo/blob/master/screenshots/ScreenOne.png" width="625">


Output:

<img src="https://github.com/luisra/waldo/blob/master/screenshots/ScreenTwo.png" width="625">

