import matplotlib.pyplot as plt
import os
import sys


def render_graph(output_file, dstat_time, cpu_event, mem_event, load_event, show=False):
    """
    This just generates a graph based on dstat info
    :param dstat_time: list of times that the events took place in. Must be same length as cpu_even and mem_event
    :param cpu_event: list of CPU usage events for each second in dstat_time
    :param mem_event: list of memory usage events for each second in dstat_time
    """
    fig, host = plt.subplots()
    mem_plt = host.twinx()
    load_plt = host.twinx()
    fig.subplots_adjust(right=0.75)
    load_plt.spines["right"].set_position(("axes", 1.2))
    load_plt.spines["right"].set_visible(True)
    make_patch_spines_invisible(load_plt)

    # Setting up plot lines
    cpu_ln, = host.plot(dstat_time, cpu_event, "r-", label="CPU Usage / Time")
    mem_ln, = mem_plt.plot(dstat_time, mem_event, "b-", label="Memory Usage / Time")
    load_ln, = mem_plt.plot(
        dstat_time, load_event, "g-", label="System Load (1m) / Time"
    )

    # adding labels
    host.set_ylabel("CPU Usage (%)")
    mem_plt.set_ylabel("Memory Usage (GB)")
    load_plt.set_ylabel("System Load (1m)")
    host.set_xlabel("Time")

    host.yaxis.label.set_color(cpu_ln.get_color())
    mem_plt.yaxis.label.set_color(mem_ln.get_color())
    load_plt.yaxis.label.set_color(load_ln.get_color())

    host.set_ylim(0, 100)
    mem_plt.set_ylim(0, max(mem_event) + 1)

    tkw = dict(size=4, width=1.5)
    host.tick_params(axis='y', colors=cpu_ln.get_color(), **tkw)
    mem_plt.tick_params(axis='y', colors=mem_ln.get_color(), **tkw)
    load_plt.tick_params(axis='y', colors=load_ln.get_color(), **tkw)
    host.tick_params(axis='x', **tkw)

    # setting legend
    lines = [cpu_ln, mem_ln, load_ln]
    host.legend(lines, [x.get_label() for x in lines])

    # saving figure to file
    plt.savefig(output_file)

    # showing plot
    if show:
        plt.show()


def make_patch_spines_invisible(ax):
    ax.set_frame_on(True)
    ax.patch.set_visible(False)
    for sp in ax.spines.values():
        sp.set_visible(False)
