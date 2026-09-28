from app.database import get_recent_telemetry
from app.anomaly import AnomalyDetector


class ServerHealthAnalyzer:
    def __init__(self):
        self.anomaly_detector = AnomalyDetector()

    def analyze(self, limit=50):
        records = get_recent_telemetry(limit)

        if not records:
            return {
                "status": "no_data",
                "health": "unknown",
                "timestamp": None,
                "records_analyzed": 0,
                "event_count": 0,
                "events": [],
            }

        latest = records[0]

        active_conditions = self.anomaly_detector.detect_current_conditions(
            latest
        )

        critical_conditions = [
            condition
            for condition in active_conditions
            if condition["severity"] == "critical"
        ]

        warning_conditions = [
            condition
            for condition in active_conditions
            if condition["severity"] == "warning"
        ]

        if critical_conditions:
            health = "critical"
        elif warning_conditions:
            health = "warning"
        else:
            health = "normal"

        historical_events = []

        for record in records:
            cpu_temperature = record.get("cpu_temperature_celsius")
            exhaust_temperature = record.get("exhaust_temperature_celsius")
            cpu_power = record.get("cpu_power_watts")
            total_power = record.get("total_power_watts")
            fan_speed = record.get("fan_speed_percent")
            battery_health = record.get("battery_state_of_health")

            if (
                cpu_temperature is not None
                and exhaust_temperature is not None
                and cpu_temperature > 80
                and exhaust_temperature > 70
            ):
                historical_events.append({
                    "type": "THERMAL_STRESS",
                    "severity": "critical",
                    "timestamp": record["timestamp"],
                    "message": "CPU and exhaust temperatures are elevated",
                    "metrics": {
                        "cpu_temperature_celsius": cpu_temperature,
                        "exhaust_temperature_celsius": exhaust_temperature,
                    },
                })

            if (
                cpu_power is not None
                and total_power is not None
                and cpu_power > 200
                and total_power > 1000
            ):
                historical_events.append({
                    "type": "POWER_STRESS",
                    "severity": "critical",
                    "timestamp": record["timestamp"],
                    "message": "CPU and total system power consumption are elevated",
                    "metrics": {
                        "cpu_power_watts": cpu_power,
                        "total_power_watts": total_power,
                    },
                })

            if fan_speed is not None and fan_speed > 95:
                historical_events.append({
                    "type": "COOLING_STRESS",
                    "severity": "critical",
                    "timestamp": record["timestamp"],
                    "message": "Fan speed is approaching maximum capacity",
                    "metrics": {
                        "fan_speed_percent": fan_speed,
                    },
                })

            if battery_health is not None and battery_health < 80:
                historical_events.append({
                    "type": "BATTERY_DEGRADATION",
                    "severity": "warning",
                    "timestamp": record["timestamp"],
                    "message": "Battery state of health is below the configured threshold",
                    "metrics": {
                        "battery_state_of_health": battery_health,
                    },
                })

        unique_events = []
        seen = set()

        for event in historical_events:
            key = (
                event["type"],
                event["timestamp"],
                tuple(sorted(event["metrics"].items())),
            )

            if key not in seen:
                seen.add(key)
                unique_events.append(event)

        return {
            "status": "events_detected" if unique_events else "normal",
            "health": health,
            "timestamp": latest["timestamp"],
            "records_analyzed": len(records),
            "active_condition_count": len(active_conditions),
            "active_conditions": active_conditions,
            "event_count": len(unique_events),
            "events": unique_events,
        }