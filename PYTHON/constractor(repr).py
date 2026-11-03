class gf:
    def __init__(self,name,age,address):
        self.name=name
        self.age=age
        self.address=address
    def __repr__(self):
        return f'''
        gf.name={self.name}
        gf.age={self.age}
        gf.address={self.address}'''
gf1=gf("Radhika",20,"patal loke")
print(gf1)        
