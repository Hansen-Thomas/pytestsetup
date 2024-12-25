from domain.tag import Tag


def test_tag_can_be_created():
    tag = Tag(value="my_test_tag")
    assert tag.value == "my_test_tag"
