from datetime import datetime, UTC
from math import floor

class PopPricer:
  def __init__(self, start_price, max_price, reset_rate=0.05, cost_weight=0.001):
    """
    """
    self._start_price = start_price
    self._max_price = max_price
    self._cost_weight = cost_weight
    self._reset_rate = reset_rate
    self._last_cost = None
    self._cost = 0

  def peek(self):
    return self._push_cost(0)

  def push(self, cost):
    return self._push_cost(cost)

  def _push_cost(self, cost):
    """
    Fetch current surge price according to sliding window, optionally incurring a new cost
    """
    if self._last_cost:
      delta = datetime.now(UTC) - self._last_cost
      self._cost = max(self._cost - delta.total_seconds() * self._reset_rate, 0)
    
    self._last_cost = datetime.now(UTC)
    if cost:
      self._cost += cost

    current_multiplier = 1 + self._cost * self._cost_weight
    calculation = self._round_price(current_multiplier * self._start_price)
    # TODO allow dip below
    return min(max(calculation, self._start_price), self._max_price)
  
  def _round_price(self, price):
    dec = price % 1
    if dec < 0.25:
      return round(price) - 0.01
    elif dec < 0.75:
      return floor(price) + 0.49
    else:
      return floor(price) + 0.99


