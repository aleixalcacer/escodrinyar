import matplotlib.pyplot as plt
import matplotlib as mpl
import io
from .utils import sowraps
from functools import wraps
from seaborn.objects import Plot as SeabornPlot
from seaborn._core.typing import (
    DataSource,
    VariableSpec,
    VariableSpecList,
    OrderSpec,
)
from seaborn._core.scales import Scale
from seaborn.objects import Mark, Stat, Move
from typing import Any, Callable
import base64


class Layout:
    """
    An interface for declaratively specifying the layout for multiple plots.
    """

    def __init__(self, layout):
        self.layout: list[list] = layout
        _ = self.opts()
        self.fig: mpl.figure.Figure | None = None

    def __add__(self, other):
        """
        Add a plot in the same row as the current layout.

        Parameters
        ----------
        other: Plot | Layout
            The plot or layout to add.

        Returns
        -------
        Layout
            The layout with the added plot.

        Examples
        --------
        .. include:: ../docstrings/Layout.__add__.rst

        """
        if isinstance(other, Plot):
            return self + Layout([[other]])
        else:
            return Layout([self.layout[0] + other.layout[0]])

    def __or__(self, other):
        """
        Add a new row to the current layout.

        Parameters
        ----------
        other: Plot | Layout
            The plot or layout to add in the new row.

        Returns
        -------
        Layout
            The layout with the added row.

        Examples
        --------
        .. include:: ../docstrings/Layout.__or__.rst

        """
        if isinstance(other, Plot):
            return self | Layout([[other]])
        else:
            return Layout([*self.layout, *other.layout])

    @sowraps(SeabornPlot.show)
    def show(self, **kwargs):
        if self.fig is None or self.fig.__class__ == mpl.figure.Figure:
            plt.close(self.fig)
            self.plot(pyplot=True)
        plt.show(**kwargs)

    @sowraps(SeabornPlot.save)
    def save(self, loc, **kwargs):
        if self.fig is None:
            _ = self.plot()
        self.fig.savefig(loc, **kwargs)
        # plt.close(fig)

    @sowraps(SeabornPlot.plot)
    def plot(self, pyplot=False):
        if self.fig is not None:
            plt.close(self.fig)

        nrows = len(self.layout)
        ncols = -1
        for row in self.layout:
            if ncols < len(row):
                ncols = len(row)

        # create a gridspec
        if pyplot is False:
            fig = mpl.figure.Figure(constrained_layout=True, figsize=self.figsize)
        else:
            fig = plt.figure(constrained_layout=True, figsize=self.figsize)

        gs = fig.add_gridspec(
            nrows,
            ncols,
            width_ratios=self.width_ratios,
            height_ratios=self.height_ratios,
        )

        for i, row in enumerate(self.layout):
            plot_ncols = ncols // len(row)
            for j, plot in enumerate(row):
                sfig = fig.add_subfigure(
                    gs[i, j * plot_ncols : (j + 1) * plot_ncols]
                )
                with mpl.rc_context(plot.rc_params):
                    plot_j = plot.splot.on(sfig).plot()
                    legend_j = plot_j._legend_contents
                    make_legend(sfig, legend_j)

        fig.legends = []

        self.fig = fig
        return self

    def _repr_png_(self):
        if self.fig is None:
            _ = self.plot()
        buffer = io.BytesIO()
        self.fig.savefig(buffer, format="png")
        buffer.seek(0)
        image = buffer.getvalue()
        buffer.close()
        graphic = base64.b64encode(image).decode("utf-8")
        # plt.close(fig)
        return graphic

    def opts(self, figsize=(5, 5), width_ratios=None, height_ratios=None):
        """
        Set the layout options for the plots.

        Parameters
        ----------
        figsize: tuple
            The size of the figure. Default is (5, 5).
        width_ratios: list
            The relative widths of the columns. Default is None.
        height_ratios:
            The relative heights of the rows. Default is None.

        Returns
        -------
        Layout
            The layout with the specified options.
        """
        self.figsize = figsize
        self.width_ratios = width_ratios
        self.height_ratios = height_ratios

        return self


class Plot:
    """
    An interface for declaratively specifying statistical graphics.
    """

    def __init__(
        self,
        splot: SeabornPlot = None,
        *args,
        data: DataSource = None,
        **variables: VariableSpec,
    ):
        if splot is None:
            splot = SeabornPlot(*args, data=data, **variables)
        self.splot = splot
        self.rc_params = {}

    def __add__(self, other):
        if isinstance(other, Plot):
            return Layout([[self]]) + Layout([[other]])
        else:
            return Layout([[self]]) + other

    def __or__(self, other):
        if isinstance(other, Plot):
            return Layout([[self]]) | Layout([[other]])
        else:
            return Layout([[self]]) | other

    def __mul__(self, other):
        if isinstance(other, Plot):
            # TODO: check that the plots have the same data and variables
            splot = self.splot._clone()
            splot._layers.extend(other.splot._layers)
            self.rc_params = {**self.rc_params, **other.rc_params}
            plot = Plot(splot.theme(self.rc_params))
            plot.rc_params = self.rc_params
            return plot
        else:
            raise ValueError("Can only multiply Plot by Plot")

    def _repr_png_(self):
        return Layout([[self]])._repr_png_()

    @sowraps(SeabornPlot.add)
    def add(
        self,
        mark: Mark,
        *transforms: Stat | Move,
        orient: str | None = None,
        legend: bool = True,
        label: str | None = None,
        data: DataSource = None,
        **variables: VariableSpec,
    ):
        plot = Plot(
            self.splot.add(
                mark,
                *transforms,
                orient=orient,
                legend=legend,
                label=label,
                data=data,
                **variables,
            )
        )
        plot.rc_params = self.rc_params
        return plot

    @sowraps(SeabornPlot.scale)
    def scale(self, **scales: Scale):
        plot = Plot(self.splot.scale(**scales))
        plot.rc_params = self.rc_params
        return plot

    @sowraps(SeabornPlot.theme)
    def theme(self, config: dict[str, Any]):
        plot = Plot(self.splot.theme(self.rc_params))
        plot.rc_params = {**self.rc_params, **config}
        return plot

    @sowraps(SeabornPlot.facet)
    def facet(
        self,
        col: VariableSpec = None,
        row: VariableSpec = None,
        order: OrderSpec | dict[str, OrderSpec] = None,
        wrap: int | None = None,
    ):
        plot = Plot(self.splot.facet(col, row, order, wrap))
        plot.rc_params = self.rc_params
        return plot

    @sowraps(SeabornPlot.pair)
    def pair(
        self,
        x: VariableSpecList = None,
        y: VariableSpecList = None,
        wrap: int | None = None,
        cross: bool = True,
    ):
        plot = Plot(self.splot.pair(x, y, wrap, cross))
        plot.rc_params = self.rc_params
        return plot

    @sowraps(SeabornPlot.label)
    def label(
        self,
        *,
        title: str | None = None,
        legend: str | None = None,
        **variables: str | Callable[[str], str],
    ):
        plot = Plot(self.splot.label(title=title, legend=legend, **variables))
        plot.rc_params = self.rc_params
        return plot

    @sowraps(SeabornPlot.plot)
    def plot(self, pyplot=False):
        return Layout([[self]]).plot(pyplot=pyplot)

    @sowraps(SeabornPlot.show)
    def show(self):
        return Layout([[self]]).show()

    @sowraps(SeabornPlot.save)
    def save(self, loc, **kwargs):
        return Layout([[self]]).save(loc, **kwargs)

    @wraps(Layout.opts)
    def opts(self, figsize=(5, 5), width_ratios=None, height_ratios=None):
        return Layout([[self]]).opts(figsize, width_ratios, height_ratios)


def make_legend(sfig, legend_contents):
    merged_contents = {}
    for key, new_artists, labels in legend_contents:
        # Key is (name, id); we need the id to resolve variable uniqueness,
        # but will need the name in the next step to title the legend
        if key not in merged_contents:
            # Matplotlib accepts a tuple of artists and will overlay them
            new_artist_tuples = [tuple([a]) for a in new_artists]
            merged_contents[key] = new_artist_tuples, labels
        else:
            existing_artists = merged_contents[key][0]
            for i, new_artist in enumerate(new_artists):
                existing_artists[i] += tuple([new_artist])

    # When using pyplot, an "external" legend won't be shown, so this
    # keeps it inside the axes (though still attached to the figure)
    # This is necessary because matplotlib layout engines currently don't
    # support figure legends — ideally this will change.

    # get last axes
    ax = sfig.get_axes()[-1]

    base_legend = None
    for (name, _), (handles, labels) in merged_contents.items():
        legend = mpl.legend.Legend(
            ax,
            handles,  # type: ignore  # matplotlib/issues/26639
            labels,
            title=name,
        )

        if base_legend:
            # Matplotlib has no public API for this, so it is a bit of a hack.
            # Ideally we'd define our own legend class with more flexibility,
            # but that is a lot of work!
            base_legend_box = base_legend.get_children()[0]
            this_legend_box = legend.get_children()[0]
            base_legend_box.get_children().extend(this_legend_box.get_children())
        else:
            base_legend = legend
            sfig.legends.append(legend)
