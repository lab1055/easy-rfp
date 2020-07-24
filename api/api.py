import time
import sys

from flask import Flask, jsonify, request
from flask_socketio import SocketIO, send, emit
from flask_cors import CORS, cross_origin


import smtplib
from string import Template
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from email.utils import make_msgid

import os
import yaml
import argparse
import pdb
import time
from datetime import datetime
import pprint
import json
import base64

import cv2
import gphoto2 as gp

from utils import log_started_scheduler, log_started_realtime, save_and_log_results, notify_email, log_generic
from tasks.task_bank import inference


app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*")

CORS(app)

image_counter = 1

@app.route('/')
def initialize():
    print('Initializing...')
    socketio.run(app, debug=True, host='0.0.0.0')
    return jsonify(success=True)


@app.route('/getAllTasks')
def taskList():
    with open('tasks/alltasks.yml', 'r') as f:
        cfg = yaml.safe_load(f)
    return jsonify(cfg)


@app.route('/realtime', methods=['GET', 'POST'])
def realtime():
    if(request.method == 'POST'):
        arguments = request.data.decode("utf-8")
        arguments = json.loads(arguments)

    with open('configs/config.yaml', 'r') as f:
        cfg = yaml.safe_load(f)
    
    # email settings
    src_email = cfg['EMAIL']['SRC_EMAIL_ID']
    src_pass = cfg['EMAIL']['SRC_EMAIL_PASSWORD']
    smtp_host = cfg['EMAIL']['SMTP_SERVER']
    smtp_port = cfg['EMAIL']['SMTP_PORT']
    dest_emails = arguments['email']  
    dest_emails = dest_emails.split(',')

    # i/o settings
    logs_save_dir = cfg['IO']['LOGS_SAVE_DIR']

    # model & task settings
    resize_width = cfg['IMAGE']['RESIZE_WIDTH']
    resize_height = cfg['IMAGE']['RESIZE_HEIGHT']
    
    # get task type
    with open('tasks/alltasks.yml', 'r') as f:
        all_tasks = yaml.safe_load(f)
    
    for x in all_tasks:
        if x['name'] == arguments['task']:
            task_type = x['task_type']
            break

    # create a log dir for all io
    now = datetime.now()
    dt_string = now.strftime("%d%m%Y_%H%M%S")

    logs_save_dir = os.path.join(logs_save_dir, 'realtime')
    if not os.path.exists(logs_save_dir):
        os.mkdir(logs_save_dir)

    session_name = cfg['SESSION_NAME']
    if session_name == 'auto':
        session_dir = os.path.join(logs_save_dir, dt_string)
    else:
        session_dir = os.path.join(logs_save_dir, session_name)

    if not os.path.exists(session_dir):
        os.mkdir(session_dir)
    print("Session directory_created: ", session_dir)

    # create other useful directories
    img_save_dir = os.path.join(session_dir, 'images')
    results_save_dir = os.path.join(session_dir, 'results')

    if not os.path.exists(img_save_dir):
        os.mkdir(img_save_dir)

    if not os.path.exists(results_save_dir):
        os.mkdir(results_save_dir)

    # log that process started
    # print that process started
    log_filename = os.path.join(session_dir, 'log.txt')
    log_started_realtime(cfg, log_filename)

    # initialize the camera.
    camera = gp.Camera()
    camera.init()

    # start capturing
    file_path = camera.capture(gp.GP_CAPTURE_IMAGE)
    file_path_jpg = file_path.name.replace("cr2", "JPG")
    camera_file = camera.file_get(file_path.folder,file_path.name,gp.GP_FILE_TYPE_NORMAL)
    target = os.path.join(img_save_dir, file_path_jpg)
    gp.gp_file_save(camera_file, target)
    
    img_name = file_path_jpg
    img = cv2.imread(img_name)
    img = cv2.resize(img, (resize_width, resize_height),
                     interpolation=cv2.INTER_AREA)
    outputs = inference(img, arguments['task'])

    print("".join((img_save_dir, '/', img_name)))

    # save image and inference and log metadata to csv
    log_csv = save_and_log_results(
        img, outputs, img_name, img_save_dir, results_save_dir, log_filename, task_type, socketio)

    # send email
    notify_email(src_email, src_pass, smtp_host, smtp_port,
                 dest_emails, log_csv, log_filename)

    # send output image to UI
    with open("".join((results_save_dir, '/', img_name)), "rb") as imageFile:
        img2send = base64.b64encode(imageFile.read())
    return img2send


@app.route('/schedule', methods=['GET', 'POST'])
def schedule():
    if(request.method == 'POST'):
        arguments = request.data.decode("utf-8")
        arguments = json.loads(arguments)
    with open('configs/config.yaml', 'r') as f:
        cfg = yaml.safe_load(f)
    
    # email settings
    src_email = cfg['EMAIL']['SRC_EMAIL_ID']
    src_pass = cfg['EMAIL']['SRC_EMAIL_PASSWORD']
    smtp_host = cfg['EMAIL']['SMTP_SERVER']
    smtp_port = cfg['EMAIL']['SMTP_PORT']
    dest_emails = arguments['email']  
    dest_emails = dest_emails.split(',')
    
    logs_save_dir = cfg['IO']['LOGS_SAVE_DIR']

    # model & task settings
    resize_width = cfg['IMAGE']['RESIZE_WIDTH']
    resize_height = cfg['IMAGE']['RESIZE_HEIGHT']
    
    # get task type
    with open('tasks/alltasks.yml', 'r') as f:
        all_tasks = yaml.safe_load(f)
    
    for x in all_tasks:
        if x['name'] == arguments['task']:
            task_type = x['task_type']
            break

    # timing settings
    t_capture = float(arguments['captureInterval'])
    t_notif = float(arguments['notifInterval'])
    total_time = float(arguments['totalTime'])

    # create a log dir for all io
    now = datetime.now()
    dt_string = now.strftime("%d%m%Y_%H%M%S")

    logs_save_dir = os.path.join(logs_save_dir, 'scheduler')
    if not os.path.exists(logs_save_dir):
        os.mkdir(logs_save_dir)

    session_name = cfg['SESSION_NAME']
    if session_name == 'auto':
        session_dir = os.path.join(logs_save_dir, dt_string)
    else:
        session_dir = os.path.join(logs_save_dir, session_name)

    if not os.path.exists(session_dir):
        os.mkdir(session_dir)
    print("Session directory_created: ", session_dir)

    # create other useful directories
    img_save_dir = os.path.join(session_dir, 'images')
    results_save_dir = os.path.join(session_dir, 'results')

    if not os.path.exists(img_save_dir):
        os.mkdir(img_save_dir)

    if not os.path.exists(results_save_dir):
        os.mkdir(results_save_dir)

    # log that process started
    # print that process started
    log_filename = os.path.join(session_dir, 'log.txt')
    log_started_scheduler(cfg, log_filename)

    # initialize the camera.
    camera = gp.Camera()
    camera.init()

    # start the loop
    capture_start = time.time()
    notif_start = capture_start
    start_time = capture_start
    elapsed_time = 0
    
    image_counter = 1
    print(dest_emails)
    while elapsed_time <= total_time:
        # sleep one second
        time.sleep(1)
        iter_start_time = time.time()
        elapsed_time_c = time.time() - capture_start
        if elapsed_time_c > t_capture:
            file_path = camera.capture(gp.GP_CAPTURE_IMAGE)
            file_path_jpg = file_path.name.replace("cr2", "JPG")
            camera_file = camera.file_get(file_path.folder,file_path.name,gp.GP_FILE_TYPE_NORMAL)
            target = os.path.join(img_save_dir,file_path_jpg)
            gp.gp_file_save(camera_file, target)
            
            img_name = file_path_jpg
            img = cv2.imread(img_name)

            outputs = inference(img, arguments['task'])

            # save image and inference and log metadata to csv
            log_csv = save_and_log_results(
                img, outputs, img_name, img_save_dir, results_save_dir, log_filename, task_type, socketio)

            capture_start = iter_start_time
            elapsed_time_c = 0
        elapsed_time_n = iter_start_time - notif_start

        if elapsed_time_n > t_notif:
            notify_email(src_email, src_pass, smtp_host, smtp_port,
                         dest_emails, log_csv, log_filename)
            notif_start = iter_start_time
            elapsed_time_n = 0
        elapsed_time = iter_start_time - start_time

    return jsonify(success=True)

@app.route('/shutdown', methods=['GET'])
def shutdown():
    sys.exit(0)
    socketio.stop()
    return 'Exited'

# Handle the webapp connecting to the websocket
@socketio.on('connect')
@cross_origin()
def test_connect():
    print('someone connected to websocket')
    emit('responseMessage', {'data': 'Connected!'})


@socketio.on_error_default  # handles all namespaces without an explicit error handler
def default_error_handler(e):
    print('An error occured:')
    print(e)
