from google.cloud import spanner
import time


def query_person(instance_id, database_id):
    """Queries sample data from the database using SQL."""
    spanner_client = spanner.Client()
    instance = spanner_client.instance(instance_id)
    database = instance.database(database_id)

    with database.snapshot() as snapshot:
        results = snapshot.execute_sql(
            "SELECT * FROM person"
        )
        # for row in results:
        #     print(u"id: {}, first_name: {}, last_name: {}, email: {}, gender: {}, "
        #           u"date_of_birth: {}, country_of_birth: {}".format(*row))


while True:
    start = time.time()
    query_person("pko-database-mewa", "mewa")
    query_person("pko-database-mewa", "mewa")
    query_person("pko-database-mewa", "mewa")
    query_person("pko-database-mewa", "mewa")
    query_person("pko-database-mewa", "mewa")
    query_person("pko-database-mewa", "mewa")
    end = time.time()
    print("Response time: ", end - start)


