"""Tests for the initial MOSAIC environment."""

import torch


def test_torch_matrix_multiplication() -> None:
    """PyTorch should perform basic matrix multiplication correctly."""
    matrix_a = torch.tensor([[1.0, 2.0]])
    matrix_b = torch.tensor([[3.0], [4.0]])

    result = matrix_a @ matrix_b

    assert result.shape == (1, 1)
    assert result.item() == 11.0