# EasyRFP: An Easy to Use Edge Computing Toolkit for Real-Time Field Phenotyping
We propose EasyRFP, an edge computing toolkit for real-time field phenotyping. Recent advances in deep learning have catalysed rapid progress in high throughput field phenotyping. Much research has been dedicated towards developing accurate and cost effective deep learning models to capture phenotyping traits such as plant stress, yield and plant growth stages. 

However, there is a shortage of software tools to promote the usage of such intelligent methods among plant phenotyping practitioners and researchers. To bridge this gap, we developed this, a Flask backend, Angular frontend software toolkit. Broadly speaking, our toolkit can be interfaced with a commercial GPU enabled micro computer (such as NVIDIA Jetson) and a digital camera. Precisely, our toolkit can be used to capture images and extract phenotypic traits in both real-time and in scheduled mode. Currently, we support classification, detection and instance segmentation tasks. 

## Demonstration (Video)
[![IMAGE ALT TEXT HERE](https://img.youtube.com/vi/oAGbpVgPE6U/0.jpg)](https://www.youtube.com/watch?v=oAGbpVgPE6U)

## Installation
Toolkit is tested only on Python 3.6. Works on both Windows and Linux systems.  

To use the basic template of the toolkit (without pretrained models)
```
gphoto2==2.2.2
opencv-python==4.4.0
Flask==1.1.2
Flask-Cors==3.0.8
Flask-SocketIO==4.3.1
onnx==1.7.0
onnxruntime==1.5.2
```

NodeJS & Angular installation:
```
> pip install nodeenv
> nodeenv -p
> npm install
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
> ng serve
```

Access the UI at http://localhost:4200/. If you port it to your local machine with `--host=0.0.0.0` command, access UI at http://192.168.X.X:4200/. Also, please change the `SOCKET_ENDPOINT` variable accordingly with your IP address in `client-app/src/environments/environment.ts` 

### Some More Configuration

```
IMAGE:
  # Resizing is important since the DSLR captured images are huge (5000x4000 approximately) 
  # The Flask server could die trying to work with such huge images
  RESIZE_WIDTH: 640 # in pixels
  RESIZE_HEIGHT: 640 # in pixels
IO:
  LOGS_SAVE_DIR: logs/ # created inside api/
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
    * If it is a segmentation task, the method must return a mask image (torch tensor) of size equal to the input: `torch.Tensor` 
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
* Finally, add the newly added task to `tasks/alltasks.yaml` as follows
    ```
    - name: DummyTaskName
      display_name: Dummy Task
      task_type: classification (or detection/segmentation)
    ```

## Pretrained Models 

* Wheat Ear Detection - [FasterRCNN ResNet101](https://www.dropbox.com/s/74hvt7ykzg42tg7/wheat_head_frcnn.pth) (480 MB)
* Leaf Disease Classification - [ResNet18 (PyTorch)](https://www.dropbox.com/s/8kzeyeopz8t5tpk/leaf_stress_resnet50.pth) and [ResNet18 (ONNX)](https://www.dropbox.com/s/qe6wpkv1yq1fz4q/leaf_stress_resnet50.onnx) (45 MB)
* Leaf Segmentation - [MaskRCNN ResNet50](https://www.dropbox.com/s/7nobrkr6i2dnwg1/leaf_seg_final.pth) (350 MB)

Add these models to the project and provide the path in `tasks/wheat_detection.py` or `tasks/leaf_disease.py` or `tasks/leaf_segmentation.py`. Please check the training code for these three tasks at `tasks/models/`.


To use/test the provided pretrained models, you will need
```
detectron2==0.1.3+cu101
torch==1.5.0+cu101
torchvision==0.6.0+cu101
```

To install PyTorch and torchvision on the NVIDIA Jetson, you can follow the installation instructions [provided here](https://forums.developer.nvidia.com/t/pytorch-for-jetson-nano-version-1-6-0-now-available/72048). Detectron2 can be installed with the following command:
```
python -m pip install 'git+https://github.com/facebookresearch/detectron2.git'
```

## Citation
```
@article{easyrfp2020,
    Author = {Sai Vikas Desai, Akshay L Chandra, Masayuki Hirafuji, Seishi Ninomiya, Vineeth N Balasubramanian, Wei Guo},
    Title = {EasyRFP: An Easy to Use Edge Computing Toolkit for Real-Time Field Phenotyping},
    Journal = {https://github.com/lab1055/easy-rfp},
    Year = {2020}
}
```
