from .abstract_task import AbstractTask
from detectron2.config import get_cfg
from detectron2.engine import DefaultPredictor
from detectron2.data.datasets import register_coco_instances
from detectron2 import model_zoo
import os
import uuid

class WheatDetection(AbstractTask):

    def __init__(self, img):
        self.img = img
        self.model_path = 'tasks/models/Detectron2/output/wheat_head_frcnn.pth'
        self.cfg = get_cfg()

    def perform_task(self):
        self.cfg.merge_from_file(model_zoo.get_config_file("COCO-Detection/faster_rcnn_R_101_FPN_3x.yaml"))
        self.cfg.DATASETS.TEST = ("wheat_val",)
        self.cfg.MODEL.ROI_HEADS.NUM_CLASSES = 1
        self.cfg.MODEL.WEIGHTS = os.path.join(self.model_path)
        self.cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = 0.55

        predictor = DefaultPredictor(self.cfg)
        outputs = predictor(self.img)
        boxes = {}
        for coordinates in outputs["instances"].to("cpu").pred_boxes:
            coordinates_array = []
            for k in coordinates:
                coordinates_array.append(int(k))

            boxes[uuid.uuid4().hex[:].upper()] = coordinates_array 
        return boxes