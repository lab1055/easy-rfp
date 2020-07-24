import pdb
from .leaf_disease import LeafDisease
from .wheat_detection import WheatDetection

def inference(img, task_name):
    task_obj = None
    if task_name == 'LeafDisease':
        task_obj = LeafDisease(img)
    elif task_name == 'WheatDetection':
        task_obj = WheatDetection(img)
    outputs = task_obj.perform_task()

    return outputs

