def create_click_counter():
  clicks = 0

  def button_clicks():
    nonlocal clicks
    clicks += 1
    return clicks

  return button_clicks


def contains_employee(employees, name):
  return name in employees


button_clicks = create_click_counter()

print(button_clicks())
print(button_clicks())
print(button_clicks())

employees = ["Emil", "Tobias", "Linus"]
print(contains_employee(employees, "Emil"))
