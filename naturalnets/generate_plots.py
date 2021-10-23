import logging
import os

import matplotlib.pyplot as plt

from tools.parse_experiments import read_simulations, parse_log

logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.INFO)

simulations_directory = "Simulation_Results"
save_svg: str = "plot.svg"  # A filename where the plot should be saved as png
style: str = "seaborn-paper"  # Which plot style should be used?
recreate_all_plots: bool = False


def plot_chapter(axis, parsed_log):
    colors = ("green", "teal", "teal", 'blue')

    generations = parsed_log["generations"]
    mean = parsed_log["mean"]
    maximum = parsed_log["maximum"]
    best = parsed_log["best"]

    axis.plot(generations, maximum, "-", color=colors[0], label="maximum")
    axis.plot(generations, mean, "-", color=colors[1], label="average")
    axis.plot(generations, best, "-", color=colors[3], label="best")


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

    try:
        params_display = config["environment"]["type"] + "\n" + config["brain"]["type"] + " + " + config["optimizer"][
            "type"].replace('_', ' ')
        if config["brain"]["type"] == "CTRNN":
            params_display += "\nCTRNN neurons: " + str(config["brain"]["number_neurons"])
    except KeyError:
        params_display = os.path.basename(simulation_dir).replace('_', ' ')

    fig, ax1 = plt.subplots()
    plt.style.use(style)

    plot_chapter(ax1, log)

    ax1.set_xlabel("Generations")
    ax1.set_ylabel("Fitness")
    ax1.legend(loc="upper left")
    ax1.grid()
    plt.title(os.path.basename(simulation_dir).replace("_", " "))
    ax1.text(0.96, 0.05, params_display, ha="right",
             fontsize=8, fontname="Ubuntu", transform=ax1.transAxes,
             bbox={"facecolor": "white", "alpha": 0.4, "pad": 8})

    if save_svg:
        plot_file_name = os.path.join(simulations_directory, simulation_dir, save_svg)
        logging.info("Saving plot to: {}".format(plot_file_name))
        plt.savefig(plot_file_name)

    # Avoid memory build up
    plt.close()
