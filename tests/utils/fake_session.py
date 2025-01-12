class FakeSession:
    def __init__(self) -> None:
        self.committed: bool = False

    def commit(self) -> None:
        self.committed = True

    def refresh(self, instance) -> None:
        pass

    def expunge(self, instance) -> None:
        pass
