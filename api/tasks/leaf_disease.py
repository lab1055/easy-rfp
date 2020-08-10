import torch
from torchvision import datasets, transforms, models
import torch.nn.functional as F
from .abstract_task import AbstractTask

class LeafDisease(AbstractTask):

    def __init__(self, img):
        self.img = img
        self.model_path = 'tasks/models/LeafDisease/output/leaf_stress_resnet18.pt'
        self.transform=transforms.Compose([
                       transforms.ToTensor(),
                       transforms.Normalize((0.4914, 0.4822, 0.4465), (0.2023, 0.1994, 0.2010) )
                   ])

    def perform_task(self):
        model = models.resnet18(pretrained=False)
        model.fc = torch.nn.Linear(512, 9, bias=True)
        model.load_state_dict(torch.load(self.model_path))
        model.eval()
        img_t = self.transform(self.img)
        batch_t = torch.unsqueeze(img_t, 0)
        out = model(batch_t)
        with open('tasks/models/LeafDisease/leaf_disease_classes.txt') as f:
            classes = [line.strip() for line in f.readlines()]
        _, index = torch.max(out, 1)
        percentage = torch.nn.functional.softmax(out, dim=1)[0] * 100
        return (classes[index[0]], percentage[index[0]].item())