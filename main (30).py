import sqlite3
import re
import time

POSITIVE = {
    "good", "clean", "fast", "helpful", "improved"
}

NEGATIVE = {
    "bad", "dirty", "slow", "rude", "smoke", "broken"
}

NEGATORS = {
    "not", "never", "no"
}


def score(text):
    words = re.findall(r"\b[\w']+\b", text.lower())

    total = 0

    for index, word in enumerate(words):

        value = 0

        if word in POSITIVE:
            value = 1

        elif word in NEGATIVE:
            value = -1

        if index > 0 and words[index - 1] in NEGATORS:
            value = -value

        total += value

    return total


def label(text):
    result = score(text)

    if result > 0:
        return "positive"

    elif result < 0:
        return "negative"

    return "neutral"


def summarise(text):
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())

    frequency = {}

    for sentence in sentences:
        words = re.findall(r"\b\w+\b", sentence.lower())

        for word in words:
            if len(word) > 3:
                frequency[word] = frequency.get(word, 0) + 1

    ranked = []

    for sentence in sentences:
        words = re.findall(r"\b\w+\b", sentence.lower())

        importance = sum(
            frequency.get(word, 0)
            for word in words
        )

        ranked.append((importance, sentence))

    ranked.sort(reverse=True)

    return " ".join(
        sentence for importance, sentence in ranked[:2]
    )


complaints = [
    "The roads are clean and the buses are fast.",
    "Smoke from the factory makes the air bad.",
    "The staff were not helpful.",
    "The water supply is dirty and broken.",
    "The roads have improved.",
    "The garbage collection is slow.",
    "The air is clean and good.",
    "The transport service is bad.",
    "The workers are helpful.",
    "There is smoke near the school.",
    "The roads are broken.",
    "The bus service is fast and good.",
    "The water is dirty.",
    "The staff are rude.",
    "The environment has improved.",
    "The street lights are broken.",
    "The air quality is bad.",
    "The roads are clean.",
    "The service is not good.",
    "The garbage collection is helpful.",
    "The traffic is slow.",
    "The factory produces smoke.",
    "The water supply is good.",
    "The workers are not rude.",
    "The public transport is improved.",
    "The drainage system is broken.",
    "The road is dirty.",
    "The buses are not fast.",
    "The service is helpful.",
    "The environment is clean.",
    "The air is not clean.",
    "The water supply is improved.",
    "The factory smoke is bad.",
    "The roads are good.",
    "The transport is slow.",
    "The workers are helpful.",
    "The street is dirty.",
    "The buses are broken.",
    "The service is not bad.",
    "The environment is improved.",
    "The garbage is dirty.",
    "The air is good.",
    "The staff are not helpful.",
    "The roads are fast.",
    "The water is clean.",
    "The drainage is broken.",
    "The transport service is helpful.",
    "The factory smoke is harmful.",
    "The roads are not bad.",
    "The environment is dirty."
]


print("SENTIMENT ANALYSIS")

for complaint in complaints:
    print(label(complaint), "|", complaint)


print("\nSUMMARIES")

for complaint in complaints[:10]:
    print(summarise(complaint))


print("\nAGREEMENT TEST")

correct_labels = [
    "positive", "negative", "negative", "negative", "positive",
    "negative", "positive", "negative", "positive", "negative",
    "negative", "positive", "negative", "negative", "positive",
    "negative", "negative", "positive", "negative", "positive",
    "negative", "negative", "positive", "positive", "positive",
    "negative", "negative", "negative", "positive", "positive",
    "negative", "positive", "negative", "positive", "negative",
    "positive", "negative", "negative", "positive", "positive",
    "negative", "positive", "negative", "positive", "positive",
    "negative", "positive", "negative", "positive", "negative"
]

agree = 0

for complaint, expected in zip(complaints, correct_labels):
    if label(complaint) == expected:
        agree += 1

print("Total Complaints:", len(complaints))
print("Agreements:", agree)
print("Agreement Percentage:", round(agree / len(complaints) * 100, 2))


print("\nDATABASE INDEX TEST")

con = sqlite3.connect(":memory:")

con.execute("""
CREATE TABLE readings(
station TEXT,
day TEXT,
pm25 REAL
)
""")

data = []

for station_number in range(100):
    station = f"Station{station_number + 1}"

    for day_number in range(365):
        day = f"2026-{day_number + 1}"

        for hour in range(24):
            value = 30 + (station_number + day_number + hour) % 100
            data.append((station, day, value))

con.executemany(
    "INSERT INTO readings VALUES(?,?,?)",
    data
)

con.commit()


def run_query():
    return con.execute("""
    SELECT AVG(pm25)
    FROM readings
    WHERE station=? AND day=?
    """, ("Station50", "2026-100")).fetchone()


start = time.perf_counter()

for i in range(100):
    run_query()

before = time.perf_counter() - start

con.execute("""
CREATE INDEX idx_station_day
ON readings(station, day)
""")

con.commit()

start = time.perf_counter()

for i in range(100):
    run_query()

after = time.perf_counter() - start

print("Before Index:", round(before, 5))
print("After Index:", round(after, 5))

print("\nDATABASE RECORD COUNT")

print(con.execute(
    "SELECT COUNT(*) FROM readings"
).fetchone())

print("\nSTATION-WISE AVERAGES")

for row in con.execute("""
SELECT station, AVG(pm25)
FROM readings
GROUP BY station
LIMIT 10
"""):
    print(row)

con.close()