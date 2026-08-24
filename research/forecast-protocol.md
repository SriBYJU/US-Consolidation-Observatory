# Immutable Forecast Protocol

The Observatory will not retroactively edit a forecast after outcomes are known.

Before the first public consolidation forecast:

1. Freeze the transaction-corpus version and checksum.
2. Freeze feature definitions and source vintages.
3. Freeze train, validation, and test/forecast dates.
4. Freeze model code at a Git commit SHA.
5. Generate forecast rows containing `forecast_id`, `issued_at_utc`, market key, horizon, probability/rank, model version, data-vintage hash, and commit SHA.
6. Append those rows to the public ledger.
7. Never mutate an issued entry; corrections are appended as new records with a reason.
8. When outcomes mature, score the frozen forecast using predeclared metrics.

`data/forecast_ledger.json` intentionally contains no forecast entries in v0.1 because the verified transaction-outcome milestone has not yet been met.
