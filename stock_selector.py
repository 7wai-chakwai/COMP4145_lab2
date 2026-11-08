import streamlit as st

from market_data import MAX_SELECTED_STOCKS, normalize_tickers


SUGGESTED_US_TICKERS = (
    "AAPL", "MSFT", "NVDA", "TSLA", "AMZN", "GOOGL", "META", "JPM", "KO", "DIS",
)
DEFAULT_SELECTED_TICKERS = ("AAPL", "MSFT", "NVDA")
SHARED_SELECTION_KEY = "shared_us_stock_watchlist"
PERFORMANCE_WARNING_THRESHOLD = 10


def _set_shared_selection(symbols):
    st.session_state[SHARED_SELECTION_KEY] = list(normalize_tickers(symbols))


def _normalize_shared_selection():
    _set_shared_selection(st.session_state.get(SHARED_SELECTION_KEY, ()))


def current_stock_selection():
    return normalize_tickers(st.session_state.get(SHARED_SELECTION_KEY, DEFAULT_SELECTED_TICKERS))


def render_stock_selector():
    if SHARED_SELECTION_KEY not in st.session_state:
        st.session_state[SHARED_SELECTION_KEY] = list(DEFAULT_SELECTED_TICKERS)

    with st.sidebar:
        st.subheader("US stock watchlist")
        st.multiselect(
            "Selected US stocks",
            options=list(SUGGESTED_US_TICKERS),
            accept_new_options=True,
            key=SHARED_SELECTION_KEY,
            on_change=_normalize_shared_selection,
            help=(
                "Suggestions are examples only. Type a US-listed stock symbol and press Enter to add it. "
                "Remove a chip to remove a stock."
            ),
        )
        left, right = st.columns(2)
        left.button(
            "Clear selection",
            key="clear_shared_stock_selection",
            on_click=_set_shared_selection,
            args=((),),
            width="stretch",
        )
        right.button(
            "Restore defaults",
            key="restore_shared_stock_selection",
            on_click=_set_shared_selection,
            args=(DEFAULT_SELECTED_TICKERS,),
            width="stretch",
        )
        selected = current_stock_selection()
        if selected:
            st.caption(f"Selected ({len(selected)}/{MAX_SELECTED_STOCKS}): {', '.join(selected)}")
        else:
            st.caption(f"Selected (0/{MAX_SELECTED_STOCKS}): none")
        if len(selected) > PERFORMANCE_WARNING_THRESHOLD:
            st.warning(
                f"Loading {len(selected)} stocks can be slower and may trigger Yahoo Finance rate limits. "
                "Results are cached for one hour."
            )
    return current_stock_selection()
