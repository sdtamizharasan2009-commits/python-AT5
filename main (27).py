import csv
import io
import sqlite3
import matplotlib.pyplot as plt

data = """station,date,pm25,temperature
Adyar,2026-10-01,48,30
Adyar,2026-10-02,NA,31
Adyar,2026-10-03,,29
Guindy,2026-10-01,95,32
Guindy,2026-10-02,-5,33
Guindy,2026-10-03,121,34
Adyar,2026-10-04,1000,30
Guindy,2026-10-04,80,31
"""

def load_clean(text):
    rows = []
    reader = csv.DictReader(io.StringIO(text))

    for row in reader:
        try:
            value = row["pm25"].strip()

            if value == "" or value == "NA":
                continue

            pm = float(value)

            if pm < 0 or pm > 999:
                continue

            rows.append((
                row["station"].strip().title(),
                row["date"].strip(),
                pm,
                float(row["temperature"])
            ))
        except (ValueError, KeyError):
            continue

    return rows


def min_max(values):
    minimum = min(values)
    maximum = max(values)

    if maximum == minimum:
        return [0.0 for value in values]

    return [round((value - minimum) / (maximum - minimum), 3)
            for value in values]


print("INPUT DATA")
print(data)

clean = load_clean(data)

print("\nCLEANED DATA")
for row in clean:
    print(row)

print("\nNORMALISED VALUES")
print(min_max([row[2] for row in clean]))

con = sqlite3.connect(":memory:")

con.execute("""
CREATE TABLE readings(
station TEXT,
day TEXT,
pm25 REAL,
temperature REAL
)
""")

con.executemany(
    "INSERT INTO readings VALUES(?,?,?,?)",
    clean
)

con.commit()

print("\nSQL QUERIES")

print("Adyar Average:",
      con.execute("SELECT AVG(pm25) FROM readings WHERE station='Adyar'").fetchone())

print("Maximum PM2.5:",
      con.execute("SELECT MAX(pm25) FROM readings").fetchone())

print("Station Average:")
for row in con.execute("SELECT station, AVG(pm25) FROM readings GROUP BY station"):
    print(row)

print("\nDAILY SUMMARY")

for row in con.execute("""
SELECT station, day, MIN(pm25), MAX(pm25),
AVG(pm25), COUNT(pm25)
FROM readings
GROUP BY station, day
"""):
    print(row)

plt.plot(
    [row[1] for row in clean if row[0] == "Adyar"],
    [row[2] for row in clean if row[0] == "Adyar"],
    marker="o",
    label="Adyar"
)

plt.plot(
    [row[1] for row in clean if row[0] == "Guindy"],
    [row[2] for row in clean if row[0] == "Guindy"],
    marker="o",
    label="Guindy"
)

plt.xlabel("Date")
plt.ylabel("PM2.5")
plt.title("Monthly PM2.5 Trend")
plt.legend()
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

stations = {}

for station, day, pm, temp in clean:
    stations.setdefault(station, []).append(pm)

plt.bar(stations.keys(), [sum(v)/len(v) for v in stations.values()])
plt.xlabel("Station")
plt.ylabel("Average PM2.5")
plt.title("Station Comparison")
plt.show()

plt.scatter(
    [row[3] for row in clean],
    [row[2] for row in clean]
)

plt.xlabel("Temperature")
plt.ylabel("PM2.5")
plt.title("Temperature vs PM2.5")
plt.show()

plt.hist([row[2] for row in clean])
plt.xlabel("PM2.5")
plt.ylabel("Frequency")
plt.title("PM2.5 Distribution")
plt.show()

con.close()