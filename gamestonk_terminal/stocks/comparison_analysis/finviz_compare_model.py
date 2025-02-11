""" Finviz Comparison Model """
__docformat__ = "numpy"

import logging
from typing import List, Tuple

import pandas as pd
from finvizfinance.screener import (
    financial,
    overview,
    ownership,
    performance,
    technical,
    valuation,
)
from finvizfinance.screener.overview import Overview

from gamestonk_terminal.decorators import log_start_end
from gamestonk_terminal.rich_config import console

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def get_similar_companies(
    ticker: str, compare_list: List[str]
) -> Tuple[List[str], str]:
    """Get similar companies from Finviz

    Parameters
    ----------
    ticker : str
        Ticker to find comparisons for
    compare_list : List[str]
        List of fields to compare, ["Sector", "Industry", "Country"]

    Returns
    -------
    List[str]
        List of similar companies
    str
        String containing data source
    """
    try:
        similar = (
            Overview().compare(ticker, compare_list, verbose=0)["Ticker"].to_list()
        )
        user = "Finviz"
    except Exception as e:
        logger.exception(str(e))
        console.print(e)
        similar = [""]
        user = "Error"
    return similar, user


@log_start_end(log=logger)
def get_comparison_data(data_type: str, similar: List[str]):
    """Screener Overview

    Parameters
    ----------
    data_type : str
        Data type between: overview, valuation, financial, ownership, performance, technical

    Returns
    ----------
    pd.DataFrame
        Dataframe with overview, valuation, financial, ownership, performance or technical
    """
    if data_type == "overview":
        screen = overview.Overview()
    elif data_type == "valuation":
        screen = valuation.Valuation()
    elif data_type == "financial":
        screen = financial.Financial()
    elif data_type == "ownership":
        screen = ownership.Ownership()
    elif data_type == "performance":
        screen = performance.Performance()
    elif data_type == "technical":
        screen = technical.Technical()
    else:
        console.print("Invalid selected screener type")
        return pd.DataFrame()

    screen.set_filter(ticker=",".join(similar))
    try:
        return screen.screener_view(verbose=0)
    except IndexError:
        console.print("[red]Invalid data from website[red]")
        return pd.DataFrame()
