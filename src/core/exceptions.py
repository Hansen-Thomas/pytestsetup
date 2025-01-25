class ResourceNotFoundError(Exception):
    def __init__(self, resource_type: str, resource_id: int | str):
        self.resource_type = resource_type
        self.resource_id = resource_id
        super().__init__(f"{resource_type} with ID {resource_id} not found.")


class DuplicateResourceError(Exception):
    def __init__(self, resource_type: str):
        self.resource_type = resource_type
        super().__init__(f"Identical {resource_type} already exists.")
