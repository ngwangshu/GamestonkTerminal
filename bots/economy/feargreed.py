import io
import logging

import matplotlib.pyplot as plt

from bots import config_discordbot as cfg
from bots.helpers import image_border
from gamestonk_terminal.config_plot import PLOT_DPI
from gamestonk_terminal.decorators import log_start_end
from gamestonk_terminal.economy import cnn_model
from gamestonk_terminal.helper_funcs import plot_autoscale

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def feargreed_command(indicator=""):
    """CNN Fear and Greed Index [CNN]"""

    # Debug user input
    if cfg.DEBUG:
        logger.debug("econ-futures")

    # Check for argument
    possible_indicators = ("", "jbd", "mv", "pco", "mm", "sps", "spb", "shd")

    if indicator not in possible_indicators:
        raise Exception(
            f"Select a valid indicator from {', '.join(possible_indicators)}"  # nosec
        )
    # Output data

    fig, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)

    report, im = cnn_model.get_feargreed_report(indicator, fig)
    ax.axes.xaxis.set_visible(False)
    ax.axes.yaxis.set_visible(False)

    if indicator:
        ax.imshow(im)

    imagefile = "feargreed.png"
    dataBytesIO = io.BytesIO()

    plt.savefig(dataBytesIO)
    plt.close("all")

    dataBytesIO.seek(0)
    imagefile = image_border(imagefile, base64=dataBytesIO)

    return {
        "title": "Economy: [CNN] Fear Geed Index",
        "imagefile": imagefile,
        "description": report,
    }
