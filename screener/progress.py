class Progress:

    def __init__(self, name, stocks):
        self.name = name
        self.stocks = stocks
        self.elapsed = 0

    def next(self, lbda):
        self.animate()
        self.elapsed += 1
        if self.elapsed == len(self.stocks):
            print()
        return lbda()

    def animate(self):
        print(f'\rProgress "{self.name}": {self.elapsed + 1}/{len(self.stocks)} {self.stocks[self.elapsed]}', end='')
