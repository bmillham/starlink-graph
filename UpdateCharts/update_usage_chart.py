from SimpleHuman import naturalsize

def update_usage_chart(self, chart, nrx, ntx, prx, ptx, title):
    chart.clear()
    chart.set(title=title)

    nprxbar = chart.barh(['Non\nPrime'], [nrx], label='RX', color=['orange'])
    nptxbar = chart.barh(['Non\nPrime'], [ntx], label='TX', left=[nrx], color=['purple'])
    rxbar = chart.barh(['Prime'], [prx], label='RX', color=['orange'])
    txbar = chart.barh(['Prime'], [ptx], label='TX', left=[prx], color=['purple'])
    tbar = chart.barh(['Total'], [prx + nrx], label='RX', color=['orange'])
    self.set_bar_text(chart, rxbar, f'RX: {naturalsize(prx)} TX: {naturalsize(ptx)} Total: {naturalsize(prx+ptx)}')
    self.set_bar_text(chart, nprxbar, f'RX: {naturalsize(nrx)} TX: {naturalsize(ntx)} Total: {naturalsize(nrx+ntx)}')
    self.set_bar_text(chart, tbar, f'RX: {naturalsize(nrx+prx)} TX: {naturalsize(ntx+ptx)} Total: {naturalsize(prx+ptx+nrx+ntx)}')
    chart.barh(['Total'], [ptx + ntx], label='TX', left=[prx + nrx], color=['purple'])
    chart.legend(handles=[rxbar, txbar])
    chart.yaxis.set_label_text('Usage')
    chart.yaxis.set_label_position('right')
    chart.xaxis.set_ticks([0, prx + ptx + nrx + ntx], labels=['', naturalsize(prx + ptx + nrx + ntx)])
