# Lessons learned

## Architecture and patterns

### Repository pattern

- for our test-driven-approach, we usually need exactly three repository-classes:
    1) the abstract base class of the repository
    2) the fake-implementation we use for the unit-tests with in-memory-data
    3) the real one that connects to the database

- ***File organization***: After trying out a lot, in the end the best overview might be given if the three repository-classes mentioned above all live in one
  file, e.g.:

  ```
  card-repository.py:

  # imports ...

  class AbstractCardRepository(ABC):
      ...

  class FakeCardRepository(AbstractCardRepository):
      ...

  class DbCardRepository(AbstractCardRepository):
      ...

  ```

  Another question is where these repository-files shall live, in the domain-directory or in the database-directory. There is no perfect answer, but it might make sense to keep the database-directory really as thin as possible. This would mean that we only keep the following things in the database-folder:

  - the tables-directory with all files that describe the table-metadata
  - the init-file that defines how we connect to the databases
  - the orm-file that maps the tables to their corresponding domain-classes.

  The repository-files are then part of the domain (as it is anyway meant to be by Evans). As they are way more influenced by our apps requirements than the three database-aspects mentioned above (table-structure, connecting and ORM), putting them into the domain-directory feels quite natural.

### Service layer

- within the service-layer usually we at least need a couple of services that implement the CRUD-functionalities. It makes sense to put these together in one file for one certain domain-object, e.g. one file for all CRUD-services we need for the cards.

- what we do need in terms of CRUD are usually 5 services:
  1) Create new reacord
  2) Read one certain record
  3) Read a list of records in a paginated manner
  4) Update a record
  5) Delete a record

  It's interesting how tempting it is to create a "read-all"-service. It doesn't make sense, forget it. Of course we can implement it, and it doesn't hurt if we e.g. offer a method to "get-all" in the corresponding repository, but for web-apps, a "read-all"-service doesn't make sense. You should never offer a way to read and transmit all records of a certain entity to a client - what would happen if there are already millions of records existing for that entity? So simply forget about it. We need a "read-one" and a "read-list-paginated"-service in terms of reading, no more, no less. And the "read-list-paginated"-service should of course offer filter-options as they make sense in the given domain.

## Testing

### e2e-tests:

The major idea should be: Write two e2e-tests for each feature: One with the happy path and one with the unhappy path. Then, cover all possible unhappy-path-constellations in the unit-tests and not in the e2e-tests. There we are just interested in seeing that the unhappy path results in a server-response that makes sense for the client. In the unit-tests we want to cover all unhappy-path-possibilities in detail.

### unit-tests:

Write the vast majority against the services, there is the place to check for all the possible unhappy-path-constellations. Write tests against the domain-model especially while developing new aspects of the model, but sooner or later, turn over to write the tests against the service layer as that is usually the best compromise of testing details but still as well parts of the bigger picture.

### integration-tests:

Here by that we mean "all tests about data-access, ORM etc.". We need them to ensure that our mapping works as expected. As in the unit-tests the domain-objects have the most details and the services lesser, here in the integration-part we have the following order from detailed to more broad:

connection >> ORM >> repositories >> Unit of work

The unit of work is most general, so more or less comparable with the services in the unit-tests-area. Again, it makes sense to move the tests to the more general ones after establishing a working fundament. So move them sooner or later from ORM to the repositories or the unit of work to ensure that you always cover the whole processes and not only highly detailed edge-cases.

## FastAPI-setup:

### REST-API-setup vs SSR with e.g. jinja2-templates

If we want to use e2e-tests (and we definitely do want that), we anyway need a REST-API to keep things feasable. So having that said: We anyway need the REST-API-endpoints. It is not a question of "either REST-API-endpoints of jinja2-templates-endpoints", it is a question of whether we want to add the jinja2-template-endpoints on top of our REST-API-endpoints.

### Practical experience with jinja2-template-endpoints:

So far, we have not used React or any other Web-Framework at all, which is the reason why we went with jinja2-endpoints. However, creating endpoints that support both, a pure REST-API-style-JSON-response and a jinja2-template-response increases complexity and work a lot. So sooner or later, we should do the transition towards using e.g. React and then only using the simple REST-API-endpoints with JSON-responses after all.