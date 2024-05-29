from datetime import datetime, UTC
from math import floor

WINDOW_THRESHOLD = 1000

class PopPricer:
  def __init__(self, start_price, max_price, reset_interval_seconds):
    """
    """
    self._start_price = start_price
    self._max_price = max_price
    self._reset_interval_seconds = reset_interval_seconds or 1800 # every 30 mins
    self._last_cost = None
    self._cost = 0
    self._cost_queue = []

  def peek(self):
    return self._calculate_price()

  def push(self, cost):
    return self._calculate_price(cost)

  def _calculate_price(self, additional_cost=0):
    """
    Fetch current surge price according to sliding window, optionally incurring a new cost
    """
    self._pop_costs_to_timestamp(datetime.now(UTC))
    self._push_cost(additional_cost)

    calculation = self._round_price(self._current_multiplier() * self._start_price)
    return min(max(calculation, self._start_price), self._max_price)

  def _current_multiplier(self):
    return 1 + self._cost / WINDOW_THRESHOLD
  
  def _round_price(self, price):
    dec = price % 1
    if dec < 0.25:
      return round(price) - 0.01
    elif dec < 0.75:
      return floor(price) + 0.49
    else:
      return floor(price) + 0.99

  def _pop_costs_to_timestamp(self, timestamp):
    """
    Clears the incurred surge cost based on sliding window progress (reset interval)
    """
    delta = datetime.now(UTC) - timestamp
    delta_mins = delta.days * 24 * 60 + delta.mins + delta.seconds / 60
    
    # if not self._cost_queue:
    #   return
    
    # now = datetime.now(UTC)
    # while self._cost_queue:
    #   top_time, top_cost = self._cost_queue[0]
    #   delta = (now - top_time).seconds
    #   if delta >= self._reset_interval_seconds:
    #     self._cost = max(0, self._cost - top_cost)
    #     self._cost_queue.pop(0)
    #   else:
    #     break

  def _push_cost(self, cost):
    """
    Tracks an additional cost and associated timestamp
    """
    self._cost += cost
    self._last_cost = datetime.now(UTC)
    # self._cost_queue.append(
    #   (
    #     datetime.now(UTC),
    #     cost
    #   )
    # )  

