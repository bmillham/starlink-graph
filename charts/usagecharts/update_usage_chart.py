from simplehuman import naturalsize

def update_usage_chart(self, chart, rx, tx, title):
    chart.clear()
    chart.set(title=title)

    nprxbar = chart.barh(['Total'], [rx], label='RX', color=['orange'])
    nptxbar = chart.barh(['Total'], [tx], label='TX', left=[rx], color=['purple'])
    tbar = chart.barh(['Total'], [rx + rx], label='RX', color=['orange'])
    self.set_bar_text(chart, nprxbar, f'RX: {naturalsize(rx)} TX: {naturalsize(tx)} Total: {naturalsize(rx+tx)}')
    self.set_bar_text(chart, tbar, f'RX: {naturalsize(rx)} TX: {naturalsize(tx)} Total: {naturalsize(rx+tx)}')
    chart.barh(['Total'], [rx + tx], label='TX', left=[rx], color=['purple'])
    chart.legend(handles=[nprxbar])
    chart.yaxis.set_label_text('Usage')
    chart.yaxis.set_label_position('right')
    chart.xaxis.set_ticks([0, rx + tx], labels=['', naturalsize(rx + tx)])
