import matplotlib.pyplot as plt
import io
import base64
from seaborn.objects import Plot as SeabornPlot
from seaborn._core.typing import (
    DataSource,
    VariableSpec,
    VariableSpecList,
    OrderSpec,
    Default,
)
from seaborn.objects import Mark, Stat, Move
import matplotlib.gridspec as gridspec


class Layout:
    def __init__(self, layout):
        self.layout: list[list] = layout
        _ = self.opts()

    def __add__(self, other):
        # print other class
        if isinstance(other, Plot):
            return self + Layout([[other]])
        else:
            return Layout([self.layout[0] + other.layout[0]])

    def __or__(self, other):
        if isinstance(other, Plot):
            return self | Layout([[other]])
        else:
            return Layout([*self.layout, *other.layout])

    def _repr_png_(self):

        nrows = len(self.layout)
        ncols = -1
        for row in self.layout:
            if ncols < len(row):
                ncols = len(row)

        # create a gridspec
        fig = plt.figure(constrained_layout=True, figsize=self.figsize)
        gs = fig.add_gridspec(nrows, ncols)

        for i, row in enumerate(self.layout):
            plot_ncols = ncols // len(row)
            for j, plot in enumerate(row):
                sfig = fig.add_subfigure(gs[i, j * plot_ncols:(j + 1) * plot_ncols])
                ax = sfig.add_subplot(111)

                l = plot.splot.on(ax).plot()
                legend = l._legend_contents

                sfig.legends = []

        fig.legends = []

        # fig.tight_layout()

        buffer = io.BytesIO()
        fig.savefig(buffer, format='png')
        buffer.seek(0)
        image_png = buffer.getvalue()
        buffer.close()
        graphic = base64.b64encode(image_png)
        graphic = graphic.decode('utf-8')
        plt.close(fig)

        return graphic

    def opts(self, ncols=-1, figsize=(5, 5)):
        self.ncols = ncols
        self.figsize = figsize

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

    def __add__(self, other):
        if isinstance(other, Plot):
            return Layout([[self]]) + Layout([[other]])
        else:
            return Layout([[self]]) + other

    def __mul__(self, other):
        if isinstance(other, Plot):
            # TODO: check that the plots have the same data and variables
            splot = self.splot._clone()
            splot._layers.extend(other.splot._layers)
            return Plot(splot)
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
        return Plot(self.splot.add(mark, *transforms, orient=orient, legend=legend, label=label, data=data, **variables))
