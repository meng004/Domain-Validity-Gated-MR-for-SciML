"""Small PyTorch Fourier Neural Operator blocks for the FNO roster pilot."""
from __future__ import annotations

import torch
from torch import nn
import torch.nn.functional as F


class SpectralConv2d(nn.Module):
    def __init__(self, width: int, modes: int) -> None:
        super().__init__()
        self.width = width
        self.modes = modes
        scale = 1.0 / max(1, width * width)
        self.weights = nn.Parameter(scale * torch.randn(width, width, modes, modes, dtype=torch.cfloat))

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        batch, channels, nx, ny = x.shape
        x_ft = torch.fft.rfft2(x, norm="ortho")
        out_ft = torch.zeros(batch, channels, nx, ny // 2 + 1, dtype=torch.cfloat, device=x.device)
        mx = min(self.modes, nx)
        my = min(self.modes, ny // 2 + 1)
        out_ft[:, :, :mx, :my] = torch.einsum(
            "bcxy,cdxy->bdxy",
            x_ft[:, :, :mx, :my],
            self.weights[:, :, :mx, :my],
        )
        return torch.fft.irfft2(out_ft, s=(nx, ny), norm="ortho")


class FNO2D(nn.Module):
    def __init__(
        self,
        in_channels: int,
        out_channels: int,
        width: int = 8,
        modes: int = 6,
        depth: int = 3,
    ) -> None:
        super().__init__()
        self.in_channels = in_channels
        self.out_channels = out_channels
        self.width = width
        self.modes = modes
        self.depth = depth
        self.lift = nn.Conv2d(in_channels, width, kernel_size=1)
        self.spectral = nn.ModuleList([SpectralConv2d(width, modes) for _ in range(depth)])
        self.local = nn.ModuleList([nn.Conv2d(width, width, kernel_size=1) for _ in range(depth)])
        self.proj1 = nn.Conv2d(width, width, kernel_size=1)
        self.proj2 = nn.Conv2d(width, out_channels, kernel_size=1)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        z = self.lift(x)
        for spec, loc in zip(self.spectral, self.local):
            z = F.gelu(spec(z) + loc(z))
        z = F.gelu(self.proj1(z))
        return self.proj2(z)


def parameter_count(model: nn.Module) -> int:
    return sum(p.numel() for p in model.parameters())
