"""Demand modeling for pricing optimization."""

import numpy as np


def predicted_demand(price, base_demand=1000.0, elasticity=-1.5, competitor_price=None):
    """Analytical demand model with price elasticity.

    Args:
        price: Product price
        base_demand: Base demand at price=1
        elasticity: Price elasticity (typically negative)
        competitor_price: If provided, demand is relative to competitor price

    Returns:
        Predicted demand (units)
    """
    if competitor_price is not None and competitor_price > 0:
        # Relative pricing model: demand depends on price vs competitor
        demand = base_demand * (price / competitor_price) ** elasticity
    else:
        # Absolute pricing model
        demand = base_demand * (price ** elasticity)
    return max(demand, 0.0)


def revenue_function(price, **kwargs):
    """Calculate revenue as price * demand."""
    demand = predicted_demand(price, **kwargs)
    return price * demand
