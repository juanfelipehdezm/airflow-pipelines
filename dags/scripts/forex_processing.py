from pyspark.sql.context import SQLContext
from pyspark.sql.session import SparkSession
from pyspark.sql.types import (DoubleType, StringType, StructField, StructType,
                               TimestampType)

# creating the spark session
spark = SparkSession.builder.appName("Forex rates processing").getOrCreate()
sqlcontext = SQLContext(spark)

# schema to be used
schema_ratings = StructType([
    StructField("1. From_Currency Code", StringType(), False),
    StructField("2. From_Currency Name", StringType(), False),
    StructField("3. To_Currency Code", StringType(), False),
    StructField("4. To_Currency Name", StringType(), False),
    StructField("5. Exchange Rate", DoubleType(), False),
    StructField("6. Last Refreshed", TimestampType(), False),
    StructField("7. Time Zone", StringType(), False),
    StructField("8. Bid Price", DoubleType(),False),
    StructField("9. Ask Price",DoubleType(),False)
])

# reading json file
rates_df = spark.read.schema(schema=schema_ratings).json(
    "G://My Drive//Big Data//Airflow-pipelines//dags//files//rates.json")

rates_df.printSchema()
rates_df.show(1)
