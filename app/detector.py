# -*- coding: utf-8 -*-

def gkDetect(f, filename, conf, buff, model, sess):
    
    from keras_retinanet.utils.image import preprocess_image
    from keras_retinanet.utils.image import resize_image
    from scenedetect.video_manager import VideoManager
    from scenedetect.scene_manager import SceneManager
    from scenedetect.stats_manager import StatsManager
    from scenedetect.detectors import ContentDetector
    from moviepy.editor import VideoFileClip    
    from tempfile import NamedTemporaryFile
    from google.cloud import storage
    from datetime import datetime
    from PIL import Image
    import urllib.request
    import numpy as np
    import requests
    import random
    import cv2
    import os

    # prep
    images = ['jpg', 'jpeg', 'png', 'tif', 'tiff']
    videos = ['avi', 'flv', 'mp4', 'mov', 'wmv', 'mkv']
    classes = {0: 'gun', 1: 'knife'}
    ext = filename.split('.')[-1]
    
    try:
        fname = filename.split('.')[-2]
    except:
        return "Please show file extension and try again."
    
    bucket =
    folder =
    
### video functions ###
    
    def ArithMean(A, B, N):
        
        """This function will smooth the transition between
        two bounding boxes, A and B, based on the number of 
        frames between them (N)."""
        
        output = []
        d = (B-A)/(N + 1)
        
        for i in range(1, N+1):
            output.append(int(A + i*d))
        
        return output


    def intersect(boxA, boxB):
        
        """This function will return the biggest of two bounding
        boxes if they intersect. Otherwise, it will return both."""
        
        xminA, yminA, xmaxA, ymaxA = boxA
        xminB, yminB, xmaxB, ymaxB = boxB
        
        # coordinates of intersection
        xA = max(xminA, xminB)
        xB = min(xmaxA, xmaxB)
        yA = max(yminA, yminB)
        yB = min(ymaxA, ymaxB)
        
        # areas
        interArea = max(0, xB - xA + 1) * max(0, yB - yA + 1)
        boxAArea = (xmaxA - xminA + 1) * (ymaxA - yminA + 1)
        boxBArea = (xmaxB - xminB + 1) * (ymaxB - yminB + 1)
        
        if interArea > 0:
            if boxAArea >= boxBArea: 
                return boxA
            else: 
                return boxB    
        else:
            return boxA, boxB
        
       
    def sceneDetect(vid):
    
        """This function will return the start and end frame
        of all scenes detected in a video."""

        scenes = []
    
        # construct scene manager
        video_manager = VideoManager([vid])
        stats_manager = StatsManager()
        scene_manager = SceneManager(stats_manager)
        
        # add content detector algorithm
        scene_manager.add_detector(ContentDetector())
        base_timecode = video_manager.get_base_timecode()
    
        try:
            # downscale, start, detect
            video_manager.set_downscale_factor() 
            video_manager.start()
            scene_manager.detect_scenes(frame_source=video_manager)  
            scene_list = scene_manager.get_scene_list(base_timecode)
    
            for i, scene in enumerate(scene_list):
                scenes.append([i+1, scene[0].get_frames(), scene[1].get_frames()])
                    
        finally:
            video_manager.release()
            
            # cleanup
            for k in range(len(scenes)):
                if k == 0:
                    scenes[k][1] = 0    
                if k == (len(scenes) - 1):
                    scenes[k][2] = nFrames
            
            return scenes


    def sceneGet(frame, scenes):
        
        """This function will retun the scene a frame belongs to."""
        
        for scene in scenes:
            start = scene[1]
            end = scene[2]
            
            if start <= frame < end:                          
                return scene[0]
     
        
    def clean(store):
        
        """This function will smooth the detections made by the model."""
        
        cleaned = []
        
        for i in range(len(store)):
            
            # get current frame and scene
            currFrame = store[i][3]
            currScene = sceneGet(currFrame, scenes)
        
            if i == 0:
                cleaned.append(store[i])
             
            else:
                
                # get previous frame and scene
                prevFrame = store[i-1][3]
                prevScene = sceneGet(prevFrame, scenes)
                diff = currFrame - prevFrame
                
                # get current and previous label
                currLab = store[i][2]
                prevLab = store[i-1][2]

                # get current and previous bounding box
                currBox = store[i][0] 
                prevBox = store[i-1][0]
                
                # move along if scenes/labels are different or gap is greater than buffer
                if (currScene != prevScene) or (currLab != prevLab) or (diff > int(buff)):
                    cleaned.append(store[i])
                    continue
                
                # check if bounding boxes intersect
                maxBox = intersect(prevBox, currBox)
                
                # if they belong to the same frame
                if currFrame == prevFrame:
                    if len(maxBox) == 4: # and intersect
                        if (maxBox == currBox).all(): # if current is bigger than previous
                            del cleaned[-1]# delete previous
                            cleaned.append(store[i]) # append current
                        else:
                            continue
                                               
                else: # if same scene and label and gap within buffer
                    
                    if len(maxBox) == 4: # if intersect
                        N = diff - 1 # get number of missing bounding boxes
                        collection = []
                        
                        # get the missing boxes between previous and current
                        for k in range(4):                
                            collection.append(ArithMean(prevBox[k], currBox[k], N))
                        
                        final = list(zip(*collection))
                        
                        # add frame details
                        for k in range(N):
                            prevFrame += 1
                            cleaned.append((np.array(final[k]),0,0,prevFrame))
                        
                        cleaned.append(store[i])
                        
                    else:
                        cleaned.append(store[i])

        return cleaned
###

### Image Functions ###

    def cleanImg(store):
        
        """This function will suppress overlapping bounding boxes with a smaller area."""
        
        # prep
        cleaned = store
        rem = []
        indx = 0
        d = {}
        
        # group detections by label
        for (box, score, label) in store:
            
            if label in d:
                d[label].append((box,score,label,indx))
                indx += 1 # track index
            
            else:
                d[label] = [(box,score,label,indx)]
                indx += 1 # track index
        
        # for every label
        for key, value in d.items():
            
            labStore = value # store detections
            
            for i in range(len(labStore)): # for every detection
                
                currBox = labStore[i][0]
                currIndx = labStore[i][3]
                
                for k in range(len(labStore)): # compare with the rest

                    iterBox = labStore[k][0]
                    iterIndx = labStore[k][3]
                    
                    if iterIndx in rem: # move along if determination made 
                        continue
                    
                    if (currBox != iterBox).all():
                        maxBox = intersect(iterBox, currBox) # check if bounding boxes intersect

                        if len(maxBox) == 4: # if they intersect
                            if (maxBox == currBox).all(): # and current is bigger
                                if iterIndx not in rem:
                                    rem.append(iterIndx) # store iter index
                            else:
                                if currIndx not in rem: # if iter is bigger
                                    rem.append(currIndx) # store current index
                                    break
                        else:
                            continue
        
        # sort
        rem = sorted(rem,reverse=True)
        
        # remove
        for indx in rem:
            del cleaned[indx]
                            
        return cleaned
###

### Images ###
        
    if ext.lower() in images: # check extension
        
        store = []
        
        # load image and make copy
        image = np.asarray(Image.open(requests.get(f, stream=True).raw).convert('RGB'))
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
        
        # first pass
        for (box, score, label) in zip(boxes[0], scores[0], labels[0]):
            
            if score < float(conf): # check treshold
                continue
        
            #if 1 == 1:
            if classes[label] == 'gun': # store detection
            
                box = box.astype("int")
                store.append((box,score,label))

        # smoothing
        if int(buff) == 0:
            cleaned = store
        else:
            cleaned = cleanImg(store)
        
        # draw
        for (box, score, label) in cleaned:
                
            box = box.astype("int")
            xmin, ymin, xmax, ymax = box
                    
            cv2.rectangle(output, (xmin, ymin), (xmax, ymax), 
                          (0, 255, 0), 2)
                
            cv2.putText(output, classes[label], (xmin, ymin - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        # upload
        gcs = storage.Client()
        bucket = gcs.get_bucket('{}'.format(bucket))
        dt = datetime.today().strftime('%Y%m%d')
        blob = bucket.blob('{}/{}_output_'.format(folder,dt) + fname + '.jpeg')
    
        temp = NamedTemporaryFile()
        tmpFile = temp.name + '.jpeg'
        cv2.imwrite(tmpFile,output)
        
        blob.upload_from_filename(tmpFile, content_type='image/jpeg')
        
        return blob.public_url
###
 
### Videos ###    
        
    elif ext.lower() in videos: # check extension
        
        f = f.replace('https', 'http')
        inputURL = f
        
        # first pass        
        cap = cv2.VideoCapture(f)
        nFrames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        c = 0
        store = []
       
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
                
                if score < float(conf): # check treshold
                    continue
                
                #if 1 == 1:
                if classes[label] == 'gun': # store detections
               
                    box = box.astype("int")
                    store.append((box,score,label,c))
        
        # cleanup         
        cap.release()

        # scene details
        tmp = NamedTemporaryFile(delete=False, suffix='.mp4')
        tmpScene = tmp.name
        
        urllib.request.urlretrieve(f,tmpScene)
        scenes = sceneDetect(tmpScene)
        
        tmp.close()
        os.unlink(tmp.name)
    
        # smoothing
        cleaned = clean(store)
        cleaner = clean(cleaned)
        
        while len(cleaned) != len(cleaner):
            cleaned = cleaner
            cleaner = clean(cleaner)
                
        # second pass
        cap = cv2.VideoCapture(f)
        fps = cap.get(cv2.CAP_PROP_FPS)
        writer = None
        c = 0
        
        temp = NamedTemporaryFile(delete=False, suffix = '.mp4')
        tmpFile = temp.name
           
        while True: # process video
                   
            ret, frame = cap.read()
           
            if not ret:
                break
           
            c += 1
            # match detections to frame
            recs = [item for item in cleaned if item[3] == c]
                        
            # if a detection has been made
            if len(recs) > 0:
                   
                for (box, score, label, f) in recs: # draw
                   
                    box = box.astype("int")
                    xmin, ymin, xmax, ymax = box

                           
                    cv2.rectangle(frame, (xmin, ymin), (xmax, ymax),
                                  (0, 255, 0), 2)
                        
                    cv2.putText(frame, classes[label], (xmin, ymin - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            
            # write
            if writer is None:
                fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                writer = cv2.VideoWriter(tmpFile, fourcc, fps,
                                             (frame.shape[1], frame.shape[0]))
         
            if writer is not None:
                writer.write(frame)
        
        # cleanup                        
        cap.release()
       
        if writer is not None:
            writer.release()
                
        # add audio
        video = VideoFileClip(inputURL)
        audio = video.audio
        output = VideoFileClip(tmpFile)
        final = output.set_audio(audio)
        
        temp.close()
        os.unlink(temp.name)
              
        tempAudio = NamedTemporaryFile(suffix='.mp4')
        tmpVid = tempAudio.name
        final.write_videofile(tmpVid)
        
        video.close()
        output.close()
        final.close()
        
        # upload                
        gcs = storage.Client()
        bucket = gcs.get_bucket('{}'.format(bucket))
        dt = datetime.today().strftime('%Y%m%d')
        blob = bucket.blob('{}/{}_output_'.format(folder,dt) + fname + '.mp4')
        blob.upload_from_filename(tmpVid, content_type='video/mp4')
        
        return blob.public_url
###

### Other ###    
        
    else:
        return "Not a valid file. Try --\n\n Images: jpg, jpeg, png, tif, tiff\n Videos: avi, flv, mp4, mov, wmv, mkv"
        
