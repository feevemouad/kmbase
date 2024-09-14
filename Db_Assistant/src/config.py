SELECTED_DBS = ["postgresql", "oracle", "mysql"]

class Config:
    def __init__(self, database_type: str, database_url: str, llm):
        # Validate database type
        if database_type.lower() not in SELECTED_DBS:
            raise Exception(
                f"Selected DB {database_type} not recognized. The possible values are: {SELECTED_DBS}."
            )
        
        self.selected_db = database_type
        self.db_uri = self.get_connection_string(database_type, database_url)
        self.llm = llm
        
    def get_connection_string(self, db_type: str, db_url: str) -> str:
        # Split the URL by '//' and take the last part
        url_parts = db_url.split('//')
        connection_details = url_parts[-1]

        if db_type.lower() == "oracle":
            return f"oracle+cx_oracle://{connection_details}"
        elif db_type.lower() == "mysql":
            return f"mysql+pymysql://{connection_details}"
        elif db_type.lower() == "postgresql":
            return f"postgresql://{connection_details}"
        else:
            raise ValueError("Unsupported database type")


