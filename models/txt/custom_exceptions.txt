class ReconciliationFileNotFoundError(Exception):
    def __init__(self, message='Brak pliku rekoncyliacji.'):
        self.message = message
        super().__init__(self.message)
