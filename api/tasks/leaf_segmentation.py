from .abstract_task import AbstractTask
from detectron2.config import get_cfg
from detectron2.engine import DefaultPredictor
from detectron2.data.datasets import register_coco_instances
from detectron2 import model_zoo
import os
import uuid

class LeafSegmentation(AbstractTask):

    def __init__(self, img):
        self.img = img
        self.model_path = 'tasks/models/Detectron2/output/leaf_seg_final.pth'
        self.cfg = get_cfg()

    def perform_task(self):
        self.cfg.merge_from_file(model_zoo.get_config_file("COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x.yaml"))
        self.cfg.MODEL.ROI_HEADS.NUM_CLASSES = 1
        self.cfg.MODEL.WEIGHTS = os.path.join(self.model_path)
        self.cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = 0.55

        predictor = DefaultPredictor(self.cfg)
        output_mask = predictor(self.img)['instances'].to("cpu").pred_masks
        
        return output_mask
        