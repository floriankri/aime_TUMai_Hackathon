from typing import Optional
import torch.nn as nn
from .autoencoder import Autoencoder


class FCNModel(nn.Module):
    def __init__(
        self,
        input_size: int, hidden_size: int, output_size: int,
        enlarging_factor: float,
        autoencoder: Optional[Autoencoder] = None,
        dropOutRatio: float = 0,
    ):
        super().__init__()

        self.NN = nn.Identity()
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.output_size = output_size
        self.enlarging_factor = enlarging_factor
        if autoencoder:
            self.encoder = autoencoder.return_encoder()

            l1 = nn.Linear(self.input_size, self.hidden_size)
            nn.init.xavier_uniform_(l1.weight)
            d1 = nn.Dropout(p=dropOutRatio)
            l2 = nn.Linear(self.hidden_size, self.hidden_size)
            nn.init.xavier_uniform_(l2.weight)
            d2 = nn.Dropout(p=dropOutRatio)
            l3 = nn.Linear(self.hidden_size, self.output_size)
            nn.init.xavier_uniform_(l3.weight)

            # define model architecture and move to cuda
            self.NN = nn.Sequential(
                l1,
                nn.Tanh(),
                d1,
                l2,
                nn.Tanh(),
                d2,
                l3,
                nn.Sigmoid()
            )

        else:
            self.encoder = None

            l1 = nn.Linear(self.input_size, self.hidden_size)
            nn.init.xavier_uniform_(l1.weight)
            d1 = nn.Dropout(p=dropOutRatio)
            l2 = nn.Linear(self.hidden_size, self.hidden_size)
            nn.init.xavier_uniform_(l2.weight)
            d2 = nn.Dropout(p=dropOutRatio)
            l3 = nn.Linear(self.hidden_size, self.output_size)
            nn.init.xavier_uniform_(l3.weight)

            # define model architecture and move to cuda
            self.NN = nn.Sequential(
                l1,
                nn.Tanh(),
                d1,
                l2,
                nn.Tanh(),
                d2,
                l3,
                nn.Sigmoid()
            )

    def forward(self, x):
        if self.encoder:
            x = self.encoder(x)
        x = self.NN(x)
        return x
