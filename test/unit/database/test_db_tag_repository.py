from database.repositories.tag_repository import DbTagRepository
from domain.tag import Tag


def test_db_tag_repo_can_add_tag(session):
    # Arrange:
    tag_repo = DbTagRepository(session)

    # Act:
    tag = Tag("Natur")
    tag_repo.add(tag)
    session.commit()

    # Assert:
    all_tags = tag_repo.all()
    assert len(all_tags) == 1
    tag = all_tags[0]
    assert tag.value == "Natur"
