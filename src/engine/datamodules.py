import pytorch_lightning as pl
from torch.utils.data import DataLoader, Dataset
from src.alpha_factory.kdb_interface import KDBInterface
import torch

class KDBDataset(Dataset):
    def __init__(self, symbols, mode="hdb"):
        self.kdb = KDBInterface(mode=mode)
        # Fetch a large historical block from kdb+ for training
        self.data = self.kdb.get_vwap_bars(symbols, window_minutes=5)
        
    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        # Convert kdb+/Pandas row to PyTorch Tensor
        row = self.data.iloc[idx].values
        return torch.tensor(row, dtype=torch.float32)

class AxiomDataModule(pl.LightningDataModule):
    """
    Bridges kdb+ time-series data with PyTorch Lightning training.
    Handles splitting, shuffling, and distributed loading.
    """
    def __init__(self, symbols, batch_size=256):
        super().__init__()
        self.symbols = symbols
        self.batch_size = batch_size

    def setup(self, stage=None):
        # Initialize the high-performance kdb+ dataset
        self.full_dataset = KDBDataset(self.symbols)
        # Simple split for demonstration
        train_size = int(0.8 * len(self.full_dataset))
        self.train_ds, self.val_ds = torch.utils.data.random_split(
            self.full_dataset, [train_size, len(self.full_dataset) - train_size]
        )

    def train_dataloader(self):
        return DataLoader(self.train_ds, batch_size=self.batch_size, shuffle=False, num_workers=4)

    def val_dataloader(self):
        return DataLoader(self.val_ds, batch_size=self.batch_size)