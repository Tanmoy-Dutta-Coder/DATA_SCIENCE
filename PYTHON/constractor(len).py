class Company:
  def __init__(self, employees):
    self.employees = employees

  def __len__(self):
    return len(self.employees)

c1 = Company(["Emil", "Tobias", "Linus"])

print(len(c1))