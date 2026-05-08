import pandas as pd
import yfinance as yf
import requests

from io import StringIO

class Node:
    def __init__(self, date, price):
        self.date = date
        self.price = price
        self.left = None
        self.right = None

class BST:
    def __init__(self):
        self.root = None

    def insert(self, date, price):
        self.root = self.insert_node(self.root, date, price)

    def insert_node(self, node, date, price):
        if node == None:
            return Node(date, price)
        if date < node.date:
            node.left = self.insert_node(node.left, date, price)
        elif date > node.date:
            node.right = self.insert_node(node.right, date, price)
        else:
            node.price = price
        return node

    def build_balanced(self, records):
        self.root = self._build_balanced(records, 0, len(records) - 1)

    def _build_balanced(self, records, left, right):
        if left > right:
            return None
        mid = (left + right) // 2
        date, price = records[mid]
        node = Node(date, price)
        node.left = self._build_balanced(records, left, mid - 1)
        node.right = self._build_balanced(records, mid + 1, right)
        return node

    def search(self, date):
        return self._search(self.root, date)

    def _search(self, node, date):
        if node == None or node.date == date:
            return node
        if date < node.date:
            return self._search(node.left, date)
        return self._search(node.right, date)

    def search_nearest(self, date):
        target = pd.Timestamp(date)
        node = self.root
        closest = None
        while node:
            if self._is_closer(node, closest, target):
                closest = node

            if date == node.date:
                return node
            if date < node.date:
                node = node.left
            else:
                node = node.right
        return closest

    def _is_closer(self, candidate, current_best, target):
        if current_best is None:
            return True

        candidate_diff = abs((pd.Timestamp(candidate.date) - target).days)
        current_diff = abs((pd.Timestamp(current_best.date) - target).days)

        if candidate_diff != current_diff:
            return candidate_diff < current_diff
        return candidate.date < current_best.date

    def inorder(self):
        result = []
        self.inorder_helper(self.root, result)
        return result

    def inorder_helper(self, node, result):
        if node:
            self.inorder_helper(node.left, result)
            result.append((node.date, node.price))
            self.inorder_helper(node.right, result)

    def range_query(self, start_date, end_date):
        result = []
        self.range_query_helper(self.root, start_date, end_date, result)
        return result

    def range_query_helper(self, node, start, end, result):
        if node:
            if start <= node.date <= end:
                result.append((node.date, node.price))
            if node.date > start:
                self.range_query_helper(node.left, start, end, result)
            if node.date < end:
                self.range_query_helper(node.right, start, end, result)

class Stock:
    def __init__(self, name, ticker):
        self.name = name
        self.ticker = ticker
        self.history = BST()

    def addrecord(self, date, price):
        self.history.insert(date, price)

    def buildhistory(self, records):
        self.history.build_balanced(records)

    def getprice(self, date):
        node = self.history.search_nearest(date)
        if node:
            return node.price
        return None

    def getprice_with_date(self, date):
        node = self.history.search_nearest(date)
        if node:
            return node.date, node.price
        return None, None

    def getrange(self, start, end):
        return self.history.range_query(start, end)

    def trend(self):
        records = self.history.inorder()
        if len(records) == 0:
            return None
        start_price = records[0][1]
        end_price = records[-1][1]
        change = ((end_price - start_price) / start_price) * 100
        return round(change, 2)

NUM_BUCKETS = 509
stock_table = [[] for _ in range(NUM_BUCKETS)]

def hash_function(ticker):
    return hash(ticker) % NUM_BUCKETS

def add_stock(ticker, stock):
    bucket = hash_function(ticker)
    stock_table[bucket].append((ticker, stock))
    push_action(("add", ticker, stock))

def get_stock(ticker):
    bucket = hash_function(ticker)
    for item in stock_table[bucket]:
        if item[0] == ticker:
            return item[1]
    return "Not found"

def update_stock(ticker, new_stock):
    bucket = hash_function(ticker)
    for i, item in enumerate(stock_table[bucket]):
        if item[0] == ticker:
            old_stock = stock_table[bucket][i][1]
            stock_table[bucket][i] = (ticker, new_stock)
            push_action(("update", ticker, old_stock))
            return
    return "Not found"

def remove_stock(ticker):
    bucket = hash_function(ticker)
    for i, item in enumerate(stock_table[bucket]):
        if item[0] == ticker:
            removed_stock = stock_table[bucket][i][1]
            stock_table[bucket].pop(i)
            push_action(("remove", ticker, removed_stock))
            return
    return "Not found"

stack = []

def push_action(action):
    stack.append(action)

def undo_last():
    if len(stack) == 0:
        print("Nothing to undo")
        return

    action = stack.pop()

    if action[0] == "add":
        ticker = action[1]
        bucket = hash_function(ticker)
        for i, item in enumerate(stock_table[bucket]):
            if item[0] == ticker:
                stock_table[bucket].pop(i)
                print("Undid add: removed " + ticker)
                return

    elif action[0] == "remove":
        ticker = action[1]
        old_stock = action[2]
        bucket = hash_function(ticker)
        stock_table[bucket].append((ticker, old_stock))
        print("Undid remove: restored " + ticker)

    elif action[0] == "update":
        ticker = action[1]
        old_stock = action[2]
        bucket = hash_function(ticker)
        for i, item in enumerate(stock_table[bucket]):
            if item[0] == ticker:
                stock_table[bucket][i] = (ticker, old_stock)
                print("Undid update: reverted " + ticker)
                return

def get_sp500_metadata():
    url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    all_tables = pd.read_html(StringIO(response.text))
    for table in all_tables:
        if "Symbol" in table.columns and "Security" in table.columns:
            sp500_table = table
            break

    meta = sp500_table[["Symbol", "Security"]].copy()
    meta.columns = ["Ticker", "Company"]
    meta["Ticker"] = meta["Ticker"].str.replace(".", "-", regex=False)
    return meta

def download_returns(meta):
    tickers = meta["Ticker"].tolist()
    data = yf.download(tickers, period="2y", interval="1d", auto_adjust=True, progress=False)

    prices = data["Close"].sort_index()
    prices = prices.dropna(axis=1, how="all")

    valid_tickers = prices.columns.tolist()
    meta = meta[meta["Ticker"].isin(valid_tickers)].reset_index(drop=True)

    returns = prices.pct_change(fill_method=None).dropna(how="all")

    return meta, prices, returns

def main():
    print("Fetching S&P 500 company list...")
    meta = get_sp500_metadata()

    print(f"Downloading prices for {len(meta)} stocks...")
    meta, prices, returns = download_returns(meta)

    print("Building stock objects...")
    for ticker in prices.columns:
        company_name = meta[meta["Ticker"] == ticker]["Company"].values[0]
        stock = Stock(company_name, ticker)
        records = [(str(date.date()), price) for date, price in prices[ticker].dropna().items()]
        stock.buildhistory(records)
        add_stock(ticker, stock)

    meta.to_csv("sp500_metadata.csv", index=False)
    prices.to_csv("sp500_prices.csv")
    returns.to_csv("sp500_returns.csv")

    print(f"Done! {len(meta)} stocks loaded.")

    ticker = input("\nEnter a ticker to look up (e.g. AAPL): ").strip().upper()
    stock = get_stock(ticker)
    if stock != "Not found":
        print(f"  Trend over 2 years: {stock.trend()}%")

        choice = input("Look up a single day or a range? (day/range): ").strip().lower()
        if choice == "day":
            date = input("Enter a date to look up (YYYY-MM-DD): ").strip()
            matched_date, price = stock.getprice_with_date(date)
            if price is None:
                print(f"  No price data available for {ticker}.")
            elif matched_date == date:
                print(f"  Price on {date}: {price}")
            else:
                print(f"  No trading data on {date}. Nearest trading day was {matched_date}: {price}")
        elif choice == "range":
            start = input("Enter a start date for range (YYYY-MM-DD): ")
            end = input("Enter an end date for range (YYYY-MM-DD): ")
            print(f"  Prices from {start} to {end}: {stock.getrange(start, end)}")
        else:
            print("  Invalid choice. Please enter 'day' or 'range'.")

        print("\nTesting undo:")
        remove_stock(ticker)
        print(f"  After remove, {ticker}: {get_stock(ticker)}")
        undo_last()
        print(f"  After undo, {ticker} trend: {get_stock(ticker).trend()}%")
    else:
        print(f"{ticker} not found in hash table")

if __name__ == "__main__":
    main()