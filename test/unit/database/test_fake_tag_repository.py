from database.repositories.tag_repository import FakeTagRepository
from domain.tag import Tag


def test_fake_tag_repo_can_add_tag(fake_session):
    # Arrange:
    tag_repo = FakeTagRepository(fake_session)

    # Act:
    tag = Tag("Natur")
    tag_repo.add(tag)
    fake_session.commit()

    # Assert:
    all_tags = tag_repo.all()
    assert len(all_tags) == 1
    tag = all_tags[0]
    assert tag.value == "Natur"
