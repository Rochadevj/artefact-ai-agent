from src.tools import (
    get_active_promotions,
    get_order_status,
    search_products,
)


def test_search_products_by_name():
    results = search_products(query="Takamine GD20")

    assert len(results) == 1
    assert results[0]["product_id"] == 95
    assert results[0]["price_brl"] == 2199.0


def test_search_products_by_price_and_category():
    results = search_products(
        category="Violões",
        max_price=1000,
    )

    assert len(results) > 0

    for product in results:
        assert product["price_brl"] <= 1000
        assert product["stock_quantity"] > 0
        assert product["status"] == "active"


def test_active_promotions():
    promotions = get_active_promotions()

    assert len(promotions) > 0

    for promotion in promotions:
        assert promotion["discount_percent"] > 0
        assert (
            promotion["discounted_price_brl"]
            < promotion["original_price_brl"]
        )


def test_order_with_correct_customer_email():
    result = get_order_status(
        order_id=1,
        customer_email="pedro.oliveira@jmail.com",
    )

    assert "error" not in result
    assert result["order_id"] == 1


def test_order_rejects_wrong_email():
    result = get_order_status(
        order_id=1,
        customer_email="wrong@example.com",
    )

    assert "error" in result