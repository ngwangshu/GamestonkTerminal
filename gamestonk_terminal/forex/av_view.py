"""AlphaVantage Forex View."""
__docformat__ = "numpy"

import logging

import pandas as pd

from gamestonk_terminal.decorators import check_api_key
from gamestonk_terminal.decorators import log_start_end
from gamestonk_terminal.forex import av_model
from gamestonk_terminal.helper_funcs import print_rich_table
from gamestonk_terminal.rich_config import console

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
@check_api_key(["API_KEY_ALPHAVANTAGE"])
def display_quote(to_symbol: str, from_symbol: str):
    """Display current forex pair exchange rate.

    Parameters
    ----------
    to_symbol : str
        To symbol
    from_symbol : str
        From forex symbol
    """
    quote = av_model.get_quote(to_symbol, from_symbol)

    if not bool(quote) or "Note" in quote:
        if "Note" in quote:
            console.print(quote["Note"])
        console.print(
            "\n[red]"
            + "No historical data loaded.\n"
            + "Make sure 'av' supports the requested pair and you aren't hitting your API call limits."
            + "[/red]\n"
        )
        return

    df = pd.DataFrame.from_dict(quote)
    df.index = df.index.to_series().apply(lambda x: x[3:]).values
    df = df.iloc[[0, 2, 5, 4, 7, 8]]
    print_rich_table(
        df,
        show_index=True,
        title=f"[bold]{from_symbol}/{to_symbol} Quote [/bold]",
    )
    console.print("")
