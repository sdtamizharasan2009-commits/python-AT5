import sqlite3
import csv
import io

readings = [
    ("Adyar", "2026-10-01", 48.0),
    ("Guindy", "2026-10-01", 95.0),
    ("Guindy", "2026-10-03", 121.0),
    ("Adyar", "2026-10-04", 60.0)
]

con = sqlite3.connect(":memory:")

con.execute("""
CREATE TABLE aq(
station TEXT,
day TEXT,
pm25 REAL
)
""")

con.executemany(
    "INSERT INTO aq VALUES(?,?,?)",
    readings
)

con.commit()


def station_average(name):
    result = con.execute(
        "SELECT AVG(pm25) FROM aq WHERE station=?",
        (name,)
    ).fetchone()

    return result[0]


print("INPUT READINGS")
for row in readings:
    print(row)

print("\nSTATION AVERAGES")
print("Adyar:", station_average("Adyar"))
print("Guindy:", station_average("Guindy"))

print("\nSQL INJECTION TEST")
print(station_average("Adyar' OR '1'='1"))

print("\nMISSING COLUMN TEST")

data = """station,pm25
Adyar,48
Guindy,95
"""

try:
    reader = csv.DictReader(io.StringIO(data))

    for row in reader:
        print(row["station"], row["date"])

except KeyError as error:
    print("Missing column:", error)

print("\nWRONG DELIMITER TEST")

data = """station;date;pm25
Adyar;2026-10-01;48
"""

reader = csv.DictReader(io.StringIO(data))

for row in reader:
    print(row)

print("\nEMPTY FILE TEST")

reader = csv.DictReader(io.StringIO(""))
print(list(reader))

print("\nENCODING TEST")

try:
    text = b"station,date,pm25\nAdyar,2026-10-01,48"
    print(text.decode("utf-8"))

except UnicodeDecodeError:
    print("Encoding error")

print("\nQUOTE CHARACTER TEST")
print(station_average("O'Brien"))

print("\nALL READINGS")

for row in con.execute("SELECT * FROM aq"):
    print(row)

con.close()