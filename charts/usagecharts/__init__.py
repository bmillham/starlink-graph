from matplotlib.figure import Figure
from matplotlib.backends.backend_gtk3agg import (FigureCanvasGTK3Agg as FigureCanvas)


class UsageCharts(object):
    from .do_daily_chart import do_daily_chart
    from .do_today_chart import do_today_chart
    from .update_usage_chart import update_usage_chart

    def __init__(self, widgets=None, db=None):
        self.day_last_update = -1
        self.today_last_update = -1
        self._db = db
        self.last_date = None
        self._widgets=widgets

        # The today tab
        self.today_usage_fig = Figure(layout='constrained')
        self.today_usage_ax = self.today_usage_fig.add_subplot()
        self.today_usage_canvas = FigureCanvas(self.today_usage_fig)
        self.today_usage_ax.set_title('Please wait, gathering data...')
        self.today_fig = Figure(layout='constrained')
        self.today_ax = self.today_fig.add_subplot()
        self.today_canvas = FigureCanvas(self.today_fig)
        self.today_ax.set_title('Please wait, gathering data...')

        self._widgets['today_usage_box2'].pack_start(self.today_usage_canvas, True, True, 0)
        self._widgets['today_usage_box1'].pack_start(self.today_canvas, True, True, 0)

        # The daily tab
        self.day_fig = Figure()
        self.day_ax = self.day_fig.add_subplot()
        self.day_canvas = FigureCanvas(self.day_fig)
        self._widgets['dailybox'].pack_start(self.day_canvas, True, True, 0)



    def set_bar_text(self, chart, bar, text):
        for idx, rect in enumerate(bar):
            height = rect.get_height()
            width = rect.get_width()
            chart.text(rect.get_y(), rect.get_y() + height*0.5,
                    f" {text}",
                    ha='left', va='center')
