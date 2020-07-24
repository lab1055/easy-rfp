# EasyRFP: An Easy to Use Edge Computing Toolkit for Real-Time Field Phenotyping

## Installation
Code is tested on Python 3.7 and 3.8. Works on both Windows and Linux systems.

To use the basic template of the toolkit (without pretrained models)
```
gphoto2==2.2.2
opencv-python==4.2.0
Flask==1.1.2
Flask-Cors==3.0.8
Flask-SocketIO==4.3.1
```
NodeJS Anaconda install:
```
conda install -c conda-forge nodejs
```
Direct install:
```
npm install
```


To use/test the provided pretrained models, you will need
```
detectron2==0.1.3+cu101
torch==1.5.0+cu101
torchvision==0.6.0+cu101
```

## Execution

### Run Flask Backend Server 
Inside `api/` do

Linux:
```
> export FLASK_APP=api
> flask run
```

Windows:
```
> set FLASK_APP=api
> flask run
```

### Run Angular Frontend Server
Inside `client-app/` do
```
nm serve
```

Access the UI at https://localhost:4200/. If you port it to your local machine with `--host=0.0.0.0` command, access UI at https://192.168.X.X:4200/. Also, please change the `SOCKET_ENDPOINT` variable accordingly with your IP address in `client-app/src/environments/environment.ts` 

### Some More Configuration

```
IO:
  LOGS_SAVE_DIR: logs/
EMAIL:
  # While you are free to use any email id, you are recommended to create
  # a throwaway email id at any provider supporting SMTP (ex: Gmail).
  # The only purpose of this email id is to send emails on behalf of the Jetson.
  # Make sure you don't have any personal information connected to this email id
  # to ensure security. Please know that you have been warned.
  SRC_EMAIL_ID: dummy@yandex.com
  SRC_EMAIL_PASSWORD: dummypassword
  SMTP_SERVER: smtp.yandex.com #smtp server of your email provider -> ex: smtp.gmail.com
  SMTP_PORT: 465 # ex: 587
SESSION_NAME: your_desired_name # or auto (session folder will be timestamp string if auto) 
```

## How To Add Your Own Task

* Create task python file in `tasks` directory, say `dummy_task.py`
* Declare a class whose constructor takes a cv2 image as input, say `DummyTaskClass`.
* Include a method `perform_task()` that uses the input image, trained model, and _your own_ inference code to output result appropriately. 
    * If it is a detection task, the method must return a list of tuples, where each tuple looks as follows: `(classname, [x, y, width, height])`
    * If it is a classification task, the method must return a tuple as follows: `(class_name, class_probability)`
    * Please refer to `tasks/wheat_detection.py` and `task/leaf_disease.py` to know more.
* Once `DummyTaskClass().perform_task()` is configured to work as above, import the class in `tasks/task_bank.py`
    * Something like `from .dummy_task import DummyTaskClass`
    * Add a simple `if` statement inside the `inference()` method to work based on the task name (provided in YAML) and you are good to go. 
    * The `task_bank.py` could look as follows
    ``` 
    from .some_other_task import SomeOtherTask
    ##### Newly added 
    from .dummy_task import DummyTaskClass
    def inference(img, task_name):
        task_obj = None
        if task_name == `SomeOtherTask`:
            task_obj = SomeOtherTask(img)
        ##### Newly added
        elif task_name == 'DummyTaskName':
            task_obj = DummyTaskClass(img)
        
        outputs = task_obj.perform_task()
        return outputs
    ```
* Finally, add the newly added task to `alltasks.yaml` as follows
```
- name: DummyTaskName
  display_name: Dummy Task
  task_type: classification (or detection)
```

## Pretrained Models 

* Wheat Ear Detection - [FasterRCNN ResNet101](https://www.google.com/url?q=https://www.dropbox.com/s/74hvt7ykzg42tg7/wheat_head_frcnn.pth?dl%3D0&sa=D&source=hangouts&ust=1592644895243000&usg=AFQjCNHaJ6uUhi1fmsskQy-gN2vz93RB1A)
* Leaf Disease Classification - [ResNet18](https://www.google.com/url?q=https://www.dropbox.com/s/8kzeyeopz8t5tpk/leaf_stress_resnet50.pth?dl%3D0&sa=D&source=hangouts&ust=1592644882326000&usg=AFQjCNFSeyA11V5HKlJHj72VvP4rdieY_g)

Add these models to the project and provide the path in `tasks/wheat_detection.py` or `tasks/leaf_disease.py`. Please check the training code for these two tasks at `tasks/models/`.