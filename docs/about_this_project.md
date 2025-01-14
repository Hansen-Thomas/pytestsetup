# About this Project

The basic idea of this project is to have kind of a playground to learn and fully understand how to setup a Python-architecture that enables test-driven development. It is all based on the book "Architecture Patterns with Python" (written by Percival & Gregory, published by O'Reilly) and targets on really understanding everything necessary of what happens under the hood in the frameworks used in that architecture.

## About real projects

From what I experienced in 10 years of software development, there are in the end especially two main aspects a software needs to consider:

1) **Persistence**:
   
   No matter what we develop, in nearly each case of production software data needs to be persisted. And in nearly each case, relational databases play a crucial role in this. Thus, whatever we develop, we need to be able to work with relational databases in a robust and reliable way.

2) **Changing requirements**:

   As a software evolves and the company or industry using that software evolves, the requirements change. Maybe sooner, mayber later, but we can be assured that the requirements will definitely change. These changes especially target on the business logic. Thus, we need an architecture that allows us to easily change things without breaking something. Automated tests and test-driven development play a crucial role to enable that.

In the Python-ecosystem, the ***SqlAlchemy***-framework delivers all we need to work on the first aspect, the requirement of data persistence. With the ***PyTest***-framework we have everything we need to set up automated tests. However, linking both a reliable persistence-layer and an easy-to-test business-logic-layer is somewhat of a challenge in Python. Percival and Gregory identified exactly that and developed an architecture-approach that copies ideas of other languages (like Java) to tackle the difficulties in the Python world.

In the end, what they achieve (until the end of the fist half of the book) is ***an architecture that enables domain-driven and test-driven design with a fully decoupled persistence-layer*** that can be simply turned on or off or can target to a production-database or an in-memory-test-database or to whatever else of a database. This means we have the possibility to fully make use of the two grown up frameworks **SqlAlchemy** and **PyTest** in a way they support each other in the process of software development and do not behave like obstacles for each other.

Having that in place, we have a way to develop a robust software-backend that is backed by automated software tests, is database-agnostic (which means we can exchange the whole database with ease) and is able to face the challenges of a fast changing world. It especially means that we can focus on developing solutions that solve the business-logic-problems - which is what clients actually want to pay for. We can treat persistence as a natural requirement that we don't really need to focus on during solving the business-logic-problems but from which we know that we can easily add it later on after finding working solutions.

However, using the architecture-patterns suggested by Percival and Gregory means that we definitely need to understand the technical backgrounds of all used technologies and the frameworks themselves, at least to a certain extend. On top of that, ***aside from architecture and framework concerns, there is our pretty complex ecosystem of tools we need to use to develop software***, which includes IDEs with linters, formatters and test runners, several DBMS and maybe some GUI-database-clients to observe their behaviour easily, VCS, containers, everything to deploy our software like packaging-solutions or maybe proxy-servers - oh, and front-end-frameworks as well! So learning the architecture patterns and how they interact is one thing, understanding the frameworks they use is already another one, but making use of this in a real software developing process is hell of a different thing. This is the reason why things become wild and chaotic pretty fast: Because reality kicks in and is way more complex than learning something new in an ideal, simple world.

This project is about stepping back and setting up a tiny test-application to learn the architecture patterns and the two main frameworks SqlAlchemy and PyTest together with some Python-built-in-functionalities in a real-life-environment. We want to learn how these architecture patterns work in a setup that uses VSCode as an IDE, which can be a challenge on its own since plug-ins may behave differently after updates and so on. But still, VSCode is a free-to-use IDE with pretty good support, giving us actually all we need (including VCS, linters, formatters, test runners) for free.

What we cut out here in this project is the frontend. However, we still add a Web-API to be able to do end-to-end-tests. We will set up a FastAPI-frontend-controller to supply some web-routes to trigger the backend, but using the backend-services e.g. within a desktop-application would be easily possible, too.

## About the example in this project

We set up a little app that shall help us learning the italian language by creating learning-cards that translate vocabulary from german to italian and vice versa. In this setup, we will encounter most of the relations objects and data may have - and we will try to make it look as natural as possible and not being intentionally constructed to simply have a certain kind of relationship in our model. However, this means:

- our main data model is the *learning card*, being a simple table called "Card"
- a card has a *level of relevance*, meaning it can be of 
   - Level A - vocabulary for beginners
   - Level B - vocabuly for intermediates
   - Level C - vocabulry for professionals
- by that we have a 1:n-relationship in our model
- furthermore, each card describes the *type of the word*. We could model that as a 1:n-relationship as well, but instead we will use an enumeration-type which is defined in the Python-code. This might be unnatural for the domain, but we rather more want to have this kind of object-relatinoship in our example as well.
- next, cards can have *multiple tags* indicating their domain, like "Nature", "Work", "Person", "at the doctor" and so on. These tags can be used for multiple cards, resulting in a m:n-relationship.

Apart from that, we may add further entities and relationships, but having the ones mentioned above in place, we have more or less everything in our app which is of relevance in the real world.

## How the architecture is set up

The steps Percival and Gregory undertake basically all focus on getting rid of everything about persistence in our service-functions which shall solve the problems of the business-domain.

To achieve that, they do the following:

1) They use SqlAlchemy's ORM and define it in the classical, "imperative" style. In this style, the linking of database-table-structures and Python-classes is done in a separate file, not together at once. This results in plain old Python objects that model our domain, so there is no dependency to the persistence framework at all in our domain. This ensures that modeling our domain is not distracted by any persistence-logics and that writing unit-tests is a charme as we do not need to care about anything related to our data-layer.

2) They introduce the repository-pattern as a data-access-layer to fake the whole database as such, enabling us to test our service-functions with in-memory-fake-data that can be accessed exactly the same as the real database-data.

3) They introduce the service-layer as the entry-point to the domain-objects and the data-access-layer. By that, the clients only communicate with this service-layer and do not need to interact with anything of the domain and the data-layer directly.

4) They introduce the unit-of-work-pattern to be the one and only dependency towards the data-layer which in the same time ensures atomacity of our data-operations. By that, the service-layer only depends on this unit-of-work and only this one object decides with which data-source we work, be it a real database in production or fake in-memory-data for our automated tests.

After all, we have a service-layer that is the only entry-point for our clients and that solves all use-cases the software shall handle. We create a unit-of-work that defines with which data-source we want to work and hand that over to the service-methods. And that's it. The repository-pattern and the imperative mapping-style of the ORM ensure that we have no dependencies to our data-layer in our whole domain model, making it a pure OOP-model we can easily use for domain-driven and test-driven development without caring about persistence at all.