class ClickCounter:
  def __init__(self):
    self.clicks = 0

  def __call__(self):
    self.clicks += 1
    return self.clicks

button_clicks = ClickCounter()

print(button_clicks())
print(button_clicks())
print(button_clicks())