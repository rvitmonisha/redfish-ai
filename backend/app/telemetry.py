from app.redfish_client import RedfishClient
from app.simulator import TelemetrySimulator


class TelemetryCollector:
    def __init__(self):
        self.client = RedfishClient()
        self.simulator = TelemetrySimulator()

    def set_simulation_mode(self, mode):
        self.simulator.set_mode(mode)

    def collect(self):
        systems = self.client.get_systems()
        system_members = systems.get("Members", [])

        if not system_members:
            raise RuntimeError("No Redfish systems found")

        system_uri = system_members[0]["@odata.id"]
        system = self.client.get(system_uri)

        processors_uri = system["Processors"]["@odata.id"]
        processors = self.client.get(processors_uri)
        processor_members = processors.get("Members", [])

        cpu_uri = None

        for processor in processor_members:
            processor_data = self.client.get(processor["@odata.id"])

            if processor_data.get("ProcessorType") == "CPU":
                cpu_uri = processor["@odata.id"]
                break

        if not cpu_uri:
            raise RuntimeError("No CPU processor found")

        cpu = self.client.get(cpu_uri)

        metrics_uri = cpu.get("EnvironmentMetrics", {}).get("@odata.id")
        cpu_metrics = self.client.get(metrics_uri) if metrics_uri else {}

        chassis_uri = system.get("Links", {}).get("Chassis", [{}])[0].get(
            "@odata.id"
        )

        chassis = self.client.get(chassis_uri) if chassis_uri else {}

        sensors_uri = chassis.get("Sensors", {}).get("@odata.id")
        sensors = self.client.get(sensors_uri) if sensors_uri else {}

        selected_sensors = {
            "AmbientTemp": None,
            "IntakeTemp": None,
            "ExhaustTemp": None,
            "TotalPower": None,
            "PS1InputPower": None,
            "PS2InputPower": None,
            "Battery1Temp": None,
            "Battery1StateOfHealth": None,
        }

        for sensor in sensors.get("Members", []):
            sensor_uri = sensor.get("@odata.id")

            if not sensor_uri:
                continue

            sensor_name = sensor_uri.rsplit("/", 1)[-1]

            if sensor_name in selected_sensors:
                sensor_data = self.client.get(sensor_uri)
                selected_sensors[sensor_name] = sensor_data.get("Reading")

        data = {
            "system": {
                "id": system.get("Id"),
                "name": system.get("Name"),
                "hostname": system.get("HostName"),
                "manufacturer": system.get("Manufacturer"),
                "model": system.get("Model"),
                "power_state": system.get("PowerState"),
                "health": system.get("Status", {}).get("Health"),
                "memory_gib": system.get("MemorySummary", {}).get(
                    "TotalSystemMemoryGiB"
                ),
                "processor_count": system.get("ProcessorSummary", {}).get("Count"),
                "core_count": system.get("ProcessorSummary", {}).get("CoreCount"),
                "logical_processor_count": system.get(
                    "ProcessorSummary", {}
                ).get("LogicalProcessorCount"),
            },
            "cpu": {
                "id": cpu.get("Id"),
                "manufacturer": cpu.get("Manufacturer"),
                "model": cpu.get("Model"),
                "operating_speed_mhz": cpu.get("OperatingSpeedMHz"),
                "max_speed_mhz": cpu.get("MaxSpeedMHz"),
                "cores": cpu.get("TotalCores"),
                "threads": cpu.get("TotalThreads"),
                "health": cpu.get("Status", {}).get("Health"),
            },
            "cpu_metrics": {
                "temperature_celsius": cpu_metrics.get(
                    "TemperatureCelsius", {}
                ).get("Reading"),
                "power_watts": cpu_metrics.get("PowerWatts", {}).get("Reading"),
                "fan_speeds_percent": cpu_metrics.get("FanSpeedsPercent", []),
            },
            "sensors": selected_sensors,
            "sensor_count": sensors.get("Members@odata.count", 0),
        }

        return self.simulator.apply(data)