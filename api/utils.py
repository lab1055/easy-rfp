import csv
import pdb
import pprint
from datetime import datetime
import copy
import cv2
import os
import io

import numpy as np

import smtplib

from string import Template
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from email.utils import make_msgid

import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvas

def save_and_log_results(img, outputs, img_name, img_save_dir, results_save_dir, log_filename, task_type, socketio):
    
    if task_type == 'detection':
        log_csv = save_and_log_det_results(
            img, outputs, img_name, img_save_dir, results_save_dir, log_filename, socketio)
    elif task_type == 'classification':
        log_csv = save_and_log_clf_results(
            img, outputs, img_name, img_save_dir, results_save_dir, log_filename, socketio)
    elif task_type == 'segmentation':
        log_csv = save_and_log_seg_results(
            img, outputs, img_name, img_save_dir, results_save_dir, log_filename, socketio)
    
    return log_csv


# Detection methods
def save_and_log_det_results(img, outputs, img_name, img_save_dir, results_save_dir, log_filename, socketio):

    # save input image to images/
    cv2.imwrite(os.path.join(img_save_dir, img_name), img)

    # save resultant image with boxes drawn
    img_with_dets = draw_rectangles(img, outputs)
    result_img_loc = os.path.join(results_save_dir, img_name)
    cv2.imwrite(result_img_loc, img_with_dets)
    
    # save output to results/
    result_ann_loc = os.path.join(results_save_dir, f"{img_name.split('.')[0]}.txt")
    with open(result_ann_loc, "w", newline="") as f:
        writer = csv.writer(f)
        for k,b in outputs.items():
            writer.writerow([f'{b[0]},{b[1]},{b[2]},{b[3]}'])
    return log_det_results(outputs, result_img_loc, result_ann_loc, log_filename, socketio)


def log_det_results(boxes, output_img_loc, output_ann_loc, log_filename, socketio):

    # csv filename
    csv_log = log_filename[:-4] + '.csv'

    if not os.path.exists(csv_log):
        with open(csv_log, 'w') as f:
            writer = csv.writer(f)
            writer.writerow(['Time Captured', 'Image Result Location',
                             'Image Inference Location', 'Number of Objects'])

    with open(csv_log, 'a') as f:
        writer = csv.writer(f)

        now = datetime.now()
        now_text = now.strftime("%d/%m/%Y %H:%M:%S")

        writer.writerow([now_text, output_img_loc, output_ann_loc, len(boxes)])

    text = f'\nImage captured and processed at {now_text} \n'
    text += f'Results saved at {output_ann_loc} \n'
    text += f'Number of objects detected: {str(len(boxes))} \n'
    text += f'Result summary written to: {csv_log} \n'

    # emit socket event
    socketio.emit('Logs', {'data': text})

    log_generic(text, log_filename)

    return csv_log


def draw_rectangles(img, boxes):

    color = (255, 0, 0)
    thickness = 2

    for k, b in boxes.items():
        img = cv2.rectangle(img, (b[0], b[1]), (b[2], b[3]), color, thickness)
    
    return img


# Classification methods
def save_and_log_clf_results(img, outputs, img_name, img_save_dir, results_save_dir, log_filename, socketio):
    
    # save input image to images/
    image_path = os.path.join(results_save_dir, img_name)
    cv2.imwrite(image_path, img)
    
    return log_clf_results(outputs, image_path, results_save_dir, log_filename, socketio)


def log_clf_results(outputs, image_path, results_save_dir, log_filename, socketio):
    (class_name, prob) = outputs

    # csv filename
    csv_log = log_filename[:-4] + '.csv'

    if not os.path.exists(csv_log):
        with open(csv_log, 'w') as f:
            writer = csv.writer(f)
            writer.writerow(['Time Captured', 'Image Location',
                             'Class Name', 'Class Probability'])

    with open(csv_log, 'a') as f:
        writer = csv.writer(f)

        now = datetime.now()
        now_text = now.strftime("%d/%m/%Y %H:%M:%S")

        writer.writerow([now_text, image_path, class_name, prob])

    text = f'\nImage captured and processed at {now_text} \n'
    text += f'Image saved at {image_path} \n'
    text += f'Predicted Class Name: {class_name} \n'
    text += f'Class Probability: {str(prob)} \n'

    # emit socket event
    socketio.emit('Logs', {'data': text})

    log_generic(text, log_filename)

    return csv_log


# Segmentation methods
def save_and_log_seg_results(img, outputs, img_name, img_save_dir, results_save_dir, log_filename, socketio):
    output_mask = outputs.permute(1,2,0)
    # save input image to images/
    cv2.imwrite(os.path.join(img_save_dir, img_name), img)
    
    # save output mask to results/
#     cv2.imwrite(os.path.join(results_save_dir, img_name), np.array(output_mask, dtype=np.float32))
    
    # save segmentation overlay + mask (side by side) to results/ 
    img_with_mask_fig = overlay_mask(img, output_mask)
    canvas = FigureCanvas(img_with_mask_fig)
    canvas.draw()
    img_with_mask = np.array(canvas.renderer.buffer_rgba())
#     output_img_loc = os.path.join(results_save_dir, f"{img_name.split('.')[0]}_mask_overlay.{img_name.split('.')[1]}")
    output_img_loc = os.path.join(results_save_dir, img_name)
    cv2.imwrite(output_img_loc, img_with_mask)
    
    return log_seg_results(output_mask, output_img_loc, log_filename, socketio)


def log_seg_results(output_mask, output_img_loc, log_filename, socketio):
    
    # csv filename
    csv_log = log_filename[:-4] + '.csv'
    
    mask_area = output_mask.sum().item()/(output_mask.shape[0]*output_mask.shape[1])
    
    if not os.path.exists(csv_log):
        with open(csv_log, 'w') as f:
            writer = csv.writer(f)
            writer.writerow(['Time Captured', 'Output Mask Location', 'Area of Mask'])

    with open(csv_log, 'a') as f:
        writer = csv.writer(f)

        now = datetime.now()
        now_text = now.strftime("%d/%m/%Y %H:%M:%S")

        writer.writerow([now_text, output_img_loc, mask_area])

    text = f'\nImage captured and processed at {now_text} \n'
    text += f'Results saved at {output_img_loc} \n'
    
    text += f'Area of segmentation mask: {str(mask_area)} \n'
    text += f'Result summary written to: {csv_log} \n'

    # emit socket event
    socketio.emit('Logs', {'data': text})

    log_generic(text, log_filename)

    return csv_log


def overlay_mask(img, output_mask):
    
    fig = plt.figure(figsize=(6, 3))
    plt.subplot(1,2,1)
    masked = np.ma.masked_where(output_mask == 0, output_mask)
    plt.imshow(np.asarray(img), 'gray', interpolation='none')
    plt.imshow(masked, 'jet', interpolation='none', alpha=0.8)
    plt.axis('off')
    
    plt.subplot(1,2,2)
    plt.imshow(output_mask, cmap='gray')
    plt.axis('off')
    
    return fig


def time_human(seconds):
    hours = int(seconds / 3600)
    seconds %= 3600
    minutes = int(seconds/60)
    seconds %= 60
    return "%d hours %d minutes %d seconds" % (hours, minutes, seconds)


def log_generic(text, filename):
    print(text)
    with open(filename, 'a') as f:
        f.write(text)


def log_started_realtime(cfg, filename):

    text = ''

    cfg_ = copy.deepcopy(cfg)

    cfg_['EMAIL']['SRC_EMAIL_PASSWORD'] = '********'
    cfg_print = pprint.pformat(cfg_)

    now = datetime.now()
    now_text = now.strftime("%d/%m/%Y %H:%M:%S")
    started = f'Real-Time Mode Process started at: {now_text} \n'
    text += 'Contents of YAML File:\n'
    text += f'{cfg_print} \n\n\n'
    text += started
    print(text)
    with open(filename, 'a') as f:
        f.write(text)


def log_started_scheduler(cfg, capture_time, notif_time, total_time, filename):

    text = ''

    cfg_ = copy.deepcopy(cfg)

    cfg_['EMAIL']['SRC_EMAIL_PASSWORD'] = '********'
    cfg_print = pprint.pformat(cfg_)

    capture_time = time_human(capture_time)
    notif_time = time_human(notif_time)
    total_time = time_human(total_time)

    now = datetime.now()
    now_text = now.strftime("%d/%m/%Y %H:%M:%S")
    started = f'Scheduler Mode Process started at: {now_text}  \n'
    started += f'Capturing images every:  {capture_time} \n'
    started += f'Notification every: {notif_time} \n'
    started += f'Total time: {total_time} \n'
    text += 'Contents of YAML File:\n'
    text += f'{cfg_print} \n\n\n'
    text += started

    print(text)
    with open(filename, 'a') as f:
        f.write(text)


def notify_email(src_email, src_pass, smtp_host, smtp_port, dest_emails, attachment, log_filename):
    s = smtplib.SMTP_SSL(host=smtp_host, port=smtp_port)
    s.ehlo()
    s.login(src_email, src_pass)

    now = datetime.now()
    now_text = now.strftime("%d/%m/%Y %H:%M:%S")

    # create a message
    msg = MIMEMultipart()
    msg['Message-ID'] = make_msgid()

    # setup the parameters of the message
    msg['From'] = src_email
    msg['To'] = ', '.join(dest_emails)
    msg['Subject'] = "JETSON TX2 Results at "+now_text

    # add in the message body
    message = 'Please find the task summary in attachments.'
    print(f'Summary of results being attached and sent to {dest_emails} recipients.')

    msg.attach(MIMEText(message, 'plain'))

    # attach the file
    filename = os.path.split(attachment)[1]
    attch = open(attachment, 'rb')

    # instance of MIMEBase and named as p
    p = MIMEBase('application', 'octet-stream')

    # To change the payload into encoded form
    p.set_payload((attch).read())

    # encode into base64
    encoders.encode_base64(p)

    p.add_header('Content-Disposition', "attachment; filename= %s" % filename)

    # attach the instance 'p' to instance 'msg'
    msg.attach(p)

    # send the message via the server set up earlier.
    # s.send_message(msg)
    s.sendmail(src_email, dest_emails, msg.as_string())
    del msg

    s.quit()

    log_generic(f'\nNotified via email to {dest_emails} recipients!', log_filename)