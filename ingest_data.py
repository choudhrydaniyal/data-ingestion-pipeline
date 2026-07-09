import click
import pandas as pd
from sqlalchemy import create_engine
from tqdm.auto import tqdm

dtype = {
    "VendorID": "Int64",
    "passenger_count": "Int64",
    "trip_distance": "float64",
    "RatecodeID": "Int64",
    "store_and_fwd_flag": "string",
    "PULocationID": "Int64",
    "DOLocationID": "Int64",
    "payment_type": "Int64",
    "fare_amount": "float64",
    "extra": "float64",
    "mta_tax": "float64",
    "tip_amount": "float64",
    "tolls_amount": "float64",
    "improvement_surcharge": "float64",
    "total_amount": "float64",
    "congestion_surcharge": "float64"
}

parse_dates = [
    "tpep_pickup_datetime",
    "tpep_dropoff_datetime"
]

@click.command()
@click.option("--pg-user", default="root", show_default=True, help="Postgres username")
@click.option("--pg-password", default="root", show_default=True, help="Postgres password")
@click.option("--pg-host", default="localhost", show_default=True, help="Postgres host")
@click.option("--pg-port", default="5432", show_default=True, help="Postgres port")
@click.option("--pg-db", default="ny_taxi", show_default=True, help="Postgres database name")
@click.option("--chunk-size", default=100000, show_default=True, type=int, help="Number of rows per chunk")
@click.option("--year", default=2021, show_default=True, type=int, help="Data year")
@click.option("--month", default=1, show_default=True, type=int, help="Data month")
@click.option("--table-name", default="yellow_taxi_data", show_default=True, help="Destination table name")
def run(
    pg_user,
    pg_password,
    pg_host,
    pg_port,
    pg_db,
    chunk_size,
    year,
    month,
    table_name,
):

    engine = create_engine(f"postgresql://{pg_user}:{pg_password}@{pg_host}:{pg_port}/{pg_db}")

    prefix = "https://github.com/DataTalksClub/nyc-tlc-data/releases/download/yellow"
    url = f"{prefix}/yellow_tripdata_{year}-{month:02d}.csv.gz"


    print(f"Downloading and ingesting data from {url} in chunks of {chunk_size} rows...")

    df_iter = pd.read_csv(
        url,
        dtype=dtype,
        parse_dates=parse_dates,
        iterator=True,
        chunksize=chunk_size,
    )

    print(f"Successfully downloaded data from {url}. Beginning ingestion into the database...")
    print("Inserting data into the database...")

    first = True
    for df_chunk in tqdm(df_iter):
        if first:
            df_chunk.head(0).to_sql(name=table_name, con=engine, if_exists="replace")
            first = False
        df_chunk.to_sql(name=table_name, con=engine, if_exists="append")

    print("Data ingestion completed successfully.")


if __name__ == "__main__":
    run()
