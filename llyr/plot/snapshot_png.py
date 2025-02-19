import matplotlib.pyplot as plt
import numpy as np

from ..base import Base


class snapshot_png(Base):
    def plot(self, image: str):
        arr = self.m[f"snapshots/{image}"][:]
        arr = np.flip(arr, axis=0)
        fig, ax = plt.subplots(1, 1, figsize=(6, 6))
        if "dy" in self.m.attrs:
            extent = [
                0,
                arr.shape[1] * self.m.dy * 1e9,
                0,
                arr.shape[0] * self.m.dx * 1e9,
            ]
        else:
            extent = None
        ax.imshow(arr, origin="lower", extent=extent)
        ax.set_ylabel(r"$y$ (nm)")
        ax.set_xlabel(r"$x$ (nm)")
        fig.tight_layout()
        return self
