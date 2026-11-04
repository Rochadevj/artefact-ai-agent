from pathlib import Path

import pandas as pd


DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def find_csv(filename_suffix: str) -> Path:
    matches = list(DATA_DIR.glob(f"*{filename_suffix}"))

    if len(matches) != 1:
        raise FileNotFoundError(
            f"Expected exactly one file ending with '{filename_suffix}', "
            f"but found {len(matches)}."
        )

    return matches[0]


def load_products() -> pd.DataFrame:
    return pd.read_csv(find_csv("products.csv"))


def load_categories() -> pd.DataFrame:
    return pd.read_csv(find_csv("categories.csv"))


def load_promotions() -> pd.DataFrame:
    return pd.read_csv(find_csv("promotions.csv"))


def load_customers() -> pd.DataFrame:
    return pd.read_csv(find_csv("customers.csv"))


def load_orders() -> pd.DataFrame:
    return pd.read_csv(find_csv("orders.csv"))


def load_order_items() -> pd.DataFrame:
    return pd.read_csv(find_csv("order_items.csv"))