# Streamlit Deployment Verification

Verified: 2026-11-09. This is a post-snapshot update; the End of Week 2 Scrum
Board remains unchanged as historical evidence.

## Deployment Source

- GitHub repository: `https://github.com/7wai-chakwai/COMP4145_lab2`
- Branch: `main`
- Commit: `3471d57e693f38533b5dd6a5158247827353a58b`
- Entry point: `app.py`
- Runtime dependencies: `requirements.txt`
- Public URL: `https://comp4145lab2-p38vam3wevyhkpmrafap8u.streamlit.app/`

The existing Community Cloud app was reused. No duplicate app was created and no
application secrets were required.

## Production Smoke Test

The sleeping app was restarted and rebuilt after the GitHub push. The deployed
site loaded without a Streamlit exception. Browser checks confirmed:

- Original MSFT strategy chart, moving averages, buy/sell markers and trade count.
- Multi-Stock Comparison with two charts and the shared `3/20` watchlist.
- Risk Analysis with three metric cards, two charts and persisted stock selection.
- Portfolio Backtesting with five metrics, two charts, two data tables and trade history.
- Manual addition of JPM, changing the shared selection to `4/20`; comparison
  reloaded four price/performance traces without an exception.

The public results remain dependent on Yahoo Finance availability and may change
when adjusted historical prices are revised.
