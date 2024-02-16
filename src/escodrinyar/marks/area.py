from __future__ import annotations
from dataclasses import dataclass
from seaborn._marks.area import AreaBase
from seaborn._marks.base import (
    Mark,
    Mappable,
    MappableBool,
    MappableFloat,
    MappableColor,
    document_properties,
)
import scipy


@document_properties
@dataclass
class Polygon(AreaBase, Mark):
    """
    A fill mark representing a polygon.

    Examples
    --------
    .. include:: ../docstrings/objects.Polygon.rst

    """
    color: MappableColor = Mappable("C0", )
    alpha: MappableFloat = Mappable(.2, )
    fill: MappableBool = Mappable(True, )
    edgecolor: MappableColor = Mappable(depend="color", )
    edgealpha: MappableFloat = Mappable(1, )
    edgewidth: MappableFloat = Mappable(0, )
    edgestyle: MappableFloat = Mappable("-", )

    def _get_verts(self, data, orient):
        dv = {"x": "y", "y": "x"}[orient]
        verts = data[[orient, dv]].to_numpy()
        if orient == "y":
            verts = verts[:, ::-1]
        return verts


@document_properties
@dataclass
class ConvexHull(Polygon, Mark):
    """
    A fill mark representing a convex hull around points.

    Examples
    --------
    .. include:: ../docstrings/objects.Hull.rst

    """
    color: MappableColor = Mappable("C0", )
    alpha: MappableFloat = Mappable(.2, )
    fill: MappableBool = Mappable(True, )
    edgecolor: MappableColor = Mappable(depend="color", )
    edgealpha: MappableFloat = Mappable(1, )
    edgewidth: MappableFloat = Mappable(0, )
    edgestyle: MappableFloat = Mappable("-", )

    def _standardize_coordinate_parameters(self, data, orient):
        hull = scipy.spatial.ConvexHull(data[["x", "y"]].to_numpy())
        return data.iloc[hull.vertices]
