import torch
import torch.optim as optim
import torch.nn as nn
from torch.utils.data import DataLoader, Dataset
import cv2
import os
from model_arch import CurrencyForensicNet
import numpy as np

class RealCurrencyDataset(Dataset):
    """Dataset loader for Genuine Bank Notes."""
    def __init__(self, folder_path, img_size=(512, 512)):
        self.files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith(('.jpg', '.png'))]
        self.img_size = img_size

    def __len__(self):
        return len(self.files)

    def __getitem__(self, idx):
        img = cv2.imread(self.files[idx])
        img = cv2.resize(img, self.img_size)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        tensor = torch.from_numpy(img).permute(2, 0, 1).float() / 255.0
        return tensor

def train_anomaly_detector(data_path, epochs=50, batch_size=4):
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model = CurrencyForensicNet().to(device)
    optimizer = optim.Adam(model.parameters(), lr=1e-4)
    criterion = nn.MSELoss()
    
    dataset = RealCurrencyDataset(data_path)
    loader = DataLoader(dataset, batch_size=batch_size, shuffle=True)
    
    print(f"Starting Training on {len(dataset)} real samples...")
    
    for epoch in range(epochs):
        total_loss = 0
        for batch in loader:
            batch = batch.to(device)
            optimizer.zero_grad()
            
            reconstructed, _ = model(batch)
            loss = criterion(reconstructed, batch)
            
            loss.backward()
            optimizer.step()
            total_loss += loss.item()
            
        print(f"Epoch [{epoch+1}/{epochs}], Loss: {total_loss/len(loader):.6f}")
        
    torch.save(model.state_dict(), "currency_forensic_model.pth")
    print("Optimization Complete. Model saved as currency_forensic_model.pth")

if __name__ == "__main__":
    # Create a dummy folder if it doesn't exist to show usage
    if not os.path.exists("training_data"):
        os.makedirs("training_data")
        print("Please place your Real/Genuine bank note images in the 'training_data' folder and run this script.")
    else:
        train_anomaly_detector("training_data")
