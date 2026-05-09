# Stock-Profile-Analyzer

## Overview

This Python script downloads recent S&P 500 stock price data, stores each stock's historical prices in a balanced binary search tree, and allows the user to look up stock trends, individual prices, and date ranges from the command line.

The project demonstrates several core data structures:

- Binary Search Tree (BST): for storing and searching price history by date
- Hash Table: for quickly retrieving stocks by ticker symbol
- Stack: for undoing add, remove, and update operations

## Main Features

- Fetches the current S&P 500 company list from Wikipedia
- Downloads two years of daily adjusted stock prices using `yfinance`
- Builds one `Stock` object per ticker
- Stores each stock's price history in a balanced BST
- Allows lookup of:
  - Two-year percentage trend
  - Price on a specific date
  - Nearest available trading day if the requested date has no data
  - Prices over a date range
- Demonstrates undo functionality using a stack

## Required Libraries

Install the required packages with:

```bash
pip install pandas yfinance requests
```

## How to Run

Save the code in a Python file, for example:

```bash
stock_tracker.py
```

Then run:

```bash
python stock_tracker.py
```

or directly run this notebook in Colab.

The program will:

1. Fetch the S&P 500 company list
2. Download two years of price data
3. Build stock objects and data structures
4. Ask the user to enter a ticker symbol
5. Let the user look up either a single day or a range of dates

## Code Structure

### `Node`

Represents one date-price pair in the binary search tree.

Each node stores:

- `date`
- `price`
- `left` child
- `right` child

### `BST`

Stores price history ordered by date.

Important methods:

| Method | Purpose |
|---|---|
| `insert()` | Inserts one date-price record |
| `build_balanced()` | Builds a balanced BST from sorted records |
| `search()` | Finds an exact date |
| `search_nearest()` | Finds the closest available trading date |
| `range_query()` | Returns all records between two dates |
| `inorder()` | Returns all records in sorted date order |

### `Stock`

Represents a single company and its historical price data.

Each stock stores:

- Company name
- Ticker symbol
- Price history as a BST

Important methods:

| Method | Purpose |
|---|---|
| `buildhistory()` | Builds the stock's price-history BST |
| `getprice()` | Gets nearest price for a date |
| `getprice_with_date()` | Gets nearest date and price |
| `getrange()` | Gets prices over a date range |
| `trend()` | Calculates total percentage change over the stored period |

### `Hash Table`

The script uses a hash table with 509 buckets:

```python
NUM_BUCKETS = 509
stock_table = [[] for _ in range(NUM_BUCKETS)]
```

Ticker symbols are hashed into buckets using:

```python
def hash_function(ticker):
    return hash(ticker) % NUM_BUCKETS
```

This allows stocks to be stored and retrieved by ticker symbol.

Important functions:

| Function | Purpose |
|---|---|
| `add_stock()` | Adds a stock to the hash table |
| `get_stock()` | Retrieves a stock by ticker |
| `update_stock()` | Replaces an existing stock |
| `remove_stock()` | Removes a stock from the table |

### `Stack`

The script uses `action_stack` to support undo operations.

Each add, remove, or update action is pushed onto the stack. The most recent action can be reversed with:

```python
undo_last()
```

Supported undo actions:

| Action | Undo Behavior |
|---|---|
| Add | Removes the added stock |
| Remove | Restores the removed stock |
| Update | Reverts to the previous stock object |

## Runtime Notes

### BST Search

Because each stock's history is built as a balanced BST, searching by date is usually efficient:

- Average case: `O(log n)`
- Worst case: `O(log n)` for the initially balanced tree

If many unsorted inserts were added later without rebalancing, the worst case could degrade to `O(n)`.

### Hash Table Lookup

Hash table lookup is usually fast:

- Average case: `O(1)`
- Worst case: `O(n)` if many tickers collide in the same bucket

### Range Query

A range query takes approximately:

```text
O(log n + k)
```

where `k` is the number of records returned.

### Stack Operations

Pushing and popping actions from the stack are both:

```text
O(1)
```

## Limitations

- The script depends on live internet access.
- Wikipedia and Yahoo Finance data availability may change.
- Python's `hash()` is randomized
- The hash table does not prevent duplicate ticker entries if `add_stock()` is called more than once for the same ticker.
- Date values are stored as strings in the BST, so the code assumes dates are formatted consistently as `YYYY-MM-DD`.

## Possible Improvements

- Prevent duplicate tickers in `add_stock()`
- Add min-heap and max-heap structures to track top and bottom performers
- Separate data downloading from user interaction

## Summary

This project combines real financial data with classic data structures. The BST organizes each stock's historical prices by date, the hash table provides ticker-based lookup, and the stack supports undo behavior for recent modifications.
