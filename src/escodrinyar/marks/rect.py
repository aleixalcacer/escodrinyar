from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from seaborn._marks.base import (
    Mark,
    Mappable,
    MappableBool,
    MappableFloat,
    MappableColor,
    document_properties,
    resolve_properties,
    resolve_color,
)
import numpy as np
import matplotlib as mpl


class RectBase:
    def _plot(self, split_gen, scales, orient):

        patches = defaultdict(list)

        for keys, data, ax in split_gen():

            kws = {}
            resolved = resolve_properties(self, keys, scales)
            data = self._standardize_coordinate_parameters(data, resolved, orient)
            verts = self._get_verts(data, orient)

            xmin = verts[:, 0].min()
            xmax = verts[:, 1].max()
            ymin = verts[:, 2].min()
            ymax = verts[:, 3].max()

            ax.update_datalim(
                [[xmin, ymin], [xmax, ymax]]
            )

            # TODO should really move this logic into resolve_color
            fc = resolve_color(self, keys, "", scales)
            if not resolved["fill"]:
                fc = mpl.colors.to_rgba(fc, 0)

            kws["facecolor"] = fc
            kws["edgecolor"] = resolve_color(self, keys, "edge", scales)
            kws["linewidth"] = resolved["edgewidth"]
            kws["linestyle"] = resolved["edgestyle"]

            for xmin, xmax, ymin, ymax in verts:
                verts_i = [
                    [xmin, ymin],
                    [xmin, ymax],
                    [xmax, ymax],
                    [xmax, ymin],
                ]
                patches[ax].append(mpl.patches.Polygon(verts_i, **kws))

        for ax, ax_patches in patches.items():

            for patch in ax_patches:
                self._postprocess_artist(patch, ax, orient)
                ax.add_patch(patch)

    def _standardize_coordinate_parameters(self, data, resolved, orient):
        return data

    def _postprocess_artist(self, artist, ax, orient):
        pass

    def _get_verts(self, data, orient):

        dv = {"x": "y", "y": "x"}[orient]

        verts = data[[f"{dv}min", f"{dv}max", f"{orient}min", f"{orient}max"]].to_numpy()

        return verts

    def _legend_artist(self, variables, value, scales):

        keys = {v: value for v in variables}
        resolved = resolve_properties(self, keys, scales)

        fc = resolve_color(self, keys, "", scales)
        if not resolved["fill"]:
            fc = mpl.colors.to_rgba(fc, 0)

        return mpl.patches.Patch(
            facecolor=fc,
            edgecolor=resolve_color(self, keys, "edge", scales),
            linewidth=resolved["edgewidth"],
            linestyle=resolved["edgestyle"],
            **self.artist_kws,
        )


@document_properties
@dataclass
class Rect(RectBase, Mark):
    """
    A fill mark representing a rectangle.

    Examples
    --------
    .. include:: ../docstrings/objects.Rectangle.rst

    """
    color: MappableColor = Mappable("C0", )
    alpha: MappableFloat = Mappable(.2, )
    fill: MappableBool = Mappable(True, )
    edgecolor: MappableColor = Mappable(depend="color", )
    edgealpha: MappableFloat = Mappable(1, )
    edgewidth: MappableFloat = Mappable(0, )
    edgestyle: MappableFloat = Mappable("-", )


@document_properties
@dataclass
class Tile(RectBase, Mark):
    """
    A fill mark representing a tile.

    Examples
    --------
    .. include:: ../docstrings/objects.Tile.rst

    """
    color: MappableColor = Mappable("C0", )
    alpha: MappableFloat = Mappable(1, )
    fill: MappableBool = Mappable(True, )
    edgecolor: MappableColor = Mappable(depend="color", )
    edgealpha: MappableFloat = Mappable(1, )
    edgewidth: MappableFloat = Mappable(0, )
    edgestyle: MappableFloat = Mappable("-", )
    tilewidth: MappableFloat = Mappable(1, )  # width noun is already taken
    tileheight: MappableFloat = Mappable(1, )

    def _standardize_coordinate_parameters(self, data, resolved, orient):
        # create xmin, xmax, ymin, ymax columns
        data = data.copy()
        var = {"x": "y", "y": "x"}[orient]
        data["xmin"] = data[var] - resolved["tileheight"] / 2
        data["xmax"] = data[var] + resolved["tileheight"] / 2
        data["ymin"] = data[orient] - resolved["tilewidth"] / 2
        data["ymax"] = data[orient] + resolved["tilewidth"] / 2

        return data


    def _legend_artist(self, variables, value, scales):

        keys = {v: value for v in variables}
        resolved = resolve_properties(self, keys, scales)

        fc = resolve_color(self, keys, "", scales)
        if not resolved["fill"]:
            fc = mpl.colors.to_rgba(fc, 0)

        return mpl.patches.Patch(
            facecolor=fc,
            edgecolor=resolve_color(self, keys, "edge", scales),
            linewidth=resolved["edgewidth"],
            linestyle=resolved["edgestyle"],
            **self.artist_kws,
        )