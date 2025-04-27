# /*-----------------------------------------------------------------------*
# These coded instructions, statements, and computer programs contain proprietary
# information its licensed developers and are protected by
# national and international copyright laws. They may not be disclosed to third
# parties or copied or duplicated in any form, in whole or in part, without the
# prior written consent
# The content herein is highly confidential and should be handled accordingly.
# *-----------------------------------------------------------------------*/

import torch
import torch.nn as nn


class NNRegressor(nn.Module):
    """This class implements a simple feedforward neural network regressor."""

    hidden_size = 512

    def __init__(
        self,
        nb_dimensions,
    ):
        super().__init__()
        self.fc = nn.Sequential(
            nn.Linear(nb_dimensions, self.hidden_size),
            nn.LeakyReLU(),
            nn.Linear(self.hidden_size, self.hidden_size),
            nn.LeakyReLU(),
            nn.Linear(self.hidden_size, self.hidden_size),
            nn.LeakyReLU(),
            nn.Linear(self.hidden_size, self.hidden_size),
            nn.LeakyReLU(),
            nn.Linear(self.hidden_size, 1),
        )
        self._initialize_weights()

    def _initialize_weights(self):
        for m in self.fc:
            if isinstance(m, nn.Linear):
                nn.init.xavier_uniform_(m.weight)
                nn.init.zeros_(m.bias)

    def forward(self, inputs):
        output = self.fc(inputs)
        return output

    def load_weights(self, weight_file, device):
        self.load_state_dict(torch.load(weight_file, map_location=device))

    def train(self, train_loader):
        criterion = nn.MSELoss(reduction="mean")
        optimizer = torch.optim.SGD(self.parameters(), lr=0.01, momentum=0.9)
        train_loss = 0.0
        for i, data_batch in enumerate(train_loader, 0):
            inputs, output_ref = data_batch
            optimizer.zero_grad()
            outputs = self.forward(inputs)
            loss = criterion(outputs, output_ref)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(self.parameters(), max_norm=1.0)
            optimizer.step()
            train_loss += loss.item() / len(train_loader)
        return train_loss

    def test(self, test_loader):
        criterion = nn.MSELoss(reduction="mean")
        test_loss = 0.0
        with torch.no_grad():
            for i, data_batch in enumerate(test_loader, 0):
                inputs, output_ref = data_batch
                outputs = self.forward(inputs)
                loss = criterion(outputs, output_ref)
                test_loss += loss.item() / len(test_loader)
        return test_loss
