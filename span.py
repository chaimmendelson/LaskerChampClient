import time
class client:
    
    def __init__(self, elo, id):
        self.id = id
        self.elo = elo
        
        
clients = []
elo = 0
for i in range(300):
    elo += 0
    clients.append(client(elo, i))


client_elo = 1006
clients2 = []
now = time.time()
closest_elo = min(clients, key=lambda x: abs(x.elo - client_elo))
print(time.time() - now)
print(closest_elo.id)
