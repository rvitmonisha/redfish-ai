from statistics import mean, stdev

from app.database import get_recent_telemetry


class AnomalyDetector:
    def __init__(self):
        self.rules = {
            "cpu_temperature_celsius": {
                "threshold": 80,
                "direction": "high",
                "name": "CPU Temperature",
                "label": "Thermal Stress",
                "message": "CPU temperature is unusually high.",
                "severity": "critical",
            },
            "cpu_power_watts": {
                "threshold": 200,
                "direction": "high",
                "name": "CPU Power",
                "label": "CPU Power Stress",
                "message": "CPU power consumption is unusually high.",
                "severity": "critical",
            },
            "fan_speed_percent": {
                "threshold": 95,
                "direction": "high",
                "name": "Fan Speed",
                "label": "Cooling Stress",
                "message": "Fan speed is approaching maximum capacity.",
                "severity": "critical",
            },
            "exhaust_temperature_celsius": {
                "threshold": 70,
                "direction": "high",
                "name": "Exhaust Temperature",
                "label": "Exhaust Overheating",
                "message": "Exhaust temperature is unusually high.",
                "severity": "critical",
            },
            "total_power_watts": {
                "threshold": 1000,
                "direction": "high",
                "name": "Total Power",
                "label": "System Power Stress",
                "message": "Total server power consumption is elevated.",
                "severity": "critical",
            },
            "battery_state_of_health": {
                "threshold": 80,
                "direction": "low",
                "name": "Battery Health",
                "label": "Battery Degradation",
                "message": "Battery state of health is below the configured threshold.",
                "severity": "warning",
            },
        }

    def detect_current_conditions(self, latest):
        active_conditions = []

        for metric, rule in self.rules.items():
            value = latest.get(metric)

            if value is None:
                continue

            threshold = rule["threshold"]
            triggered = False

            if rule["direction"] == "high" and value > threshold:
                triggered = True

            if rule["direction"] == "low" and value < threshold:
                triggered = True

            if triggered:
                active_conditions.append({
                    "metric": metric,
                    "name": rule["name"],
                    "label": rule["label"],
                    "value": value,
                    "threshold": threshold,
                    "severity": rule["severity"],
                    "message": rule["message"],
                    "timestamp": latest["timestamp"],
                })

        return active_conditions

    def calculate_z_score(self, current_value, historical_values):
        if len(historical_values) < 5:
            return 0

        deviation = stdev(historical_values)

        if deviation == 0:
            return 0

        average = mean(historical_values)

        return abs(
            (current_value - average) / deviation
        )

    def calculate_anomaly_score(
        self,
        current_value,
        threshold,
        z_score,
        direction,
    ):
        if direction == "high":
            threshold_distance = (
                current_value - threshold
            )

            if threshold_distance <= 0:
                threshold_score = 0
            else:
                threshold_score = min(
                    threshold_distance / threshold * 100,
                    100,
                )

        else:
            threshold_distance = (
                threshold - current_value
            )

            if threshold_distance <= 0:
                threshold_score = 0
            else:
                threshold_score = min(
                    threshold_distance / threshold * 100,
                    100,
                )

        statistical_score = min(
            (z_score / 3) * 100,
            100,
        )

        score = (
            threshold_score * 0.6
            + statistical_score * 0.4
        )

        return round(min(score, 100), 2)

    def get_score_severity(self, score):
        if score >= 80:
            return "critical"

        if score >= 50:
            return "warning"

        return "normal"

    def detect_historical_anomalies(self, records):
        anomalies = []

        for index, record in enumerate(records):
            for metric, rule in self.rules.items():
                value = record.get(metric)

                if value is None:
                    continue

                threshold = rule["threshold"]

                threshold_triggered = (
                    rule["direction"] == "high"
                    and value > threshold
                ) or (
                    rule["direction"] == "low"
                    and value < threshold
                )

                historical_values = [
                    previous[metric]
                    for previous in records[index + 1:]
                    if previous.get(metric) is not None
                ]

                z_score = self.calculate_z_score(
                    value,
                    historical_values,
                )

                anomaly_score = self.calculate_anomaly_score(
                    value,
                    threshold,
                    z_score,
                    rule["direction"],
                )

                statistical_triggered = z_score >= 3

                if threshold_triggered or statistical_triggered:
                    severity = rule["severity"]

                    if statistical_triggered and not threshold_triggered:
                        severity = self.get_score_severity(
                            anomaly_score
                        )

                    anomalies.append({
                        "timestamp": record["timestamp"],
                        "metric": metric,
                        "name": rule["name"],
                        "value": value,
                        "threshold": threshold,
                        "z_score": round(z_score, 2),
                        "anomaly_score": anomaly_score,
                        "severity": severity,
                        "type": (
                            "threshold"
                            if threshold_triggered
                            else "historical"
                        ),
                        "message": (
                            f"{metric} exceeded the threshold"
                            if threshold_triggered
                            else f"{metric} significantly differs from historical behavior"
                        ),
                    })

        return anomalies

    def detect(self, limit=50):
        records = get_recent_telemetry(limit)

        if not records:
            return {
                "status": "no_data",
                "timestamp": None,
                "records_analyzed": 0,
                "active_condition_count": 0,
                "active_conditions": [],
                "anomaly_count": 0,
                "critical_count": 0,
                "warning_count": 0,
                "average_anomaly_score": 0,
                "max_anomaly_score": 0,
                "anomalies": [],
            }

        latest = records[0]

        active_conditions = self.detect_current_conditions(
            latest
        )

        anomalies = self.detect_historical_anomalies(
            records
        )

        critical_count = sum(
            1
            for anomaly in anomalies
            if anomaly["severity"] == "critical"
        )

        warning_count = sum(
            1
            for anomaly in anomalies
            if anomaly["severity"] == "warning"
        )

        scores = [
            anomaly["anomaly_score"]
            for anomaly in anomalies
        ]

        average_score = (
            round(mean(scores), 2)
            if scores
            else 0
        )

        max_score = (
            round(max(scores), 2)
            if scores
            else 0
        )

        return {
            "status": (
                "anomalies_detected"
                if anomalies
                else "normal"
            ),
            "timestamp": latest["timestamp"],
            "records_analyzed": len(records),
            "active_condition_count": len(active_conditions),
            "active_conditions": active_conditions,
            "anomaly_count": len(anomalies),
            "critical_count": critical_count,
            "warning_count": warning_count,
            "average_anomaly_score": average_score,
            "max_anomaly_score": max_score,
            "anomalies": anomalies,
        }