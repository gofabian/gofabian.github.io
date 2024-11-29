class Progress:

    def __init__(self, name, stocks, error_to_catch=None):
        self.name = name
        self.stocks = stocks
        self.elapsed = 0
        self.error_to_catch = error_to_catch
        self.errors = []

    def next(self, lbda):
        self.animate()
        self.elapsed += 1
        if self.elapsed == len(self.stocks):
            print()
        try:
            return lbda()
        except Exception as e:
            if isinstance(e, self.error_to_catch):
                self.errors.append(e)
            else:
                raise e

    def animate(self):
        print(f'\rProgress "{self.name}": {self.elapsed + 1}/{len(self.stocks)} {self.stocks[self.elapsed]} ', end='')
