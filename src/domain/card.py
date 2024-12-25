from domain.tag import Tag


class Card:
    def __init__(self):
        self.id: int | None = None
        self.german: str = ""
        self.italian: str = ""
        self.tags: set[Tag] = set()

    def add_tag(self, tag: Tag):
        self.tags.add(tag)

    def remove_tag(self, tag: Tag):
        if tag in self.tags:
            self.tags.remove(tag)
