from datetime import datetime, UTC
from math import floor
import json

class Pricer:
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
    """
    Check current price without increasing it
    """
    return self._push_cost(0)

  def push(self, cost):
    """
    Check current price for a given cost, to be combined with the cost weight as a multiplier of original price
    """
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
    return min(max(calculation, self._start_price), self._max_price)
  
  def _round_price(self, price):
    """
    Round price to nearest displayable price (X.99, X.49, X.99)
    """
    dec = price % 1
    if dec < 0.25:
      return round(price) - 0.01
    elif dec < 0.75:
      return floor(price) + 0.49
    else:
      return floor(price) + 0.99
  
  def __str__(self):
    return self.Serializer(self).serialize()

  class Serializer:
    def __init__(self, pricer):
      self._pricer = pricer

    def serialize(self):
      data = {
        "_start_price": self._pricer._start_price,
        "_max_price": self._pricer._max_price,
        "_reset_rate": self._pricer._reset_rate,
        "_cost_weight": self._pricer._cost_weight,
        "_last_cost": self._pricer._last_cost and self._pricer._last_cost.isoformat(),
        "_cost": self._pricer._cost
      }
      return json.dumps(data)

    @staticmethod
    def deserialize(str):
      try:
        data = json.loads(str)
        p = Pricer(data['_start_price'], data['_max_price'], data['_reset_rate'], data['_cost_weight'])
        p._last_cost = data['_last_cost'] and datetime.fromisoformat(data['_last_cost'])
        p._cost = data['_cost']
        return p
      except json.decoder.JSONDecodeError:
        return None
