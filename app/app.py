# -*- coding: utf-8 -*-

from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
from keras_retinanet import models
from google.cloud import storage
from keras import backend as K
from datetime import datetime
from detector import gkDetect
import tensorflow as tf
import timeit
import json
import os

app = Flask(__name__)
model = None
sess = None

def load():
    
    # prep
    mod = "model50.h5"
    config = tf.ConfigProto()
    config.gpu_options.allow_growth = True
    global sess
    sess = tf.Session(config=config)
    K.set_session(sess)
    global model
    model = models.load_model("{}".format(mod), backbone_name="resnet50")

@app.route('/')
def home():
    return render_template('home.html')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html'), 404

@app.errorhandler(500)
def page_not_found(e):
    return render_template('error.html'), 500

@app.route('/', methods=['GET', 'POST'])
def dynamic_page():
    
    # constants
    images = ['jpg', 'jpeg','png', 'tif', 'tiff']
    videos = ['avi', 'flv', 'mp4', 'mov', 'wmv', 'mkv']

    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] =
    bucket =
    folder =

    gcs = storage.Client()
    bucket = gcs.get_bucket('{}'.format(bucket))
    
    ### Log ###
    dt = datetime.today().strftime('%Y%m%d')
    lname = '{}/{}_log'.format(folder,dt) + '.txt'
    
    try:
        b = bucket.get_blob(lname)
        s = b.download_as_string().decode('utf-8')
    except:
        s = ''

    log = bucket.blob(lname)
    ###
    
    ### Upload ###
    upload_start = timeit.default_timer()
    
    file = request.files['file']
    filename = secure_filename(file.filename)
    
    ext = filename.split('.')[-1]
    ext = ext.lower()

    rm = '{} | Request made. ({})'.format(str(datetime.now()), file.filename)
    log.upload_from_string('{}\n{}'.format(s,rm), content_type='text/plain')

    blob = bucket.blob('{}/{}_input_'.format(folder,dt) + file.filename)
    blob.upload_from_string(file.read(), content_type=file.content_type)
    
    upload_stop = timeit.default_timer()
    upload_time = round((upload_stop - upload_start),1)
    
    ir = '{} | Input received.'.format(str(datetime.now()))
    b = bucket.get_blob(lname)
    s = b.download_as_string().decode('utf-8')
    
    log.upload_from_string('{}\n{}'.format(s,ir), content_type='text/plain')
    ###
    
    ### Detect ###    
    f = blob.public_url

    if (ext in images) or (ext in videos):
        
        detect_start = timeit.default_timer()
        conf = request.form['conf']
        buff = request.form['buff']

        ip = '{} | Detection in progress.'.format(str(datetime.now()))
        b = bucket.get_blob(lname)
        s = b.download_as_string().decode('utf-8')
        log.upload_from_string('{}\n{}'.format(s,ip), content_type='text/plain')

        if sess is None: load() # testing
        output = gkDetect(f, filename, conf, buff, model, sess)

        detect_stop = timeit.default_timer()
        detect_time = round((detect_stop - detect_start),1)

        pc = '{} | Process completed.'.format(str(datetime.now()))
        b = bucket.get_blob(lname)
        s = b.download_as_string().decode('utf-8')
        log.upload_from_string('{}\n{}'.format(s,pc), content_type='text/plain')
    
    else:
        detect_time = None
        conf = None 
        buff = None
        output = gkDetect(f, filename, conf, buff, model, sess)
    ###

    if request.method == 'POST':
                
        if ext in images: template = 'homeImg.html'            
        elif ext in videos: template = 'homeVid.html'
        else: template = 'error.html'

        conf = 'Confidence: ' + str(conf)
        buff = 'Buffer: ' + str(buff)
        upload_time = 'Upload Time: ' + str(upload_time)
        detect_time = 'Detect Time: ' + str(detect_time)
            
        return (render_template(template, upload = f, results = output, confidence = conf, buffer = buff, uploadTime = upload_time, detectTime = detect_time))

@app.route('/api', methods=['POST'])
def detect():
    
    # constants    
    images = ['jpg', 'jpeg','png', 'tif', 'tiff']
    videos = ['avi', 'flv', 'mp4', 'mov', 'wmv', 'mkv']
    
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] =
    bucket =
    folder =
    
    gcs = storage.Client()
    bucket = gcs.get_bucket('{}'.format(bucket))
    
    # data
    try:
        data = json.load(request.files['json'])
    except: # testing
        pass
    
    ### Log ###
    dt = datetime.today().strftime('%Y%m%d')
    lname = '{}/{}_log'.format(folder,dt) + '.txt'
    
    try:
        b = bucket.get_blob(lname)
        s = b.download_as_string().decode('utf-8')
    except:
        s = ''

    log = bucket.blob(lname)
    ###
    
    ### Upload ###
    upload_start = timeit.default_timer()
    
    file = request.files['file']
    filename = secure_filename(file.filename)
    
    ext = filename.split('.')[-1]
    ext = ext.lower()

    rm = '{} | Request made. ({})'.format(str(datetime.now()), file.filename)
    log.upload_from_string('{}\n{}'.format(s,rm), content_type='text/plain')
    
    blob = bucket.blob('{}/{}_input_'.format(folder,dt) + filename)
    blob.upload_from_string(file.read(), content_type=file.content_type)
    
    upload_stop = timeit.default_timer()
    upload_time = round((upload_stop - upload_start),1)
    
    ir = '{} | Input received.'.format(str(datetime.now()))
    b = bucket.get_blob(lname)
    s = b.download_as_string().decode('utf-8')
    
    log.upload_from_string('{}\n{}'.format(s,ir), content_type='text/plain')
    ###
    
    ### Detect ###
    f = blob.public_url
    
    if (ext in images) or (ext in videos):

        detect_start = timeit.default_timer()

        try:
            conf = data['conf']
            buff = data['buff']
        except: # testing
            conf = request.form['conf']
            buff = request.form['buff']

        ip = '{} | Detection in progress.'.format(str(datetime.now()))
        b = bucket.get_blob(lname)
        s = b.download_as_string().decode('utf-8')
        log.upload_from_string('{}\n{}'.format(s,ip), content_type='text/plain')

        if sess is None: load() # testing
        output = gkDetect(f, filename, conf, buff, model, sess)

        detect_stop = timeit.default_timer()
        detect_time = round((detect_stop - detect_start),1)

        pc = '{} | Process completed.'.format(str(datetime.now()))
        b = bucket.get_blob(lname)
        s = b.download_as_string().decode('utf-8')
        log.upload_from_string('{}\n{}'.format(s,pc), content_type='text/plain')
        
    else:
        detect_time = 'N/A'
        conf = 'N/A'
        buff = 'N/A'
        output = 'Not a valid file.'
    ###
    
    ### Results ###
    results = {'Confidence':conf, 'Buffer':buff, 
               'Upload Time': upload_time, 'Detect Time': detect_time, 'Output': output}
    
    return jsonify(results)
    ###
    
if __name__ == '__main__':
    print("Loading Keras model and starting Flask server...")
    load()
    app.run(host='0.0.0.0', threaded=True, debug=True)
