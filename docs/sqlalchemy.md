# How SqlAlchemy works

SqlAlchemy is a pretty complex framework for database-connectivity and all about SQL. It offers everything from emitting simple textual SQL to using DBMS-agnostic ORM. Thus, getting lost is easy. This introduction does not replace reading the official docs and the great tutorial but instead tries to add those background information which are often missing in the official docs and deliver the context needed to fully understand how all the concepts work together.

## Up front: Key concepts and what's always given

SqlAlchemy divides it's API into two bigger concepts: "Core" and "ORM". However, it makes sense to make it even three to include textual SQL as well, so let's break it down to these three main concepts:

1) *Textual SQL:*
   
   Connecting to a database and emitting textual SQL. This is the most basic way, here we use SqlAlchemy only to connect to a database and do the old-fashioned, plaintext-SQL-work. We work with the SqlAlchemy objects "Engine" to set up connectivity, the "Connection" to emit statements we wrap in the "text()"-construct and the "Result" to receive data from the database. (We mainly mention it here to underline that really no other SQL-tools are required to work with databases in the Python-ecosystem aside from SqlAlchemy.)

2) *Core*: 

   Describing the database structure with metadata in Python and creating statements directly in Python based on that metadata. In this moment, we are database-agnostic and don't write textual SQL on our own anymore. We mainly add the SqlAlchemy objects "MetaData", "Table" and "Column" to our toolset to be able to describe the database structure (plus many classes to describe column types, foreign keys and so on) and the Sql-statement-constructs such as "select()", "insert()" etc. to replace the textual SQL with Python-constructs.

3) *ORM:*

   Mapping SQL-tables and their columns to Python-objects (rather more classes) and their attributes. Here we make the step from working with database-logic to working with domain-objects. To achieve that, we need again to add some SqlAlchemy-objects to our toolset, which are the "registry" and "Mappers" to set up these mappings and the "Session" as our way of connecting to the database in the context of ORM (this "Session" more or less replaces the "Connection" in the moment we want to use SqlAlchemy's ORM).

When using SqlAlchemy, some really important basic things are always guaranteed to be happening. These include:

- **Escaping**: Automatically generated SQL-statements are always escaped. When using textual SQL, always use the bind-parameters-syntax and you'll be on the safe side. This way, there are no chances for SQL-Injections.
- **Transactions**: SqlAlchemy emits statements always in the context of a database-transaction. This happens no matter whether you use the ORM, SqlAlchemy-Core-constructs or textual SQL.

## On Database-Transactions

It is crucial to understand what database transactions are and how they typically work to understand what's really happening when we use SqlAlchemy to emit statements against a database.

SqlAlchemy **always** uses transactions, so be ensured that this knowledge really is important to understand the effects of emitting statements.

### Transactions-buffer

Database-transactions are something like a buffer in the DBMS that shall ensure data integrity in the moment where more than one user/application tries to modify the same data or when something technically goes wrong. In this context, the keyword is "ACID" or the ***ACID-properties*** (atomicity, consistency, isolation, durability), respectively. As Wikipedia states: 

> "In computer science, ACID (atomicity, consistency, isolation, durability) is a set of properties of database transactions intended to guarantee data validity despite errors, power failures, and other mishaps. In the context of databases, a sequence of database operations that satisfies the ACID properties (which can be perceived as a single logical operation on the data) is called a transaction."

Whenever someone starts a transaction (with **BEGIN**), a new transaction-context for this user is created within this transaction-buffer of the DBMS. If another user starts another transaction, a second transaction-context is created within this buffer.

Whatever happens within a transaction only takes place within this transaction-buffer (more or less, details follow below). Even though it may look like the data-changes are already persisted to the database, they are not (which means that e.g. primary keys are already created in the transaction-buffer, so it definitely looks like everything is already finally persistet even though it isn't). It will only be really *"materialized"* to the database when the user commits the transaction (with **COMMIT**). If he doesn't, all not yet committed changes will never be transfered from the transaction-buffer to the actual database, so they will be lost again. Another option is to intentionally rollback all pending changes of the current transaction (with **ROLLBACK**), e.g. in case something goes wrong.

We can imagine this whole setup as follows:

![image that illustrates the transaction buffer of a DBMS](transaction-buffer-1.jpg)

### Flushing and Commiting

There are two different mechanisms to differentiate in handling the transaction: **Flush** and **Commit**:
- **Flushes** can be emitted manually but are often emitted automatically by SqlAlchemy as well, e.g. before executing a SELECT-statement or before commiting the transaction. The flush moves changes from the SqlAlchemy-Session to the transaction-buffer of the DBMS.
- **Commits** are emitted manually by the user (as long as *auto-commit* has not been configured to happen). Commits finally move changes from the transaction-buffer to the DBMS, so a commit really materializes state-changes in the database.

These two mechanisms can be illustrated as follows:

![image that illustrates the difference between flush and commit](transaction-buffer-2.jpg)

### Transaction-isolation

It is a matter of configuration to what extend two (or more) transactions are really isolated from each other. This is called the level of transaction-isolation. It defines how much of the data-changes of a transaction is visible to the database and other transactions. Usually, there are 4 different levels to differentiate:

1) **READ UNCOMMITED**:
   
   From SqlAlchemy's docs:

   > One of the four database isolation levels, read uncommitted features that changes made to database data within a transaction will not become permanent until the transaction is committed. However, within read uncommitted, it may be possible for data that is not committed in other transactions to be viewable within the scope of another transaction; these are known as “dirty reads”.

2) **READ COMMITED**:

   From SqlAlchemy's docs:

   > One of the four database isolation levels, read committed features that the transaction will not be exposed to any data from other concurrent transactions that has not been committed yet, preventing so-called “dirty reads”. However, under read committed there can be non-repeatable reads, meaning data in a row may change when read a second time if another transaction has committed changes.

3) **REPEATABLE READ**:

   From SqlAlchemy's docs:

   > One of the four database isolation levels, repeatable read features all of the isolation of read committed, and additionally features that any particular row that is read within a transaction is guaranteed from that point to not have any subsequent external changes in value (i.e. from other concurrent UPDATE statements) for the duration of that transaction.

4) **SERIALIZABLE**:

   From SqlAlchemy's docs:

   > One of the four database isolation levels, serializable features all of the isolation of repeatable read, and additionally within a lock-based approach guarantees that so-called “phantom reads” cannot occur; this means that rows which are INSERTed or DELETEd within the scope of other transactions will not be detectable within this transaction. A row that is read within this transaction is guaranteed to continue existing, and a row that does not exist is guaranteed that it cannot appear of inserted from another transaction.  
   >
   > Serializable isolation typically relies upon locking of rows or ranges of rows in order to achieve this effect and can increase the chance of deadlocks and degrade performance. There are also non-lock based schemes however these necessarily rely upon rejecting transactions if write collisions are detected.

The fifth option is called **AUTOCOMMIT** and effectively avoids the transactional character of the connection and directly persists any change to the database. This especially means that there is no option for a rollback. Technically, using AUTOCOMMIT means that each single SQL-statement is executed as an own transaction which is directly commited.

The isolation level can be set per connection/session or for the engine, meaning as the default for all connections/sessions based on that engine.

If not explicitely configured, the **default-transaction-isolation** of the currently used DBMS will be used. These are:

- PostgreSQL: READ COMMITTED
- MySQL (InnoDB): REPEATABLE READ
- SQLite: SERIALIZABLE
- Oracle: READ COMMITTED
- SQL Server: READ COMMITTED

## The two worlds of the ORM: In-memory with the session and persistent in DB:

When using the ORM, we always need to keep in mind that the certain set of
records we are currently working on exist in two worlds: They live in the
memory in shape of ORM-mapped Python-objects and they live in the database.

SqlAlchemy's session-object organizes all that, it manages the ORM-mapped
objects and keeps track of the differences compared to the database. It always
works in the context of a database-transaction and flushes changes every now
and then (or when we explicitely ask it to do so). Once we commit all changes,
the session will finally flush all pending changes to the transaction-buffer and
ask the DBMS to commit this transaction.

Now there are a lot of mechanisms in a DB we usually want to use, like
constraints or cascades etc. Now what we need to keep in mind: We can set up
these mechanisms (like cascading) on the DB but as well on the ORM-world. Let's
check that out to understand the difference:

In the metadata we define to describe our database-structures, we can define
constraints and their behaviour, e.g. like here:

```
card_has_tag_table = Table(
    "Card_has_Tag",
    metadata,
    Column(
        "id_card",
        Integer,
        ForeignKey("Card.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "id_tag",
        Integer,
        ForeignKey("Tag.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)
```

These "`ondelete`"-parameters tell SqlAlchemy that the DB-table shall configure
the ForeignKey-relationship such that DELETE cascades. So this will directly
end up in the database as constraints!

Having that in place usually makes sense and reduces the risk of data-integrity-
issues etc. However, there is as well a way to set the very same up in the ORM-
world. This is done in the definition of our mapping:

```
mapping_registry = registry()
mapping_registry.map_imperatively(
   Card,
   card_table,
   properties={
      "tags": relationship(
            Tag,
            secondary=card_has_tag_table,
            collection_class=set,
            lazy="immediate",
            cascade="all",
      ),
      "relevance": relationship(
            Relevance,
            lazy="immediate",
            cascade="save-update, expunge",

            # Don't choose "all" because of delete: "all" would include
            # delete, which would lead to the following problem:
            # If a card shall be deleted, the session would then
            # automatically cascade this delete-command as well to
            # the relevance-object that is connected to the card.
            # But we can expect that re thelevance-record in DB is as well
            # connected to other cards (normal 1:n-situation in DB).
            # Deleting the ORM-mapped relevance-object would issue
            # SQL-statements to delete the corresponding DB-record.
            # This again is very likely to not work because the DB cannot 
            # violate that foreign-key-constraint as this relevance-record
            # is very likely to be connected to other cards in DB already.
            # 
            # We always need to differentiate between the ORM-objects and
            # the DB-records. The cascade-parameter here deals with the
            # cascading within the ORM-object tree. The cascading in the DB
            # is defined in the SqlAlchemy-Table-objects with parameters of
            # the ForeignKey-class ("ondelete" and "onupdate"). These
            # parameters result in DDL that adds these constraints to the
            # DB-schema.
      ),
   },
)
```

See the comment in the code above. Here we define the cascading within the ORM-
mapped object-tree, so all changes take already place in the memory before we
flush anything to the database.


## About expiring and expunging

When working with sessions to retrieve objects from DB, we often run into the
situation that we want to already close the session but need to returned objects
in subsequent steps. This especially is a result from our architecture where we
want to encapsulate the database but of course still need the data in some other
places (like e.g. to return them to a user via web-API.)

Here we run into a situation, because in ORM-mappers there is the concept of
"expiring", which is totally making sense but is somewhat in our way here:

In several situations, ORM-mapped objects are set to be "expired". This is for
example the case if a session is committed. In this moment, SqlAlchemy says
"well i just committed a transaction, i honestly have no idea how the data you
have been working on does look like right now after committing since someone
else might as well just modified that!". And this is totally correct! So what it
does is it sets the objects that have been part of that session to be "expired".
This has a very important effect: Whenever we access the attributes of such an
object, SqlAlchemy will try to synchronize them with their current DB-data by
using the session. But often in this very moment, we want to the session to be
already closed. And this will lead to an exception! So what shall we do now?

First let's see in which situations objects are marked as expired:
- after committing the session
- after rolling back the session
- after closing the session

Our problem occurs in the moment the session is closed, because then there is no
chance anymore for SqlAlchemy to use that session to get the current data from
DB. If a session is closed, all its objects become "detached", so to be precise:
Detached objects with expired attributes are our problem, because "expired"
means that SqlAlchemy wants to update them and "detached" means it has no
session to do so. But being detached is exactly what we often want our objects
to be to use them on other subsequent steps.

So our target is to get detached objects without being expired. As long as the
session is not closed yet, getting an expired object to be updated with its 
current DB-data is as easy as calling the "`refresh`"-method of the session with
this object:

```
session.refresh(my_object)
```

This changes the object to be not expired anymore. And getting that object to be
detached but without expiring it again is possible with the session's 
"`expunge`"-method! Expunging means that we remove expunged object from the
session, but without setting its state to be "expired". And here we are, that's 
all we need to do:

```
session.expunge(my_object)
```


### Two important fun-facts:

The behaviour of "refreshing" objects is different in debugging mode and in
normally executed code. Never just test something out in your debugger! It might
happen that an object seems to be automatically refreshed by the session right
after committing. **But this is a lie! :-)** Never trust that behaviour, when we
execute our code in a normal application run, it will be different. After a
commit, the session will NOT automatically refresh our objects, so ALWAYS call
that refresh-method explicitely if you need it in your current situation. NEVER
rely on the behaviour you observe while using the debugger. (I guess this sort
of "auto-refresh" happens because the debugging-tools already inspect the
attributes of our mapped objects so this way maybe there are already some calls
to the session we do not see ourselves but just the mighty debugger...)

However, fun fact number two: Never get confused with your current session-
situation because of any context-manager: When using sessions, we will usually
make use of Pythons context-managers to automatically close them. Even worse,
we want to use an own implementation of the Unit-of-work-pattern, which again
is implemented with a Python-context-manager. We do that because it has many
benefits for us. However, especially with context-managers indentation counts!
Always be sure that you understand at which level of indentation you are and
which "stepping left" in indentation levels has which effect on your session! It
is very easy to oversee that moving an indentation-level back to the left might
just have rolled-back your session or closed it or what so ever! Always be care-
ful when using context-managers and be very critical about understanding your
current level of indentation there.
