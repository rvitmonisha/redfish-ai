from statistics import mean, stdev

from app.database import get_recent_telemetry


class PredictiveMaintenance:
    def __init__(self):
        self.metrics = {
            "cpu_temperature_celsius": {
                "name": "CPU Temperature",
                "unit": "°C",
                "warning_threshold": 70,
                "critical_threshold": 80,
                "higher_is_worse": True,
            },
            "cpu_power_watts": {
                "name": "CPU Power",
                "unit": "W",
                "warning_threshold": 150,
                "critical_threshold": 200,
                "higher_is_worse": True,
            },
            "exhaust_temperature_celsius": {
                "name": "Exhaust Temperature",
                "unit": "°C",
                "warning_threshold": 60,
                "critical_threshold": 70,
                "higher_is_worse": True,
            },
            "total_power_watts": {
                "name": "Total Power",
                "unit": "W",
                "warning_threshold": 800,
                "critical_threshold": 1000,
                "higher_is_worse": True,
            },
            "fan_speed_percent": {
                "name": "Fan Speed",
                "unit": "%",
                "warning_threshold": 85,
                "critical_threshold": 95,
                "higher_is_worse": True,
            },
            "battery_state_of_health": {
                "name": "Battery Health",
                "unit": "%",
                "warning_threshold": 80,
                "critical_threshold": 60,
                "higher_is_worse": False,
            },
        }

    def calculate_trend(self, values):
        if len(values) < 2:
            return 0

        return (values[-1] - values[0]) / (len(values) - 1)

    def calculate_risk_score(
        self,
        current_value,
        recent_average,
        trend,
        config,
    ):
        warning = config["warning_threshold"]
        critical = config["critical_threshold"]

        if config["higher_is_worse"]:
            if current_value >= critical:
                threshold_score = 100
            elif current_value >= warning:
                threshold_score = 60 + (
                    (current_value - warning)
                    / (critical - warning)
                ) * 40
            else:
                threshold_score = max(
                    0,
                    (current_value / warning) * 40,
                )

            trend_score = min(max(trend * 15, 0), 30)

            if recent_average >= critical:
                average_score = 100
            elif recent_average >= warning:
                average_score = 60 + (
                    (recent_average - warning)
                    / (critical - warning)
                ) * 40
            else:
                average_score = (
                    recent_average / warning
                ) * 40

        else:
            if current_value <= critical:
                threshold_score = 100
            elif current_value <= warning:
                threshold_score = 60 + (
                    (warning - current_value)
                    / (warning - critical)
                ) * 40
            else:
                threshold_score = max(
                    0,
                    ((100 - current_value) / 20) * 40,
                )

            trend_score = min(max(-trend * 15, 0), 30)

            if recent_average <= critical:
                average_score = 100
            elif recent_average <= warning:
                average_score = 60 + (
                    (warning - recent_average)
                    / (warning - critical)
                ) * 40
            else:
                average_score = (
                    max(0, 100 - recent_average) / 20
                ) * 40

        score = (
            threshold_score * 0.5
            + average_score * 0.3
            + trend_score * 0.2
        )

        return round(min(max(score, 0), 100), 2)

    def get_risk(self, score):
        if score >= 80:
            return "critical"

        if score >= 60:
            return "high"

        if score >= 30:
            return "warning"

        return "normal"

    def generate_prediction(
        self,
        metric,
        current_value,
        recent_average,
        trend,
        risk,
        config,
    ):
        if metric == "battery_state_of_health":
            if trend < -0.5:
                return "Battery health is degrading."

            if current_value < config["warning_threshold"]:
                return "Battery health is below the recommended level."

            return "Battery health is stable."

        if trend > 1:
            return f"{config['name']} is trending upward."

        if trend < -1:
            return f"{config['name']} is trending downward."

        if current_value >= config["critical_threshold"]:
            return f"{config['name']} is currently at a critical level."

        if recent_average >= config["warning_threshold"]:
            return f"{config['name']} remains elevated."

        return f"{config['name']} is stable."

    def generate_recommendation(
        self,
        metric,
        risk,
        trend,
        current_value,
    ):
        if risk == "normal":
            return "No immediate maintenance action required."

        recommendations = {
            "cpu_temperature_celsius": (
                "Inspect cooling airflow, fans and heatsink condition."
            ),
            "cpu_power_watts": (
                "Inspect CPU workload and verify power delivery."
            ),
            "exhaust_temperature_celsius": (
                "Inspect chassis airflow and cooling system."
            ),
            "total_power_watts": (
                "Inspect PSU load and overall server power consumption."
            ),
            "fan_speed_percent": (
                "Inspect fans, airflow and cooling system condition."
            ),
            "battery_state_of_health": (
                "Inspect the backup battery and consider replacement."
            ),
        }

        if trend > 1 or (
            metric == "battery_state_of_health"
            and trend < -0.5
        ):
            return recommendations.get(
                metric,
                "Schedule hardware inspection.",
            )

        if current_value is not None:
            return recommendations.get(
                metric,
                "Schedule hardware inspection.",
            )

        return "Schedule hardware inspection."

    def analyze_metric(self, records, metric, config):
        values = [
            record.get(metric)
            for record in reversed(records)
            if record.get(metric) is not None
        ]

        if len(values) < 10:
            return None

        current_value = values[-1]

        recent_values = values[-10:]
        baseline_values = values[:-10]

        recent_average = mean(recent_values)

        baseline_average = (
            mean(baseline_values)
            if baseline_values
            else recent_average
        )

        trend = self.calculate_trend(recent_values)

        recent_change = (
            recent_values[-1] - recent_values[0]
        )

        score = self.calculate_risk_score(
            current_value,
            recent_average,
            trend,
            config,
        )

        risk = self.get_risk(score)

        prediction = self.generate_prediction(
            metric,
            current_value,
            recent_average,
            trend,
            risk,
            config,
        )

        recommendation = self.generate_recommendation(
            metric,
            risk,
            trend,
            current_value,
        )

        historical_std = (
            stdev(baseline_values)
            if len(baseline_values) >= 2
            else 0
        )

        return {
            "metric": metric,
            "name": config["name"],
            "unit": config["unit"],
            "current_value": round(current_value, 2),
            "recent_average": round(recent_average, 2),
            "baseline_average": round(baseline_average, 2),
            "historical_std": round(historical_std, 2),
            "recent_change": round(recent_change, 2),
            "trend_per_sample": round(trend, 4),
            "risk_score": score,
            "risk": risk,
            "prediction": prediction,
            "recommendation": recommendation,
        }

    def analyze(self, limit=100):
        records = get_recent_telemetry(limit)

        if not records:
            return {
                "status": "no_data",
                "records_analyzed": 0,
                "metrics_analyzed": 0,
                "critical_predictions": 0,
                "high_predictions": 0,
                "warning_predictions": 0,
                "predictions": [],
            }

        predictions = []

        for metric, config in self.metrics.items():
            result = self.analyze_metric(
                records,
                metric,
                config,
            )

            if result:
                predictions.append(result)

        critical_count = sum(
            1
            for prediction in predictions
            if prediction["risk"] == "critical"
        )

        high_count = sum(
            1
            for prediction in predictions
            if prediction["risk"] == "high"
        )

        warning_count = sum(
            1
            for prediction in predictions
            if prediction["risk"] == "warning"
        )

        if critical_count:
            status = "critical"
        elif high_count:
            status = "high"
        elif warning_count:
            status = "warning"
        else:
            status = "normal"

        return {
            "status": status,
            "records_analyzed": len(records),
            "metrics_analyzed": len(predictions),
            "critical_predictions": critical_count,
            "high_predictions": high_count,
            "warning_predictions": warning_count,
            "predictions": predictions,
        }