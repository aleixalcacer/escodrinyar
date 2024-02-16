from dataclasses import dataclass
from typing import ClassVar, Callable

from pandas import DataFrame

from seaborn._core.scales import Scale
from seaborn._core.groupby import GroupBy
from seaborn._stats.base import Stat

from seaborn._core.typing import Vector

@dataclass
class Agg2d(Stat):
    """
    Aggregate data along the values axis using given method.

    Parameters
    ----------
    func : str or callable
        Name of a :class:`pandas.Series` method or a vector -> scalar function.

    See Also
    --------
    objects.Est : Aggregation with error bars.

    Examples
    --------
    .. include:: ../docstrings/objects.Agg.rst

    """
    func: str | Callable[[Vector], float] = "mean"
    group_by_orient: ClassVar[bool] = False

    def __call__(
        self, data: DataFrame, groupby: GroupBy, orient: str, scales: dict[str, Scale],
    ) -> DataFrame:

        agg_dict = {
            "x": self.func,
            "y": self.func,
        }
        res = (
            groupby
            .agg(data, agg_dict)
            .dropna(subset=["x", "y"])
            .reset_index(drop=True)
        )
        return res
