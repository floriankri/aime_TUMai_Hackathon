# -*- coding: utf-8 -*-
"""
Created on Sat Apr 23 09:43:32 2022

@author: robin
"""
import torch.nn as nn


class Autoencoder(nn.Module):
    """
    This class forms the architecture of the autoencoder. The latent size which is an input
    of the init function describes the dimension of the innermost layer.
    After Training the output of this first encoder part will serve as input for the following FCN
    """
    def __init__(self, input_size, hidden_size, latent_size):
        super().__init__()
        
        # define encoder and decoder Parameters
        self.encoder = None
        self.decoder = None
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.latent_size = latent_size
        self.output_size = input_size

        # architecture and initialization of encoder
        l1 = nn.Linear(self.input_size, self.hidden_size)
        nn.init.xavier_uniform_(l1.weight)
        l2 = nn.Linear(self.hidden_size, self.latent_size)
        nn.init.xavier_uniform_(l2.weight)
        
        self.encoder = nn.Sequential(
            l1,
            nn.Tanh(),
            l2
        )
        
        #architecture and initialization of decoder
        l3 = nn.Linear(self.latent_size, self.hidden_size)
        nn.init.xavier_uniform_(l1.weight)
        l4 = nn.Linear(self.hidden_size, self.output_size)
        nn.init.xavier_uniform_(l2.weight)
        
        self.decoder = nn.Sequential(
            l3,
            nn.Tanh(),
            l4
        )
        
    def return_encoder(self):
        """
        Returns only the encoder part for further use
        """
        return self.encoder
        
    
    def forward(self, x):
        
        representation = self.encoder(x)
        reconstruction = self.decoder(representation)
        return reconstruction
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
