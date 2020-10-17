import torch
from torchvision import datasets, transforms, models
import torch.nn.functional as F
from .abstract_task import AbstractTask
import onnxruntime
from PIL import Image

class LeafDisease(AbstractTask):
    """
    Using ONNX model
    """
    def __init__(self, img):
        self.img = Image.fromarray(img)
        self.model_path = 'tasks/models/LeafDisease/leaf_stress_resnet50.onnx'
        self.transform=transforms.Compose([
                       transforms.Resize((64,64)),                    
                       transforms.ToTensor(),
                       transforms.Normalize((0.4914, 0.4822, 0.4465), (0.2023, 0.1994, 0.2010))
                   ])
        
    def perform_task(self):
        img_t = self.transform(self.img)
        batch_t = torch.unsqueeze(img_t, 0)
        
        ort_session = onnxruntime.InferenceSession(self.model_path)

        def to_numpy(tensor):
            return tensor.detach().cpu().numpy() if tensor.requires_grad else tensor.cpu().numpy()

        # compute ONNX Runtime output prediction
        ort_inputs = {ort_session.get_inputs()[0].name: to_numpy(batch_t)}
        ort_outs = ort_session.run(None, ort_inputs)

        out = torch.from_numpy(ort_outs[0])
        with open('tasks/models/LeafDisease/leaf_disease_classes.txt') as f:
            classes = [line.strip() for line in f.readlines()]
        _, index = torch.max(out, 1)
        percentage = torch.nn.functional.softmax(out, dim=1)[0] * 100
        return (classes[index[0]], percentage[index[0]].item())

# Currently this class is not being used, it is only here for reference 
class LeafDiseasePyTorch(AbstractTask):

    def __init__(self, img):
        self.img = Image.fromarray(img)
        self.model_path = 'tasks/models/LeafDisease/output/leaf_stress_resnet18.pt'
        self.transform=transforms.Compose([
                       transforms.Resize((64,64)),                    
                       transforms.ToTensor(),
                       transforms.Normalize((0.4914, 0.4822, 0.4465), (0.2023, 0.1994, 0.2010))
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