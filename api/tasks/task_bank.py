import pdb
from .leaf_disease import LeafDisease
from .wheat_detection import WheatDetection
from .leaf_segmentation import LeafSegmentation

def inference(img, task_name):
    task_obj = None
    
    if task_name == 'LeafDisease':
        task_obj = LeafDisease(img)
    elif task_name == 'WheatDetection':
        task_obj = WheatDetection(img)
    elif task_name == 'LeafSegmentation':
        task_obj = LeafSegmentation(img)
    outputs = task_obj.perform_task()
    
    return outputs

