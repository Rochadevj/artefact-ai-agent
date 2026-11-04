import unicodedata

from src.data_loader import (
    load_categories,
    load_customers,
    load_order_items,
    load_orders,
    load_products,
    load_promotions,
)


def normalize_text(value: str) -> str:
    value = str(value).lower().strip()

    normalized = unicodedata.normalize("NFKD", value)

    return "".join(
        char for char in normalized
        if not unicodedata.combining(char)
    )


def search_products(
    query: str | None = None,
    category: str | None = None,
    max_price: float | None = None,
    only_available: bool = True,
) -> list[dict]:

    products = load_products()
    categories = load_categories()

    products = products.merge(
        categories[["category_id", "name"]],
        on="category_id",
        how="left",
        suffixes=("", "_category"),
    )

    if query:
        normalized_query = normalize_text(query)

        mask = products.apply(
            lambda row: normalized_query in normalize_text(
                f"{row['name']} {row['description']}"
            ),
            axis=1,
        )

        products = products[mask]

    if category:
        normalized_category = normalize_text(category)

        products = products[
            products["name_category"].apply(normalize_text)
            .str.contains(normalized_category, regex=False)
        ]

    if max_price is not None:
        products = products[
            products["price_brl"] <= max_price
        ]

    if only_available:
        products = products[
            (products["stock_quantity"] > 0)
            & (products["status"] == "active")
        ]

    results = []

    for _, product in products.iterrows():
        results.append(
            {
                "product_id": int(product["product_id"]),
                "name": product["name"],
                "category": product["name_category"],
                "price_brl": float(product["price_brl"]),
                "stock_quantity": int(product["stock_quantity"]),
                "status": product["status"],
                "description": product["description"],
            }
        )

    return results


def get_active_promotions() -> list[dict]:
    promotions = load_promotions()
    products = load_products()

    promotions = promotions[
        promotions["is_active"] == 1
    ]

    promotions = promotions.merge(
        products[
            [
                "product_id",
                "name",
                "price_brl",
                "status",
                "stock_quantity",
            ]
        ],
        on="product_id",
        how="left",
    )

    promotions = promotions[
        (promotions["status"] == "active")
        & (promotions["stock_quantity"] > 0)
    ]

    results = []

    for _, promotion in promotions.iterrows():
        discount = float(promotion["discount_percent"])
        original_price = float(promotion["price_brl"])

        discounted_price = original_price * (
            1 - discount / 100
        )

        results.append(
            {
                "product_id": int(promotion["product_id"]),
                "product_name": promotion["name"],
                "description": promotion["description"],
                "discount_percent": discount,
                "original_price_brl": original_price,
                "discounted_price_brl": round(
                    discounted_price, 2
                ),
            }
        )

    return results


def get_order_status(
    order_id: int,
    customer_email: str,
) -> dict:

    orders = load_orders()
    customers = load_customers()
    order_items = load_order_items()
    products = load_products()

    matching_order = orders[
        orders["order_id"] == order_id
    ]

    if matching_order.empty:
        return {
            "error": "Order not found or customer verification failed."
        }

    order = matching_order.iloc[0]

    customer = customers[
        customers["customer_id"]
        == order["customer_id"]
    ]

    if customer.empty:
        return {
            "error": "Order not found or customer verification failed."
        }

    customer = customer.iloc[0]

    if normalize_text(customer["email"]) != normalize_text(
        customer_email
    ):
        return {
            "error": "Order not found or customer verification failed."
        }

    items = order_items[
        order_items["order_id"] == order_id
    ].merge(
        products[["product_id", "name"]],
        on="product_id",
        how="left",
    )

    order_products = []

    for _, item in items.iterrows():
        order_products.append(
            {
                "product": item["name"],
                "quantity": int(item["quantity"]),
            }
        )

    return {
        "order_id": int(order["order_id"]),
        "status": order["status"],
        "order_date": order["order_date"],
        "total_brl": float(order["total_brl"]),
        "payment_method": order["payment_method"],
        "tracking_code": order["tracking_code"],
        "estimated_delivery": order[
            "estimated_delivery"
        ],
        "items": order_products,
    }