import torch
from torch.nn.functional import normalize


class ZScoreNormalize(object):
    def __call__(self, tensor):
        # Calculate the mean and standard deviation of the tensor
        mean = torch.mean(tensor)
        std = torch.std(tensor)

        # Normalize the tensor by subtracting the mean and dividing by the standard deviation
        normalized_tensor = (tensor - mean) / std

        return normalized_tensor


class L2Normalize(object):
    def __call__(self, tensor):
        # Normalize the tensor using L2 normalization
        normalized_tensor = normalize(tensor, p=2, dim=None)

        return normalized_tensor
