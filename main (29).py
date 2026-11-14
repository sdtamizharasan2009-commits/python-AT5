import csv
import sqlite3
import time
import cProfile
import statistics
import os

try:
    import pandas as pd
except ImportError:
    pd = None


def generate_data(station_count):
    filename = f"data_{station_count}.csv"

    with open(filename, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["station", "day", "pm25"])

        for station_number in range(station_count):
            station = f"Station{station_number + 1}"

            for day_number in range(365):
                day = f"2026-{day_number + 1}"

                for hour in range(24):
                    value = 30 + (station_number + day_number + hour) % 100
                    writer.writerow([station, day, value])

    return filename


def python_loops(filename):
    values = {}

    with open(filename, "r") as file:
        reader = csv.DictReader(file)

        for row in reader:
            key = (row["station"], row["day"])

            if key not in values:
                values[key] = []

            values[key].append(float(row["pm25"]))

    result = {}

    for key, numbers in values.items():
        result[key] = statistics.mean(numbers)

    return result


def pandas_method(filename):
    if pd is None:
        raise ImportError("Install pandas to run this method")

    data = pd.read_csv(filename)

    return data.groupby(
        ["station", "day"]
    )["pm25"].mean().to_dict()


def sql_method(filename):
    con = sqlite3.connect(":memory:")

    con.execute("""
    CREATE TABLE readings(
    station TEXT,
    day TEXT,
    pm25 REAL
    )
    """)

    with open(filename, "r") as file:
        reader = csv.reader(file)
        next(reader)

        con.executemany(
            "INSERT INTO readings VALUES(?,?,?)",
            reader
        )

    result = con.execute("""
    SELECT station, day, AVG(pm25)
    FROM readings
    GROUP BY station, day
    """).fetchall()

    con.close()

    return {
        (row[0], row[1]): row[2]
        for row in result
    }


for count in [1, 12, 120]:

    print("\nSTATIONS:", count)

    filename = generate_data(count)

    start = time.perf_counter()
    loop_result = python_loops(filename)
    loop_time = time.perf_counter() - start

    start = time.perf_counter()
    sql_result = sql_method(filename)
    sql_time = time.perf_counter() - start

    print("Python Loop Time:", round(loop_time, 4))
    print("SQL Time:", round(sql_time, 4))

    print("Python and SQL Match:", all(
        abs(loop_result[key] - sql_result[key]) < 0.000001
        for key in loop_result
    ))

    if pd is not None:
        start = time.perf_counter()
        pandas_result = pandas_method(filename)
        pandas_time = time.perf_counter() - start

        print("Pandas Time:", round(pandas_time, 4))

        print("Python and Pandas Match:", all(
            abs(loop_result[key] - pandas_result[key]) < 0.000001
            for key in loop_result
        ))

    os.remove(filename)


print("\nPROFILING PYTHON LOOPS")

filename = generate_data(1)

profiler = cProfile.Profile()
profiler.enable()

python_loops(filename)

profiler.disable()
profiler.print_stats(sort="cumtime")

os.remove(filename)