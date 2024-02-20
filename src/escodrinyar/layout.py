import matplotlib.pyplot as plt
import matplotlib as mpl
import io

from seaborn.objects import Plot as SeabornPlot
from seaborn._core.typing import (
    DataSource,
    VariableSpec,
    VariableSpecList,
    OrderSpec,
)
from seaborn.objects import Mark, Stat, Move
from typing import Any, Callable
import base64

import seaborn as sns

class Layout:
    def __init__(self, layout):
        self.layout: list[list] = layout
        _ = self.opts()

    def __add__(self, other):
        if isinstance(other, Plot):
            return self + Layout([[other]])
        else:
            return Layout([self.layout[0] + other.layout[0]])

    def __or__(self, other):
        if isinstance(other, Plot):
            return self | Layout([[other]])
        else:
            return Layout([*self.layout, *other.layout])

    def show(self):
        fig = self.plot()
        plt.show(fig)

    def save(self, loc, **kwargs):
        fig = self.plot()
        fig.savefig(loc, **kwargs)

    def plot(self):
        nrows = len(self.layout)
        ncols = -1
        for row in self.layout:
            if ncols < len(row):
                ncols = len(row)

        # create a gridspec
        with plt.ioff():
            fig = plt.figure(constrained_layout=True, figsize=self.figsize)


            gs = fig.add_gridspec(
                nrows,
                ncols,
                width_ratios=self.width_ratios,
                height_ratios=self.height_ratios
            )

            for i, row in enumerate(self.layout):
                plot_ncols = ncols // len(row)
                for j, plot in enumerate(row):
                    sfig = fig.add_subfigure(gs[i, j * plot_ncols:(j + 1) * plot_ncols])
                    with mpl.rc_context(plot.rc_params):
                        l = plot.splot.on(sfig).plot()
                        make_legend(sfig, l._legend_contents)


            fig.legends = []

            return fig

    def _repr_png_(self):
        fig = self.plot()
        buffer = io.BytesIO()
        fig.savefig(buffer, format="png")
        buffer.seek(0)
        image = buffer.getvalue()
        buffer.close()
        graphic = base64.b64encode(image).decode('utf-8')
        plt.close(fig)
        return graphic

    def opts(self, figsize=(5, 5), width_ratios=None, height_ratios=None):
        self.figsize = figsize
        self.width_ratios = width_ratios
        self.height_ratios = height_ratios

        return self



class Plot():
    def __init__(self,
                 splot: SeabornPlot = None,
                 *args,
                 data: DataSource = None,
                 **variables: VariableSpec):
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
        plot = Plot(self.splot.add(mark, *transforms, orient=orient, legend=legend, label=label, data=data, **variables))
        plot.rc_params = self.rc_params
        return plot

    def theme(
            self,
            config: dict[str, Any]
    ):
        plot = Plot(self.splot.theme(self.rc_params))
        plot.rc_params = {**self.rc_params, **config}
        return plot

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

    def label(self, *,
        title: str | None = None,
        legend: str | None = None,
        **variables: str | Callable[[str], str]):
        plot = Plot(self.splot.label(title=title, legend=legend, **variables))
        plot.rc_params = self.rc_params
        return plot


    # Layout methods for Plot
    def plot(self):
        return Layout([[self]]).plot()

    def show(self):
        return Layout([[self]]).show()

    def save(self, loc, **kwargs):
        return Layout([[self]]).save(loc, **kwargs)

    def opts(self, figsize=(5, 5)):
        return Layout([[self]]).opts(figsize)


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
            title=name
        )

        if base_legend:
            # Matplotlib has no public API for this so it is a bit of a hack.
            # Ideally we'd define our own legend class with more flexibility,
            # but that is a lot of work!
            base_legend_box = base_legend.get_children()[0]
            this_legend_box = legend.get_children()[0]
            base_legend_box.get_children().extend(this_legend_box.get_children())
        else:
            base_legend = legend
            sfig.legends.append(legend)
