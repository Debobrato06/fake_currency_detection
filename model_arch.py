"""
Model definition for Bangladeshi banknote authentication (genuine vs counterfeit).

Backbone : EfficientNet-B0 pretrained on ImageNet (transfer learning)
Head     : dropout + linear layer -> 2 classes  [0 = fake, 1 = real]

The penultimate 1280-d embedding is also exposed so the detector can tell when an
input does not look like the banknotes the model was trained on (out-of-distribution
gate, see detector.py).
"""
import torch
import torch.nn as nn
from torchvision import models, transforms

CLASSES = ["fake", "real"]
IMG_SIZE = 288
MEAN = [0.485, 0.456, 0.406]
STD = [0.229, 0.224, 0.225]


class TakaAuthNet(nn.Module):
    def __init__(self, pretrained=True):
        super().__init__()
        weights = models.EfficientNet_B0_Weights.IMAGENET1K_V1 if pretrained else None
        backbone = models.efficientnet_b0(weights=weights)
        self.features = backbone.features
        self.pool = nn.AdaptiveAvgPool2d(1)
        self.head = nn.Sequential(nn.Dropout(0.3), nn.Linear(1280, len(CLASSES)))

    def embed(self, x):
        return torch.flatten(self.pool(self.features(x)), 1)

    def forward(self, x, return_embedding=False):
        emb = self.embed(x)
        logits = self.head(emb)
        return (logits, emb) if return_embedding else logits


def train_transform(img_size=IMG_SIZE):
    # Strong colour/geometry augmentation so the model learns print texture and
    # security features rather than lighting or the table the note was lying on.
    return transforms.Compose([
        transforms.RandomResizedCrop(img_size, scale=(0.35, 1.0), ratio=(0.75, 1.33)),
        transforms.RandomRotation(10),
        transforms.ColorJitter(brightness=0.4, contrast=0.4, saturation=0.3, hue=0.04),
        transforms.RandomApply([transforms.GaussianBlur(5, sigma=(0.1, 1.5))], p=0.2),
        transforms.ToTensor(),
        transforms.Normalize(MEAN, STD),
    ])


def eval_transform(img_size=IMG_SIZE):
    # Resize, then keep the central part of the photo (drops most of the background).
    return transforms.Compose([
        transforms.Resize(int(img_size * 1.15)),
        transforms.CenterCrop(img_size),
        transforms.ToTensor(),
        transforms.Normalize(MEAN, STD),
    ])
