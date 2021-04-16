import pickle
import os
import json
import matplotlib.pyplot as plt
from operator import add, sub
from scipy.ndimage.filters import gaussian_filter1d
import logging
import numpy as np
import matplotlib
# matplotlib.use('Agg')
import tikzplotlib
from tools.parse_experiments import read_simulations, parse_log

logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.INFO)

simulations_directory = "Simulation_Results"
no_show: bool = True  # Open a matplotlib window to show the plot
save_svg: str = "plot.svg"  # A filename where the plot should be saved as png
# smooth: int = 0  # How strong should the lines be smoothed? (0 to disable)
style: str = "seaborn-paper"  # Which plot style should be used?
recreate_all_plots: bool = True


def plot_chapter(axis, parsed_log, colors):
    generations = parsed_log["generations"]
    mean = parsed_log["mean"]
    maximum = parsed_log["maximum"]
    best = parsed_log["best"]

    # fit_min, fit_avg, fit_max, fit_std = chapter.select('min', 'avg', 'max', 'std')

    # std_low = list(map(add, fit_avg, np.array(fit_std) / 2))
    # std_high = list(map(sub, fit_avg, np.array(fit_std) / 2))

    axis.plot(generations, maximum, '-', color=colors[0], label="maximum")
    axis.plot(generations, mean, '-', color=colors[1], label="average")
    # axis.fill_between(generations, std_low, std_high, facecolor=colors[2], alpha=0.15,
                      # label='variance')
    axis.plot(generations, best, '-', color=colors[3], label="best")


all_simulations = read_simulations(simulations_directory)

for simulation in all_simulations:
    plot = simulation["plot"]
    simulation_dir = simulation["dir"]

    if plot is not None and not recreate_all_plots:
        continue

    log = parse_log(simulation["log"])

    if log is None:
        continue

    config = simulation["conf"]

    # if conf['brain']['type'] == 'CNN_CTRNN':
    #     nn = conf['brain']['ctrnn_conf']['number_neurons']
    # else:
    #     nn = conf['brain']['number_neurons']
    #

    try:
        params_display = config["environment"]["type"] + "\n" + config["brain"]["type"] + " + " + config["optimizer"][
            "type"].replace('_', ' ')
        if config["brain"]["type"] == "CTRNN":
            params_display += "\nCTRNN neurons: " + str(config["brain"]["number_neurons"])
    except KeyError:
        params_display = os.path.basename(simulation_dir).replace('_', ' ')

    fig, ax1 = plt.subplots()
    plt.style.use(style)

    # plot_chapter(ax1, log.chapters["fitness"], generations, ("green", "teal", "teal", 'blue'))
    plot_chapter(ax1, log, ("green", "teal", "teal", 'blue'))

    ax1.set_xlabel('Generations')
    ax1.set_ylabel('Fitness')
    ax1.legend(loc='upper left')
    ax1.grid()
    plt.title(os.path.basename(simulation_dir).replace('_', ' '))
    ax1.text(0.96, 0.05, params_display, ha='right',
             fontsize=8, fontname='Ubuntu', transform=ax1.transAxes,
             bbox={'facecolor': 'white', 'alpha': 0.4, 'pad': 8})

    # if args.plot_novelty:
    #     # quickfix because first value is bugged
    #     log.chapters["novelty"][0]["min"] = log.chapters["novelty"][1]["min"]
    #     log.chapters["novelty"][0]["avg"] = log.chapters["novelty"][1]["avg"]
    #     log.chapters["novelty"][0]["max"] = log.chapters["novelty"][1]["max"]
    #     log.chapters["novelty"][0]["std"] = log.chapters["novelty"][1]["std"]
    #
    #     ax2 = plt.twinx()
    #     ax2.set_ylabel('Novelty')
    #     plot_chapter(ax2, log.chapters["novelty"], generations, ("yellow", "orange", "orange", 'pink'))
    #     ax2.legend(loc='lower left')

    if save_svg:
        plot_file_name = os.path.join(simulations_directory, simulation_dir, save_svg)
        logging.info("Saving plot to: {}".format(plot_file_name))
        plt.savefig(plot_file_name)

    # Avoid memory build up
    plt.close()

    # if args.save_tikz:
    #     tikzplotlib.clean_figure(target_resolution=80)
    #     tikzplotlib.save(filepath=args.save_tikz, strict=True, axis_height='8cm',
    #                      axis_width='10cm')
    if not no_show:
        plt.show()
