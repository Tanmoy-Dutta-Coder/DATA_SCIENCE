class Company:
  def __init__(self, employees):
    self.employees = employees

  def __contains__(self, name):
    return name in self.employees

c1 = Company(["Emil", "Tobias", "Linus"])

print("Emil" in c1)