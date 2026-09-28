import sqlite3
from datetime import datetime, timezone

DATABASE_PATH = "telemetry.db"


def get_connection():
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():
    connection = get_connection()

    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS telemetry (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            system_id TEXT,
            cpu_id TEXT,
            cpu_temperature_celsius REAL,
            cpu_power_watts REAL,
            fan_speed_percent REAL,
            system_health TEXT,
            power_state TEXT,
            ambient_temperature_celsius REAL,
            intake_temperature_celsius REAL,
            exhaust_temperature_celsius REAL,
            total_power_watts REAL,
            psu1_input_power_watts REAL,
            psu2_input_power_watts REAL,
            battery_temperature_celsius REAL,
            battery_state_of_health REAL
        )
        """
    )

    columns = {
        "ambient_temperature_celsius": "REAL",
        "intake_temperature_celsius": "REAL",
        "exhaust_temperature_celsius": "REAL",
        "total_power_watts": "REAL",
        "psu1_input_power_watts": "REAL",
        "psu2_input_power_watts": "REAL",
        "battery_temperature_celsius": "REAL",
        "battery_state_of_health": "REAL",
    }

    existing_columns = {
        row["name"]
        for row in connection.execute("PRAGMA table_info(telemetry)").fetchall()
    }

    for column, data_type in columns.items():
        if column not in existing_columns:
            connection.execute(
                f"ALTER TABLE telemetry ADD COLUMN {column} {data_type}"
            )

    connection.commit()
    connection.close()


def save_telemetry(data):
    system = data["system"]
    cpu = data["cpu"]
    cpu_metrics = data["cpu_metrics"]
    sensors = data.get("sensors", {})

    fan_speed = None

    if cpu_metrics["fan_speeds_percent"]:
        fan_speed = cpu_metrics["fan_speeds_percent"][0].get("Reading")

    connection = get_connection()

    connection.execute(
        """
        INSERT INTO telemetry (
            timestamp,
            system_id,
            cpu_id,
            cpu_temperature_celsius,
            cpu_power_watts,
            fan_speed_percent,
            system_health,
            power_state,
            ambient_temperature_celsius,
            intake_temperature_celsius,
            exhaust_temperature_celsius,
            total_power_watts,
            psu1_input_power_watts,
            psu2_input_power_watts,
            battery_temperature_celsius,
            battery_state_of_health
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            datetime.now(timezone.utc).isoformat(),
            system["id"],
            cpu["id"],
            cpu_metrics["temperature_celsius"],
            cpu_metrics["power_watts"],
            fan_speed,
            system["health"],
            system["power_state"],
            sensors.get("AmbientTemp"),
            sensors.get("IntakeTemp"),
            sensors.get("ExhaustTemp"),
            sensors.get("TotalPower"),
            sensors.get("PS1InputPower"),
            sensors.get("PS2InputPower"),
            sensors.get("Battery1Temp"),
            sensors.get("Battery1StateOfHealth"),
        ),
    )

    connection.commit()
    connection.close()


def get_recent_telemetry(limit=100):
    connection = get_connection()

    rows = connection.execute(
        """
        SELECT *
        FROM telemetry
        ORDER BY id DESC
        LIMIT ?
        """,
        (limit,),
    ).fetchall()

    connection.close()

    return [dict(row) for row in rows]