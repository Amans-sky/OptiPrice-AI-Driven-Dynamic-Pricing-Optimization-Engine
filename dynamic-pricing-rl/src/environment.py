import numpy as np

class PricingEnvironment:
    """Professional pricing environment with rich state representation.

    State: [demand_level, competitor_price, inventory_level]
    Action: index into price_levels.
    Reward: revenue = price * demand(price)
    """
    def __init__(self, max_steps=100):
        self.price_levels = np.arange(5, 55, 5)  # [5,10,...,50]
        self.max_steps = max_steps
        self.current_step = 0

        # State variables
        self.demand_level = 0.0
        self.competitor_price = float(np.random.uniform(10.0, 40.0))
        self.inventory_level = 1000.0

    def reset(self):
        """Reset environment for new episode."""
        self.current_step = 0
        self.competitor_price = float(np.random.uniform(10.0, 40.0))
        self.inventory_level = 1000.0
        self.demand_level = float(np.random.uniform(50.0, 200.0))
        return self._get_state()

    def _get_state(self):
        """Return current state as numpy array [demand_level, competitor_price, inventory_level]."""
        return np.array(
            [self.demand_level, self.competitor_price, self.inventory_level],
            dtype=np.float32
        )

    def demand_function(self, price):
        """Calculate demand based on price and competitor price."""
        base_demand = 1000.0
        elasticity = -1.5
        # Demand depends on relative price vs competitor
        demand = base_demand * (price / max(self.competitor_price, 1.0)) ** elasticity
        return max(demand, 0.0)

    def step(self, action):
        """Execute one environment step."""
        price = float(self.price_levels[int(action)])
        demand = self.demand_function(price)
        revenue = price * demand

        # Update inventory
        self.inventory_level = max(0.0, self.inventory_level - demand)

        # Update demand level (normalize)
        self.demand_level = max(0.0, min(200.0, demand / 10.0))

        # Competitor price drifts randomly (random walk)
        self.competitor_price = max(1.0, self.competitor_price + float(np.random.normal(0.0, 1.0)))

        self.current_step += 1
        done = self.current_step >= self.max_steps

        state = self._get_state()
        info = {
            "demand": demand,
            "competitor_price": self.competitor_price,
            "inventory_level": self.inventory_level
        }
        return state, float(revenue), done, info
