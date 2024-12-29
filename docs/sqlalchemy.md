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

## Setting up connectivity with an Engine


