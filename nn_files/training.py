# -*- coding: utf-8 -*-
"""
Created on Sat Apr 23 13:30:32 2022

@author: robin
"""

import torch
import torch.nn as nn
import numpy as np
from nn_data.creator import DatasetCreator


def split_dataset(batch_size: int, dataset):
    # split dataset into training, validation and test
    train_size = int(len(dataset)*0.7)
    val_size = int(len(dataset)*0.2)
    test_size = len(dataset) - (train_size + val_size)

    train_set, val_set, test_set = torch.utils.data.random_split(
        dataset, [train_size, val_size, test_size])

    train_loader = torch.utils.data.DataLoader(
        train_set, batch_size=batch_size, shuffle=True)
    val_loader = torch.utils.data.DataLoader(
        val_set, batch_size=batch_size, shuffle=False)
    test_loader = torch.utils.data.DataLoader(
        test_set, batch_size=1, shuffle=False)
    return train_loader, val_loader, test_loader


def training(model: nn.Module, optimizer: torch.optim.Optimizer,
             loss_func,
             learning_rate: int, num_epochs: int, batch_size: int,
             device: torch.device, dataset_split: tuple,
             real_effect=None, log_rhythm: int = None, calc_accuracy=None
             ):

    train_loader, val_loader, _ = dataset_split

    val_loss_history = []
    for epoch in range(num_epochs):
        print(f'[Epoch {epoch+1}/{num_epochs}]')

        train_loss_history = []
        train_acc_history = []

        for i, (inputs, targets) in enumerate(train_loader, 1):
            inputs, targets = inputs.to(device), targets.to(device)

            optimizer.zero_grad()
            outputs = model(inputs)
            loss = loss_func(outputs, targets)
            loss.backward()
            optimizer.step()

            # Loss output after log_rhythm of iterations
            train_loss_history.append(loss.cpu().detach().numpy())
            if calc_accuracy:
                train_acc_history.append(calc_accuracy(
                    outputs.cpu().detach().numpy(), targets.cpu().detach().numpy()))
            else:
                train_acc_history.append(0.0)

            if log_rhythm:
                if i % log_rhythm == 0:
                    last_log_rhythm_losses = train_loss_history[-log_rhythm:]
                    train_loss = np.mean(last_log_rhythm_losses)

                    # train_acc_history.flatten()
                    last_log_rhythm_acc = train_acc_history[-log_rhythm:]
                    train_acc = np.mean(last_log_rhythm_acc)

                    print(
                        f'[Iteration {i}]\tTRAIN      loss/acc: {train_loss:.3f}\t{train_acc:.3f}')

            # Acc computation during after log_rhythm of iterations

        # Loss and acc output after an epoch
        train_loss = np.mean(train_loss_history)
        if calc_accuracy:
            train_acc = np.mean(train_acc_history)
        else:
            train_acc = 0.0
        print(
            f'for this epoch:\tTRAIN      loss/acc: {train_loss:.3f}\t{train_acc:.3f}')

        # Validation after an epoch
        val_losses = []
        val_accs = []
        model.eval()
        for inputs, targets in val_loader:
            inputs, targets = inputs.to(device), targets.to(device)

            outputs = model(inputs)
            loss = loss_func(outputs, targets)
            val_losses.append(loss.detach().cpu().numpy())
            if calc_accuracy:
                val_accs.append(calc_accuracy(
                    outputs.cpu().detach().numpy(), targets.cpu().detach().numpy()))

        # Training step after an epoch
        model.train()

        val_loss = np.mean(val_losses)
        if calc_accuracy:
            val_acc = np.mean(val_accs)
        else:
            val_acc = 0.0

        # Output of Validation loss
        val_loss_history.append(val_loss)
        print(f'\t\tVALIDATION loss/acc: {val_loss:.3f}\t{val_acc:.3f}')
        if real_effect:
            real_effect(outputs, targets)
            print("\n")


def test(model: nn.Module, loss_func,
         device: torch.device, dataset_split: tuple,
         target_data_creator: DatasetCreator,
         real_effect=None, calc_accuracy=None,
         ):
    test_acc = []
    _, _, test_loader = dataset_split
    for inputs, targets in test_loader:
        inputs, targets = inputs.to(device), targets.to(device)

        outputs = model(inputs)

        if calc_accuracy:
            test_acc.append(calc_accuracy(
            outputs.cpu().detach().numpy(), targets.cpu().detach().numpy()))
        else:
            test_acc.append(0.0)
        if real_effect:
            real_effect(outputs, targets)

    test_acc = np.mean(test_acc)

    print(f'Test Accuracy: {test_acc:.3f}')

    for i in range(len(outputs[0])):
        print(
            f'{target_data_creator.feature_list[i]}\t{outputs[0,i]:.2f}\t{"X" if targets[0,i] > 0 else " "}')
