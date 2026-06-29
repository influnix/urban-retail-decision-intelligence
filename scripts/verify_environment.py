"""Verify the local Python and PyTorch environment."""

from __future__ import annotations

import platform
import sys

import numpy as np
import pandas as pd
import sklearn
import torch


def main() -> None:
    """Print package versions and run a minimal tensor calculation."""
    matrix_a = torch.tensor([[1.0, 2.0]])
    matrix_b = torch.tensor([[3.0], [4.0]])
    result = matrix_a @ matrix_b

    print("=" * 50)
    print("MOSAIC environment verification")
    print("=" * 50)
    print(f"Operating system : {platform.platform()}")
    print(f"Python executable: {sys.executable}")
    print(f"Python version   : {sys.version.split()[0]}")
    print(f"NumPy version    : {np.__version__}")
    print(f"pandas version   : {pd.__version__}")
    print(f"scikit-learn     : {sklearn.__version__}")
    print(f"PyTorch version  : {torch.__version__}")
    print(f"CUDA available   : {torch.cuda.is_available()}")
    print(f"Tensor result    : {result.item()}")
    print("=" * 50)

    expected_result = 11.0
    if result.item() != expected_result:
        raise RuntimeError(
            f"Tensor verification failed: "
            f"expected {expected_result}, received {result.item()}."
        )

    print("Environment verification passed.")


if __name__ == "__main__":
    main()