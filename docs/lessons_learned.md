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

### Unit-of-work

The unit-of-work-pattern as we use it here has its beauty in two aspects: Firstly, it is the perfect place to hold our repositories and this way amazingly organizes our whole architecture-setup. However, SQLAlchemy's *Session*-object is already a unit-of-work. But still, as Gregory and Percival point out it makes sense to reimplement that on our own to be independent of framework-behaviour. The idea of the unit of work however is to provide atomicity, so ensuring that we get a controlled all-or-nothing-behaviour in our persistence-transmissions, so this is the second aspect aside from organizing our repositories in this one place.

## Testing

### Tests and persistence:

That's more or less the holy grail, here things get tricky and one of the main difficulties is creating an architecture where writing unit-tests is easy without setting up a lot of infrastructure (with the target of **no** infrastructure for fast running unit tests). Our architexture is capable of doing so, but still it's getting pretty complex and easy to loose track pretty fast, so here is the overview of what role persistence plays in each kind of our tests:

- ***unit-tests***:
  - **testing the domain**:  
      Use no infrastructure (i.e. database-access) at all, just create the domain-objects as you need them and test them. Don't ask where they come from (in production usually in some way from a database) but simply create them in memory and test your domain logic.
  - **testing the service layer**:  
      In our architecture, the services should all have a unit-of-work as a parameter-dependency (in case they need persistence). Here in the unit-tests, hand over a unit-of-work that is based on a session (or session-factory) which connects to a local database for unit tests that is automatically created for each test-run. **Watch out:** Without using FastAPI it is amazingly easy to use a SQLite-in-memory-database for that, which is really fast. However, in the moment we start using FastAPI, the in-memory-database doesn't work anymore and as far as I can see in the web, the multiple threads of FastAPI are at least one of the issues here. So here in this project we simply exchanged the in-memory-database from SQLite by a *"real"* file-based SQLite-database (so a simply "normal" SQLite-database). This is still fast enough for our situation here. However, if apps grow, it might make sense to provide an in-memory-database for the fast-running unit tests and a file-based-test-database for the tests which involve FastAPI.
- ***unit-tests for the integration-layer***:
  - Since we use *THE* default persistence framework in the python ecosystem (i.e. SQLAlchemy), in my  view we should focus on two things here: Assuring that we can connect at all to a database (so that there is nothing totally dumb in our way which we oversee while creating the connection) and then rather more important testing our whole setup that builds on top of the SQLAlchemy-basics. In our case, that's especially the repositories and the unit of work, but as well (a bit more basic though) the ORM-definition we use for that. However, we do not need to test the framework itself (as that's anyway done way more in detail by the developers of SQLAlchemy). Thus, in my view it is enough to test against a local unit-test-database and not against any kind of more production-like database, but that's a point of how far we are towards really deploying our app and making it a real thing. At least for a long time in the beginning, testing all our architecture-layers that build on top of SQLAlchemy against a local unit-test-database is quite legit in my view (since being database-agnostic and thus able to change the database is one of the key things SQLAlchemy is actually about besides the ORM). So to sum up: Integration tests should run against a local unit test database.
  - One thing is very easy to forget while testing the integration-layer: Ensure that you understand WHAT you want to test here. Being able to connect ot a database is definitely the least important thing, we should cover it shortly but no more. What we want to test here is more or less the ORM and all the architecture-layers we build on top of that, so the repository and the unit of work. And here, the important thing is: We want to see whether our ORM-setup always works, and the best way to find that out is to always use both in our tests: The ORM to add or read data on the one hand and plain SQL on the other hand, e.g. by setting up data with plain SQL and then reading that data again with our ORM-based repository and then check whether the data is as expected. This is the important thing, to see whether all our architecture-layers still retrieve something in our ORM-world as we would expect it with plain SQL. So if you check our integration-tests, you'll recognize that usually both of these two mechanisms - plain SQL and ORM-style - are used to always test exactly that. So never confuse what to test here, being able to connect to the database is of course important but usually just worth it a short test, and testing the business-logic is a matter of the unit-tests (domain and service layer), so don't cover it here!
- ***e2e-tests***:  
  Here we should definitely test at least against a local unit test database to be as close to reality as possible, even testing against a staging-database in a really production-like setup makes sense as we are getting closer to real deployment.

So to sum up:
- unit-tests:
  - domain: no database in unit tests
  - service-layer: in-memory-database if possible, else local file-based database
- integration-tests:
  - local file-based database
- e2e-tests:
  - local file-based database
  - production-like staging-database if close to real deployment-mode.


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