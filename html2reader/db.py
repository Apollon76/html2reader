from pony.orm import Database, PrimaryKey, Required

db = Database()


class DbArticle(db.Entity):  # type: ignore
    id = PrimaryKey(int, auto=True)
    pocket_id = Required(str, unique=True, index=True)


class DbAttempt(db.Entity):  # type: ignore
    id = PrimaryKey(int, auto=True)
    pocket_id = Required(str, unique=True, index=True)
    number = Required(int, sql_default=0)