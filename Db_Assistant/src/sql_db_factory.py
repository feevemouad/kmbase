from langchain.sql_database import SQLDatabase

def sql_db_factory(cfg) -> SQLDatabase:
    if cfg.selected_db in ["postgresql", "oracle", "mysql"]:
        return SQLDatabase.from_uri(cfg.db_uri, view_support=True)
    else:
        raise Exception(f"Could not create sql database factory: {cfg.selected_db}")
