from typing import Callable, Optional
import torch
import torch.nn as nn
import numpy as np
from nn_data.creator import DatasetCreator
from .plots import plot_loss_accuracy, plot_test_output
import tqdm


def split_dataset(
    batch_size: int,
    dataset: torch.utils.data.dataset.TensorDataset,
):
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


def training(
    model: nn.Module,
    device: torch.device,
    dataset_split: tuple,
    loss_func: nn.Module,
    optimizer: torch.optim.Optimizer,
    num_epochs: int,
    calc_accuracy: Optional[Callable] = None,
):
    train_loader, val_loader, _ = dataset_split

    val_loss_history = []
    val_acc_history = []
    train_loss_history = []
    train_acc_history = []
    for _ in tqdm.tqdm(range(num_epochs)):
        train_loss_epoch = []
        train_acc_epoch = []
        for inputs, targets in train_loader:
            inputs, targets = inputs.to(device), targets.to(device)

            optimizer.zero_grad()
            outputs = model(inputs)
            loss = loss_func(outputs, targets)
            loss.backward()
            optimizer.step()

            train_loss_epoch.append(loss.cpu().detach().numpy())
            if calc_accuracy:
                train_acc_epoch.append(calc_accuracy(
                    outputs.cpu().detach().numpy(), targets.cpu().detach().numpy()))

        # Validation after an epoch
        model.eval()
        val_loss_epoch = []
        val_acc_epoch = []
        for inputs, targets in val_loader:
            inputs, targets = inputs.to(device), targets.to(device)

            outputs = model(inputs)
            loss = loss_func(outputs, targets)
            val_loss_epoch.append(loss.detach().cpu().numpy())
            if calc_accuracy:
                val_acc_epoch.append(calc_accuracy(
                    outputs.cpu().detach().numpy(), targets.cpu().detach().numpy()))

        train_loss_history.append(np.mean(train_loss_epoch))
        val_loss_history.append(np.mean(val_loss_epoch))
        if calc_accuracy:
            train_acc_history.append(np.mean(train_acc_epoch))
            val_acc_history.append(np.mean(val_acc_epoch))

        # put model back into training mode
        model.train()
    plot_loss_accuracy(train_loss_history, val_loss_history,
                       train_acc_history, val_acc_history)


def test(
    model: nn.Module,
    device: torch.device,
    dataset_split: tuple,
    data_creator: DatasetCreator,
    print_real_effect: Optional[Callable] = None,
    calc_accuracy: Optional[Callable] = None,
    sort_output_by_confidence: bool = False,
    plot_outputs: bool = False,
    plot_decide: bool = False,
):
    _, _, test_loader = dataset_split

    outputs, targets = [], []
    test_acc = []
    for inputs, targets in test_loader:
        inputs, targets = inputs.to(device), targets.to(device)

        outputs = model(inputs)

        outputs, targets = outputs.cpu().detach().numpy(), targets.cpu().detach().numpy()

        if calc_accuracy:
            test_acc.append(calc_accuracy(outputs, targets))

    if calc_accuracy:
        test_acc = np.mean(test_acc)
        print(f'Test Accuracy: {test_acc:.3f}\n')

    if print_real_effect:
        print_real_effect(outputs, targets)

    if plot_outputs:
        if plot_decide:
            clamped = [int(e > 0.5) for e in outputs[0]]
        else:
            clamped = np.clip(outputs[0], 0, 1)
        plot_test_output(clamped, targets[0])
