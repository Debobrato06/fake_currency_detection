import torch
import torch.nn as nn
import torch.nn.functional as F

class SEBlock(nn.Module):
    """Squeeze-and-Excitation Block to focus on important forensic features."""
    def __init__(self, channels, reduction=16):
        super(SEBlock, self).__init__()
        self.avg_pool = nn.AdaptiveAvgPool2d(1)
        self.fc = nn.Sequential(
            nn.Linear(channels, channels // reduction, bias=False),
            nn.ReLU(inplace=True),
            nn.Linear(channels // reduction, channels, bias=False),
            nn.Sigmoid()
        )

    def forward(self, x):
        b, c, _, _ = x.size()
        y = self.avg_pool(x).view(b, c)
        y = self.fc(y).view(b, c, 1, 1)
        return x * y.expand_as(x)

class CurrencyForensicNet(nn.Module):
    """
    Advanced Forensic Autoencoder with Attention.
    Learns the 'Perfect Distribution' of real bank notes.
    """
    def __init__(self):
        super(CurrencyForensicNet, self).__init__()
        
        # Encoder: Extracting micro-features (Watermarks, Threads)
        self.encoder = nn.Sequential(
            nn.Conv2d(3, 64, kernel_size=3, padding=1),
            nn.ReLU(),
            SEBlock(64),
            nn.MaxPool2d(2, 2), # 256
            
            nn.Conv2d(64, 128, kernel_size=3, padding=1),
            nn.ReLU(),
            SEBlock(128),
            nn.MaxPool2d(2, 2), # 128
            
            nn.Conv2d(128, 256, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2, 2)  # 64 (Intermediate Forensic Representation)
        )
        
        # Decoder: Attempting to reconstruct the 'Genuine' version
        self.decoder = nn.Sequential(
            nn.ConvTranspose2d(256, 128, kernel_size=2, stride=2),
            nn.ReLU(),
            nn.ConvTranspose2d(128, 64, kernel_size=2, stride=2),
            nn.ReLU(),
            nn.ConvTranspose2d(64, 3, kernel_size=2, stride=2),
            nn.Sigmoid()
        )

    def forward(self, x):
        latent = self.encoder(x)
        reconstruction = self.decoder(latent)
        return reconstruction, latent

def get_anomaly_score(original, reconstructed):
    """Calculates MSE between original and reconstructed image."""
    return F.mse_loss(original, reconstructed).item()
