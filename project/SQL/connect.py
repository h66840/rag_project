from sqlalchemy import create_engine
from sqlalchemy import text


engine = create_engine("mysql+pymysql://root:200220lhy@localhost:3306/chikawaka")
print(engine)

# Test the connection
with engine.connect() as connection:


    # Wrap the SQL statement with text()
    result = connection.execute(text("SELECT * FROM course"))
    print(result.fetchone())  # Output: (1,)