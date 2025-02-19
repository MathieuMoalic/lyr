import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

from .._utils import hsl2rgb

from ..base import Base


class anim(Base):
    def plot(
        self,
        dset: str = "m",
        f: float = 9,
        z: int = 0,
        periods: int = 1,
        save_path: str = None,
        repeat: int = 1,
        figax=None,
    ):
        arr = self.m.calc.anim(dset, f, periods=periods)[:, z]
        arr = np.tile(arr, (1, repeat, repeat, 1))
        arr = np.ma.masked_equal(arr, 0)
        u, v, w = arr[..., 0], arr[..., 1], arr[..., 2]
        # alphas = np.abs(w)
        # alphas = 1 - self.m.m[0, 0, :, :, 2]
        # alphas = np.ma.masked_equal(alphas, 1)
        # alphas /= alphas.max()
        alphas = np.abs(self.m.get_mode(dset, f)[0, :, :, 0])
        alphas = np.ma.masked_equal(alphas, 0)
        alphas /= alphas.max()
        hsl = np.ones((u.shape[0], u.shape[1], u.shape[2], 3))
        hsl[..., 0] = np.angle(u + 1j * v) / np.pi / 2  # normalization
        hsl[..., 1] = np.sqrt(u**2 + v**2 + w**2)
        hsl[..., 2] = (w + 1) / 2
        rgba = np.ones((u.shape[0], u.shape[1], u.shape[2], 4))
        rgba[..., :3] = hsl2rgb(hsl)
        rgba[..., 3] = alphas
        stepx = max(int(u.shape[2] / 60), 1)
        stepy = max(int(u.shape[1] / 60), 1)
        scale = 1 / max(stepx, stepy)
        x, y = np.meshgrid(
            np.arange(0, u.shape[2], stepx) * self.m.dx * 1e9,
            np.arange(0, u.shape[1], stepy) * self.m.dy * 1e9,
        )
        antidots = np.ma.masked_not_equal(self.m["m"][0, 0, :, :, 2], 0)
        antidots = np.tile(antidots, (repeat, repeat))
        extent = [
            0,
            arr.shape[2] * self.m.dx * 1e9,
            0,
            arr.shape[1] * self.m.dy * 1e9,
        ]
        t = 0
        if figax is None:
            fig = plt.figure(figsize=(5, 5), dpi=150)
            gs = fig.add_gridspec(1, 1)
            ax = fig.add_subplot(gs[:])
            gs.update(left=0, right=1, top=1, bottom=0)
        else:
            fig, ax = figax
        Q = ax.quiver(
            x,
            y,
            u[t, ::stepy, ::stepx],
            v[t, ::stepy, ::stepx],
            w[t, ::stepy, ::stepx],
            alpha=alphas[::stepy, ::stepx],
            angles="xy",
            scale_units="xy",
            scale=scale,
            cmap="binary",
        )
        ax.imshow(
            rgba[t],
            interpolation="None",
            origin="lower",
            cmap="hsv",
            vmin=-np.pi,
            vmax=np.pi,
            extent=extent,
            alpha=alphas,
        )
        ax.imshow(
            antidots, interpolation="None", origin="lower", cmap="Set1_r", extent=extent
        )
        ax.set(xticks=[], yticks=[])

        def run(t):
            ax.get_images()[0].set_data(rgba[t])
            Q.set_UVC(
                u[t, ::stepy, ::stepx], v[t, ::stepy, ::stepx], w[t, ::stepy, ::stepx]
            )
            # Q.set_alpha(alphas[t, ::stepy, ::stepx])

        ani = FuncAnimation(
            fig, run, interval=1, frames=np.arange(1, arr.shape[0], dtype="int")
        )
        # plt.show()
        # return ani
        if save_path is None:
            anim_save_path = f"{self.m.abs_path}_{f}.mp4"
        else:
            anim_save_path = save_path
        ani.save(
            anim_save_path,
            writer="ffmpeg",
            fps=25,
            dpi=150,
            # savefig_kwargs={"transparent": True},
            # extra_args=["-vcodec", "h264", "-pix_fmt", "yuv420p"],
        )
        # print(f"Saved at: {anim_save_path}")
        plt.close()
