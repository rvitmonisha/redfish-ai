import random


class TelemetrySimulator:
    def __init__(self):
        self.mode = "normal"

    def set_mode(self, mode):
        if mode not in {"normal", "thermal", "power", "fan", "battery"}:
            raise ValueError("Invalid simulation mode")

        self.mode = mode

    def apply(self, data):
        if self.mode == "normal":
            return data

        if self.mode == "thermal":
            data["cpu_metrics"]["temperature_celsius"] = round(
                random.uniform(75, 95), 2
            )
            data["sensors"]["ExhaustTemp"] = round(
                random.uniform(65, 85), 2
            )

        elif self.mode == "power":
            data["cpu_metrics"]["power_watts"] = round(
                random.uniform(180, 260), 2
            )
            data["sensors"]["TotalPower"] = round(
                random.uniform(850, 1200), 2
            )

        elif self.mode == "fan":
            data["cpu_metrics"]["fan_speeds_percent"] = [
                {
                    "MemberId": "CPU #1 Fan Speed",
                    "Reading": round(random.uniform(92, 100), 2),
                }
            ]

        elif self.mode == "battery":
            data["sensors"]["Battery1StateOfHealth"] = round(
                random.uniform(60, 79), 2
            )

        return data