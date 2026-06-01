# fintrack (flat-file)

Flat-file environment — no server, no Docker. The agent reads these files
directly to answer personal-finance questions about accounts, transactions,
budgets, recurring bills, and investment holdings.

## Files

| File                | Description                                              |
|---------------------|----------------------------------------------------------|
| `profile.json`      | Account-holder profile and base currency                 |
| `accounts.csv`      | Bank, credit card, brokerage, and loan accounts          |
| `transactions.csv`  | Last 90 days of transactions across all accounts         |
| `categories.csv`    | Category taxonomy with default budget                    |
| `budgets.csv`       | Per-category monthly budgets and current spend           |
| `recurring.csv`     | Recurring bills + subscriptions                          |
| `holdings.csv`      | Investment holdings (brokerage + retirement)             |

All amounts are in the profile's `base_currency` (`USD`). Negative
transaction amounts are spending; positive are income or transfers in.
