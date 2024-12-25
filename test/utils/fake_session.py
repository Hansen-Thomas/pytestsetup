class FakeSession:
    def __init__(self) -> None:
        self.committed: bool = False

    def commit(self) -> None:
        self.committed = True
