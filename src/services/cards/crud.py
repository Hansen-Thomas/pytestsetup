from sqlalchemy.exc import IntegrityError

from domain.card_repository import DuplicateCardException
from domain.card import Card
from domain.relevance import Relevance
from domain.word_type import WordType
from services.unit_of_work import AbstractUnitOfWork


def create_card_in_db(
    word_type: WordType,
    relevance_description: str,
    german: str,
    italian: str,
    uow: AbstractUnitOfWork,
) -> Card:
    try:
        with uow:
            # Business validation:
            relevance = uow.relevance_levels.get_by_description(
                description=relevance_description
            )
            if not relevance:
                relevance = Relevance(description=relevance_description)

            # Processing:
            new_card = Card(
                word_type=word_type,
                relevance=relevance,
                german=german,
                italian=italian,
            )
            uow.cards.add(new_card)
            uow.commit()
            uow.refresh(new_card)
            uow.expunge(new_card)
        return new_card
    except IntegrityError:
        raise DuplicateCardException()


def read_card_in_db(id_card, uow: AbstractUnitOfWork) -> Card:
    with uow:
        card = uow.cards.get(id=id_card)
        if not card:
            raise ValueError("Card not found")
        uow.expunge(card)
    return card


def read_all_cards_in_db(uow: AbstractUnitOfWork) -> list[Card]:
    """
    Use case: Returns detached objects to use them for templates or as a JSON-
    response.

    This means that we need to ensure that the ORM-objects don't have expired
    attributes because this would lead to a reload once those are accessed. Since
    attributes always get expired if the session is closed or a rollback takes
    place (or a commit if the session flag "expire_on_commit is set to true -
    which is its default value), we need to expunge them before the session is
    rollbacked or closed.

    What's happening here is totally NOT trivial or intuitive. It is definitely
    important to understand this in very detail, so always come back here for
    reference, let's talk in through in detail:

    - An instance is bound to its session, the session manages the state of the
      instance.
    - There are a couple of states, some of them are important in this context:
        - detached: The instance is not connected to the session anymore, this
                    is kind of our target.
        - expired: The attributes of an instance become expired in the following
                   situations:
                   a) the session is commited.
                   b) the session is rolled back
                   c) the session is closed: then the instance automatically
                      gets detached, too.
                   If an attribute is expired, it will definitely need to ask
                   the session for its current database-data in the moment this
                   attribute is accessed. This is exactly then a problem when
                   there is no session anymore connected to this instance. In
                   this situation, sqlalchemy will raise an error.
    - Having no session anymore is a problem for an instance if there
      is a need to update some of its data again. There are typically two
      situations where this might be required:
        1) We need to use an expired attribute of that instance.
        2) We need to use an attribute which is lazy-loaded in the meaning that
           this attribute (or typically a relationship-object) has not yet been
           loaded at all.
    - Now the usual mistake is as follows: We use a session, query the database,
      close the session and then return all the queried objects. In the moment
      we access any of its attributes, we will get the 'detached instance'-
      error. So why is that: Because after closing the session, all attributes
      get expired, and in the moment an attribute is expired, accessing it means
      by a 100% that it will definitely need a session to get its current data
      from the database via a session. No chance of getting around that. But
      closing a session means the objects have no session anymore to do so (they
      are now in 'detached'-state), so -> Error.
    - In our situation here, aside from closing the session the unit-of-work-
      construct as it is set up here would even do a rollback before closing the
      session, which would as well already set all attributes to 'expired'. So
      in any case, here in our lovely setup with all its advantages, we have the
      issue of expired attributes/instances and detached objects.
    - So what now, how can we solve that? We need to take care of both
      situations above, the expiring of the instance due to the mechanisms of
      sqlalchemy and the lazy-loading. The latter is no problem: We can simply
      define the mapping of relationships to handle the lazy-loading with the
      'immediate'-mode, which basically means that there is no lazy-loading but
      eager-loading: problem solved! All relationship-objects get loaded
      directly with their main instance-object, no further database-queries
      are required. Done.
    - Still, even those will get expired once any of the mechanisms described
      above will happen (rollback, closing, commiting). By the way, commiting a
      sessino usually sets all attributes to be expired as well. But in this
      most simple case we have here ('get my objects from the database and
      that's it.), we do not even have any change to commit. So setting the flag
      'expire_on_commit' to False (as suggested in the official docs) doesn't
      help at all here (even though it would na do any harm as well). However,
      so how to deal with this now, how do we get our instances out of the
      session without expiring their attributes?
    - With the 'expunge()'-method from the session!! That's our saviour!
      This method releases the instances into their freedom, cutting all
      connections to their session, but without setting their attributes to
      expired. This way, since they are not marked as expired they will not try
      to update their values in they moment we access them. So the expunge()-
      method is our hero here, it is definitely not some 'weird other method',
      it is the one thing we need to make our key-requirement work: Querying the
      database, getting ORM-objects but closing the session while still being
      able to use these instances and access their attributes without causing a
      reload-query against the database without having any session anymore.
      So the 'expunge()'-method is our shining star, we need it, it is
      something every developer needs to know in this specific context. It is
      nothing we can avoid when learning sqlalchemy!

    """
    with uow:
        cards = uow.cards.all()
        uow.expunge_all()  # needs to be called!

        # (otherwise the rollback and or closing the session would lead to
        # expired attributes, which would try to re-query the database after the
        # session is closed, which again leads to an exception.

    # if cards:  # code to test attribute-access:
    #     first_card = cards[0]
    #     print(first_card.relevance)

    return cards


def update_card_in_db(
    id_card: int,
    word_type: WordType,
    relevance_description: str,
    german: str,
    italian: str,
    uow: AbstractUnitOfWork,
) -> Card:
    with uow:
        card = uow.cards.get(id=id_card)
        if not card:
            raise ValueError("Card not found")

        card.word_type = word_type
        card.german = german
        card.italian = italian

        relevance = uow.relevance_levels.get_by_description(relevance_description)
        if not relevance:
            relevance = Relevance(description=relevance_description)
        card.relevance = relevance

        uow.commit()
        uow.refresh(card)
        uow.expunge(card)
    return card


def delete_card_in_db(id_card: int, uow: AbstractUnitOfWork) -> None:
    with uow:
        card_to_delete = uow.cards.get(id=id_card)
        if not card_to_delete:
            raise ValueError("Card not found")
        uow.cards.delete(card=card_to_delete)
        uow.commit()
