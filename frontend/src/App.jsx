import { useEffect, useMemo, useState } from "react";

const API_BASE = "http://127.0.0.1:8000";

const simulationModes = [
  { id: "normal", label: "Normal" },
  { id: "thermal", label: "Thermal Stress" },
  { id: "power", label: "Power Stress" },
  { id: "fan", label: "Cooling Stress" },
  { id: "battery", label: "Battery Degradation" },
];

function formatNumber(value, decimals = 1) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) {
    return "—";
  }

  return Number(value).toFixed(decimals);
}

function formatInteger(value) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) {
    return "—";
  }

  return Number(value).toLocaleString();
}

function formatTime(value) {
  if (!value) {
    return "—";
  }

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return value;
  }

  return date.toLocaleString([], {
    day: "2-digit",
    month: "short",
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  });
}

function formatShortTime(value) {
  if (!value) {
    return "—";
  }

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return value;
  }

  return date.toLocaleTimeString([], {
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  });
}

function displayMetric(metric) {
  const names = {
    cpu_temperature_celsius: "CPU Temperature",
    cpu_power_watts: "CPU Power",
    fan_speed_percent: "Fan Speed",
    exhaust_temperature_celsius: "Exhaust Temperature",
    total_power_watts: "Total Power",
    battery_state_of_health: "Battery Health",
  };

  return names[metric] || metric?.replaceAll("_", " ") || "Unknown Metric";
}

function metricUnit(metric) {
  const units = {
    cpu_temperature_celsius: "°C",
    cpu_power_watts: "W",
    fan_speed_percent: "%",
    exhaust_temperature_celsius: "°C",
    total_power_watts: "W",
    battery_state_of_health: "%",
  };

  return units[metric] || "";
}

function normalizeStatus(status) {
  if (!status) {
    return "unknown";
  }

  return String(status).toLowerCase();
}

function StatusBadge({ status }) {
  const normalized = normalizeStatus(status);
  const cssStatus = normalized === "high" ? "warning" : normalized;

  return (
    <span className={`status-badge ${cssStatus}`}>
      {normalized.toUpperCase()}
    </span>
  );
}

function PageTitle({ eyebrow, title, description }) {
  return (
    <div className="page-intro">
      <div>
        <div className="eyebrow">{eyebrow}</div>
        <h1>{title}</h1>
        <p>{description}</p>
      </div>
    </div>
  );
}

function MetricCard({ label, value, unit, icon }) {
  return (
    <div className="metric-card">
      <div className="metric-icon">{icon}</div>
      <div className="metric-content">
        <span>{label}</span>
        <strong>{value}</strong>
        {unit && <small>{unit}</small>}
      </div>
    </div>
  );
}

function SummaryCard({ label, value, detail, icon }) {
  return (
    <div className="summary-card">
      <div className="summary-card-icon">{icon}</div>
      <div>
        <span>{label}</span>
        <strong>{value}</strong>
        {detail && <small>{detail}</small>}
      </div>
    </div>
  );
}

function ConditionCard({ condition }) {
  const title =
    condition.label ||
    condition.name ||
    condition.title ||
    displayMetric(condition.metric);

  return (
    <div className="condition-card">
      <div className="condition-icon">
        !
      </div>

      <div className="condition-events">
        <div className="condition-title">
          <strong>{title}</strong>
          <StatusBadge status={condition.severity} />
        </div>

        <div className="condition-message">
          {condition.message || "An abnormal condition has been detected."}
        </div>

        <div className="condition-value">
          {formatNumber(condition.value)}
          {condition.metric && ` ${metricUnit(condition.metric)}`}
          {condition.threshold !== undefined &&
            condition.threshold !== null &&
            ` · Threshold ${formatNumber(condition.threshold)}`}
        </div>
      </div>
    </div>
  );
}

function EventRow({ event }) {
  const eventType =
    event.type === "historical"
      ? "Historical anomaly"
      : event.type === "threshold"
        ? "Threshold violation"
        : event.type || "Anomaly event";

  return (
    <div className="timeline-event">
      <div className="timeline-marker" />

      <div className="timeline-event-content">
        <div className="timeline-title">
          <strong>{displayMetric(event.metric)}</strong>
          <StatusBadge status={event.severity} />
        </div>

        <div className="timeline-time">
          {formatTime(event.timestamp)} · {eventType}
        </div>

        <div className="timeline-description">
          {event.message}
        </div>

        <div className="timeline-value">
          Value: {formatNumber(event.value)} {metricUnit(event.metric)}
          {event.anomaly_score !== undefined &&
            ` · AI Score: ${formatNumber(event.anomaly_score)}`}
          {event.z_score !== undefined &&
            ` · Z-Score: ${formatNumber(event.z_score, 2)}`}
        </div>
      </div>
    </div>
  );
}

function DetailedAnomaly({ anomaly }) {
  return (
    <div className="detection-event">
      <div className="detection-icon">
        !
      </div>

      <div>
        <div className="detection-title">
          <strong>{displayMetric(anomaly.metric)}</strong>
          <StatusBadge status={anomaly.severity} />
        </div>

        <div className="detection-message">
          {anomaly.message}
        </div>

        <div className="detection-time">
          {formatTime(anomaly.timestamp)}
        </div>

        <div className="detection-value">
          Value: {formatNumber(anomaly.value)} {metricUnit(anomaly.metric)}
          {" · "}
          Threshold: {formatNumber(anomaly.threshold)} {metricUnit(anomaly.metric)}
          {" · "}
          AI Score: {formatNumber(anomaly.anomaly_score)}
          {" · "}
          Z-Score: {formatNumber(anomaly.z_score, 2)}
        </div>
      </div>
    </div>
  );
}

function PredictionCard({ prediction }) {
  return (
    <div className="prediction-card">
      <div className="prediction-header">
        <div>
          <strong>{prediction.name}</strong>
          <span>{prediction.metric}</span>
        </div>

        <StatusBadge status={prediction.risk} />
      </div>

      <div className="prediction-value">
        {formatNumber(prediction.current_value)}
        <small>{prediction.unit}</small>
      </div>

      <div className="prediction-grid-values">
        <div>
          <span>Risk Score</span>
          <strong>{formatNumber(prediction.risk_score)}</strong>
        </div>

        <div>
          <span>Recent Average</span>
          <strong>{formatNumber(prediction.recent_average)}</strong>
        </div>

        <div>
          <span>Baseline Average</span>
          <strong>{formatNumber(prediction.baseline_average)}</strong>
        </div>

        <div>
          <span>Historical Std</span>
          <strong>{formatNumber(prediction.historical_std)}</strong>
        </div>

        <div>
          <span>Recent Change</span>
          <strong>{formatNumber(prediction.recent_change)}</strong>
        </div>

        <div>
          <span>Trend / Sample</span>
          <strong>{formatNumber(prediction.trend_per_sample, 4)}</strong>
        </div>
      </div>

      <div className="prediction-message">
        <strong>Prediction</strong>
        <p>{prediction.prediction}</p>
      </div>

      <div className="prediction-message">
        <strong>Recommendation</strong>
        <p>{prediction.recommendation}</p>
      </div>
    </div>
  );
}

function HistoryChart({ records }) {
  const points = useMemo(() => {
    return [...records]
      .reverse()
      .slice(-24)
      .filter(
        (record) =>
          record.cpu_temperature_celsius !== null &&
          record.cpu_temperature_celsius !== undefined
      );
  }, [records]);

  if (!points.length) {
    return (
      <div className="empty-state">
        No historical telemetry available.
      </div>
    );
  }

  const values = points.map((point) =>
    Number(point.cpu_temperature_celsius)
  );

  const min = Math.min(...values);
  const max = Math.max(...values);
  const range = Math.max(max - min, 1);

  return (
    <div className="history-chart">
      <div className="chart-y-labels">
        <span>{formatNumber(max)}°C</span>
        <span>{formatNumber((max + min) / 2)}°C</span>
        <span>{formatNumber(min)}°C</span>
      </div>

      <div className="chart-area">
        <div className="chart-grid-line" />
        <div className="chart-grid-line" />
        <div className="chart-grid-line" />

        <div className="chart-bars">
          {points.map((point, index) => {
            const value = Number(point.cpu_temperature_celsius);
            const height = 12 + ((value - min) / range) * 88;

            return (
              <div className="chart-bar-wrapper" key={`${point.timestamp}-${index}`}>
                <div
                  className="chart-bar"
                  style={{ height: `${height}%` }}
                  title={`${formatNumber(value)}°C · ${formatShortTime(point.timestamp)}`}
                />
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}

function DistributionRow({ label, value, total }) {
  const percentage = total > 0 ? (value / total) * 100 : 0;

  return (
    <div className="distribution-row">
      <div className="distribution-header">
        <span>{label}</span>
        <strong>{value}</strong>
      </div>

      <div className="distribution-bar">
        <div
          className="distribution-fill"
          style={{ width: `${Math.min(percentage, 100)}%` }}
        />
      </div>

      <div className="distribution-meta">
        {formatNumber(percentage)}% of detected anomalies
      </div>
    </div>
  );
}

function SimulationPanel({ simulation, onChange }) {
  return (
    <div className="simulation-panel">
      <div>
        <div className="simulation-status">
          Simulation Mode: <strong>{simulation.toUpperCase()}</strong>
        </div>

        <div className="simulation-controls">
          {simulationModes.map((mode) => (
            <button
              key={mode.id}
              className={`simulation-button ${
                simulation === mode.id ? "active" : ""
              }`}
              onClick={() => onChange(mode.id)}
            >
              {mode.label}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}

function App() {
  const [page, setPage] = useState("dashboard");
  const [telemetry, setTelemetry] = useState(null);
  const [history, setHistory] = useState([]);
  const [anomalies, setAnomalies] = useState(null);
  const [health, setHealth] = useState(null);
  const [predictive, setPredictive] = useState(null);
  const [simulation, setSimulation] = useState("normal");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [lastUpdated, setLastUpdated] = useState(null);

  async function fetchJson(endpoint) {
    const response = await fetch(`${API_BASE}${endpoint}`);

    if (!response.ok) {
      const body = await response.text();
      throw new Error(body || `Request failed: ${response.status}`);
    }

    return response.json();
  }

  async function loadDashboard() {
    try {
      const [
        telemetryResponse,
        historyResponse,
        anomaliesResponse,
        healthResponse,
        predictiveResponse,
      ] = await Promise.all([
        fetchJson("/api/redfish/telemetry"),
        fetchJson("/api/redfish/monitoring/history?limit=100"),
        fetchJson("/api/redfish/monitoring/anomalies"),
        fetchJson("/api/redfish/monitoring/health"),
        fetchJson("/api/redfish/monitoring/predictive"),
      ]);

      setTelemetry(telemetryResponse);
      setHistory(historyResponse.data || []);
      setAnomalies(anomaliesResponse);
      setHealth(healthResponse);
      setPredictive(predictiveResponse);
      setLastUpdated(new Date());
      setError("");
    } catch (err) {
      setError(err.message || "Unable to connect to backend.");
    } finally {
      setLoading(false);
    }
  }

  async function changeSimulation(mode) {
    try {
      const response = await fetch(
        `${API_BASE}/api/redfish/monitoring/simulation`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            mode,
          }),
        }
      );

      if (!response.ok) {
        throw new Error("Unable to change simulation mode.");
      }

      setSimulation(mode);
      setLoading(true);
      await loadDashboard();
    } catch (err) {
      setError(err.message || "Unable to change simulation mode.");
    }
  }

  useEffect(() => {
    loadDashboard();

    const interval = setInterval(() => {
      loadDashboard();
    }, 10000);

    return () => clearInterval(interval);
  }, []);

  const system = telemetry?.system;
  const cpu = telemetry?.cpu;
  const cpuMetrics = telemetry?.cpu_metrics;
  const sensors = telemetry?.sensors;

  const currentHealth =
    health?.health ||
    normalizeStatus(system?.health || "unknown");

  const activeConditions = anomalies?.active_conditions || [];
  const activeConditionCount =
    anomalies?.active_condition_count ?? activeConditions.length;

  const anomalyCount = anomalies?.anomaly_count || 0;
  const criticalCount = anomalies?.critical_count || 0;
  const warningCount = anomalies?.warning_count || 0;
  const maxAnomalyScore = anomalies?.max_anomaly_score || 0;
  const averageAnomalyScore = anomalies?.average_anomaly_score || 0;

  const criticalPredictions = predictive?.critical_predictions || 0;
  const highPredictions = predictive?.high_predictions || 0;
  const warningPredictions = predictive?.warning_predictions || 0;

  const recentHistory = history.slice(0, 10);

  const pageDescription = {
    dashboard:
      "Real-time Redfish telemetry, hardware health and AI-powered monitoring.",
    anomalies:
      "AI-assisted anomaly detection across thermal, power, cooling and battery telemetry.",
    predictive:
      "Trend analysis and predictive maintenance signals derived from historical telemetry.",
  };

  if (loading && !telemetry) {
    return (
      <div className="loading-state">
        <strong>Redfish-AI</strong>
        <span>Connecting to monitoring services...</span>
      </div>
    );
  }

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-mark">R</div>
          <div>
            <strong>Redfish-AI</strong>
            <span>Server Intelligence</span>
          </div>
        </div>

        <nav>
          <button
            className={page === "dashboard" ? "active" : ""}
            onClick={() => setPage("dashboard")}
          >
            <span>▦</span>
            Dashboard
          </button>

          <button
            className={page === "anomalies" ? "active" : ""}
            onClick={() => setPage("anomalies")}
          >
            <span>△</span>
            Anomalies
            {activeConditionCount > 0 && (
              <b>{activeConditionCount}</b>
            )}
          </button>

          <button
            className={page === "predictive" ? "active" : ""}
            onClick={() => setPage("predictive")}
          >
            <span>◈</span>
            Predictive AI
          </button>
        </nav>

        <div className="sidebar-footer">
          <div>
            <span>Backend</span>
            <strong>FastAPI :8000</strong>
          </div>

          <div>
            <span>Redfish</span>
            <strong>Mock Server :5000</strong>
          </div>
        </div>
      </aside>

      <main className="main-content">
        <header className="topbar">
          <div>
            <span className="topbar-title">Infrastructure Monitoring</span>
            <span className="topbar-subtitle">
              DMTF Redfish telemetry platform
            </span>
          </div>

          <div className="topbar-status">
            <span className="status-dot" />
            <span>Live</span>
            <small>
              {lastUpdated
                ? `Updated ${formatShortTime(lastUpdated)}`
                : "Connecting"}
            </small>
          </div>
        </header>

        <section className="content">
          {error && (
            <div className="panel">
              <strong>Connection Error</strong>
              <p>{error}</p>
            </div>
          )}

          {page === "dashboard" && (
            <div className="page">
              <PageTitle
                eyebrow="SERVER MONITORING"
                title="Infrastructure Dashboard"
                description={pageDescription.dashboard}
              />

              <div className="hero-grid">
                <div className="health-hero">
                  <div className="health-status-card">
                    <div className="health-status-icon">✓</div>
                    <div>
                      <span>Server Health</span>
                      <strong>
                        {currentHealth.toUpperCase()}
                      </strong>
                      <small>
                        {health?.event_count || 0} historical events detected
                      </small>
                    </div>
                    <StatusBadge status={currentHealth} />
                  </div>
                </div>

                <div className="server-overview-card">
                  <div>
                    <span>Server</span>
                    <strong>
                      {system?.name || system?.hostname || system?.id || "Unknown"}
                    </strong>
                  </div>

                  <div>
                    <span>Manufacturer</span>
                    <strong>{system?.manufacturer || "—"}</strong>
                  </div>

                  <div>
                    <span>Model</span>
                    <strong>{system?.model || "—"}</strong>
                  </div>

                  <div>
                    <span>Power State</span>
                    <strong>{system?.power_state || "—"}</strong>
                  </div>
                </div>
              </div>

              <div className="summary-grid">
                <SummaryCard
                  label="Active Conditions"
                  value={activeConditionCount}
                  detail="Current telemetry"
                  icon="!"
                />

                <SummaryCard
                  label="AI Anomalies"
                  value={anomalyCount}
                  detail={`Max score ${formatNumber(maxAnomalyScore)}`}
                  icon="△"
                />

                <SummaryCard
                  label="Predictive Risk"
                  value={criticalPredictions + highPredictions}
                  detail={`${criticalPredictions} critical · ${highPredictions} high`}
                  icon="◈"
                />

                <SummaryCard
                  label="Telemetry Records"
                  value={history.length}
                  detail="Stored observations"
                  icon="⌁"
                />
              </div>

              <div className="dashboard-grid">
                <div className="panel">
                  <div className="panel-header">
                    <div>
                      <span>LIVE TELEMETRY</span>
                      <h2>Hardware Metrics</h2>
                    </div>
                  </div>

                  <div className="info-grid">
                    <MetricCard
                      label="CPU Temperature"
                      value={formatNumber(
                        cpuMetrics?.temperature_celsius
                      )}
                      unit="°C"
                      icon="°"
                    />

                    <MetricCard
                      label="CPU Power"
                      value={formatNumber(cpuMetrics?.power_watts)}
                      unit="W"
                      icon="P"
                    />

                    <MetricCard
                      label="Fan Speed"
                      value={formatNumber(
                        cpuMetrics?.fan_speeds_percent?.[0]?.Reading
                      )}
                      unit="%"
                      icon="F"
                    />

                    <MetricCard
                      label="Total Power"
                      value={formatNumber(sensors?.TotalPower)}
                      unit="W"
                      icon="W"
                    />
                  </div>
                </div>

                <div className="panel">
                  <div className="panel-header">
                    <div>
                      <span>CPU</span>
                      <h2>Processor Details</h2>
                    </div>
                  </div>

                  <div className="info-grid">
                    <MetricCard
                      label="Processor"
                      value={cpu?.model || "—"}
                      icon="C"
                    />

                    <MetricCard
                      label="Cores"
                      value={formatInteger(cpu?.cores)}
                      icon="8"
                    />

                    <MetricCard
                      label="Threads"
                      value={formatInteger(cpu?.threads)}
                      icon="T"
                    />

                    <MetricCard
                      label="Operating Speed"
                      value={formatInteger(cpu?.operating_speed_mhz)}
                      unit="MHz"
                      icon="S"
                    />
                  </div>
                </div>
              </div>

              <div className="dashboard-grid">
                <div className="panel">
                  <div className="panel-header">
                    <div>
                      <span>HISTORY</span>
                      <h2>CPU Temperature Trend</h2>
                    </div>
                  </div>

                  <HistoryChart records={history} />
                </div>

                <div className="panel">
                  <div className="panel-header">
                    <div>
                      <span>AI MONITOR</span>
                      <h2>Active Conditions</h2>
                    </div>
                    <strong>{activeConditionCount}</strong>
                  </div>

                  <div className="condition-list">
                    {activeConditions.length ? (
                      activeConditions
                        .slice(0, 4)
                        .map((condition, index) => (
                          <ConditionCard
                            key={`${condition.metric}-${index}`}
                            condition={condition}
                          />
                        ))
                    ) : (
                      <div className="empty-state">
                        No active abnormal conditions detected.
                      </div>
                    )}
                  </div>
                </div>
              </div>

              <div className="panel">
                <div className="panel-header">
                  <div>
                    <span>REDfish SENSOR DATA</span>
                    <h2>Environmental & Power Sensors</h2>
                  </div>
                </div>

                <div className="sensor-grid">
                  <MetricCard
                    label="Ambient"
                    value={formatNumber(sensors?.AmbientTemp)}
                    unit="°C"
                    icon="A"
                  />

                  <MetricCard
                    label="Intake"
                    value={formatNumber(sensors?.IntakeTemp)}
                    unit="°C"
                    icon="I"
                  />

                  <MetricCard
                    label="Exhaust"
                    value={formatNumber(sensors?.ExhaustTemp)}
                    unit="°C"
                    icon="E"
                  />

                  <MetricCard
                    label="PSU 1 Input"
                    value={formatNumber(sensors?.PS1InputPower)}
                    unit="W"
                    icon="1"
                  />

                  <MetricCard
                    label="PSU 2 Input"
                    value={formatNumber(sensors?.PS2InputPower)}
                    unit="W"
                    icon="2"
                  />

                  <MetricCard
                    label="Battery Temperature"
                    value={formatNumber(sensors?.Battery1Temp)}
                    unit="°C"
                    icon="B"
                  />

                  <MetricCard
                    label="Battery Health"
                    value={formatNumber(sensors?.Battery1StateOfHealth)}
                    unit="%"
                    icon="H"
                  />

                  <MetricCard
                    label="Sensor Count"
                    value={formatInteger(telemetry?.sensor_count)}
                    icon="#"
                  />
                </div>
              </div>
            </div>
          )}

          {page === "anomalies" && (
            <div className="page">
              <PageTitle
                eyebrow="AI DETECTION ENGINE"
                title="Anomaly Intelligence"
                description={pageDescription.anomalies}
              />

              <div className="anomaly-stat-grid">
                <div className="anomaly-stat">
                  <div className="anomaly-stat-icon">!</div>
                  <div>
                    <span className="anomaly-stat-label">
                      Active Conditions
                    </span>
                    <strong className="anomaly-stat-value">
                      {activeConditionCount}
                    </strong>
                  </div>
                </div>

                <div className="anomaly-stat">
                  <div className="anomaly-stat-icon">C</div>
                  <div>
                    <span className="anomaly-stat-label">
                      Critical Events
                    </span>
                    <strong className="anomaly-stat-value">
                      {criticalCount}
                    </strong>
                  </div>
                </div>

                <div className="anomaly-stat">
                  <div className="anomaly-stat-icon">W</div>
                  <div>
                    <span className="anomaly-stat-label">
                      Warning Events
                    </span>
                    <strong className="anomaly-stat-value">
                      {warningCount}
                    </strong>
                  </div>
                </div>

                <div className="anomaly-stat">
                  <div className="anomaly-stat-icon">AI</div>
                  <div>
                    <span className="anomaly-stat-label">
                      Max AI Score
                    </span>
                    <strong className="anomaly-stat-value">
                      {formatNumber(maxAnomalyScore)}
                    </strong>
                  </div>
                </div>

                <div className="anomaly-stat">
                  <div className="anomaly-stat-icon">AVG</div>
                  <div>
                    <span className="anomaly-stat-label">
                      Average AI Score
                    </span>
                    <strong className="anomaly-stat-value">
                      {formatNumber(averageAnomalyScore)}
                    </strong>
                  </div>
                </div>

                <div className="anomaly-stat">
                  <div className="anomaly-stat-icon">DB</div>
                  <div>
                    <span className="anomaly-stat-label">
                      Records Analyzed
                    </span>
                    <strong className="anomaly-stat-value">
                      {anomalies?.records_analyzed || 0}
                    </strong>
                  </div>
                </div>
              </div>

              <div className="panel">
                <div className="panel-header">
                  <div>
                    <span>REAL-TIME</span>
                    <h2>Active Conditions</h2>
                  </div>
                  <StatusBadge
                    status={
                      activeConditionCount
                        ? currentHealth
                        : "normal"
                    }
                  />
                </div>

                <div className="active-condition-grid">
                  {activeConditions.length ? (
                    activeConditions.map((condition, index) => (
                      <ConditionCard
                        key={`${condition.metric}-${index}`}
                        condition={condition}
                      />
                    ))
                  ) : (
                    <div className="empty-state">
                      No active conditions detected.
                    </div>
                  )}
                </div>
              </div>

              <div className="dashboard-grid">
                <div className="panel">
                  <div className="panel-header">
                    <div>
                      <span>DISTRIBUTION</span>
                      <h2>Detection Breakdown</h2>
                    </div>
                  </div>

                  <div className="distribution-list">
                    <DistributionRow
                      label="Critical"
                      value={criticalCount}
                      total={anomalyCount}
                    />

                    <DistributionRow
                      label="Warning"
                      value={warningCount}
                      total={anomalyCount}
                    />

                    <DistributionRow
                      label="Active"
                      value={activeConditionCount}
                      total={
                        anomalyCount + activeConditionCount
                      }
                    />
                  </div>
                </div>

                <div className="panel">
                  <div className="panel-header">
                    <div>
                      <span>EVENT STREAM</span>
                      <h2>Recent Detection Timeline</h2>
                    </div>
                  </div>

                  <div className="anomaly-timeline">
                    {anomalies?.anomalies?.length ? (
                      anomalies.anomalies
                        .slice(0, 8)
                        .map((event, index) => (
                          <EventRow
                            key={`${event.timestamp}-${event.metric}-${index}`}
                            event={event}
                          />
                        ))
                    ) : (
                      <div className="empty-state">
                        No historical anomaly events detected.
                      </div>
                    )}
                  </div>
                </div>
              </div>

              <div className="panel">
                <div className="panel-header">
                  <div>
                    <span>DETAILED ANALYSIS</span>
                    <h2>AI Detection Records</h2>
                  </div>
                  <strong>
                    {anomalyCount} events
                  </strong>
                </div>

                <div className="detection-list">
                  {anomalies?.anomalies?.length ? (
                    anomalies.anomalies
                      .slice(0, 20)
                      .map((anomaly, index) => (
                        <DetailedAnomaly
                          key={`${anomaly.timestamp}-${anomaly.metric}-${index}`}
                          anomaly={anomaly}
                        />
                      ))
                  ) : (
                    <div className="empty-state">
                      No anomaly records available.
                    </div>
                  )}
                </div>
              </div>

              <SimulationPanel
                simulation={simulation}
                onChange={changeSimulation}
              />
            </div>
          )}

          {page === "predictive" && (
            <div className="page">
              <PageTitle
                eyebrow="PREDICTIVE MAINTENANCE ENGINE"
                title="Predictive Intelligence"
                description={pageDescription.predictive}
              />

              <div className="anomaly-stat-grid">
                <div className="anomaly-stat">
                  <div className="anomaly-stat-icon">AI</div>
                  <div>
                    <span className="anomaly-stat-label">
                      Prediction Status
                    </span>
                    <strong className="anomaly-stat-value">
                      {(predictive?.status || "normal").toUpperCase()}
                    </strong>
                  </div>
                </div>

                <div className="anomaly-stat">
                  <div className="anomaly-stat-icon">C</div>
                  <div>
                    <span className="anomaly-stat-label">
                      Critical Risk
                    </span>
                    <strong className="anomaly-stat-value">
                      {criticalPredictions}
                    </strong>
                  </div>
                </div>

                <div className="anomaly-stat">
                  <div className="anomaly-stat-icon">H</div>
                  <div>
                    <span className="anomaly-stat-label">
                      High Risk
                    </span>
                    <strong className="anomaly-stat-value">
                      {highPredictions}
                    </strong>
                  </div>
                </div>

                <div className="anomaly-stat">
                  <div className="anomaly-stat-icon">W</div>
                  <div>
                    <span className="anomaly-stat-label">
                      Warning Risk
                    </span>
                    <strong className="anomaly-stat-value">
                      {warningPredictions}
                    </strong>
                  </div>
                </div>

                <div className="anomaly-stat">
                  <div className="anomaly-stat-icon">M</div>
                  <div>
                    <span className="anomaly-stat-label">
                      Metrics Analyzed
                    </span>
                    <strong className="anomaly-stat-value">
                      {predictive?.metrics_analyzed || 0}
                    </strong>
                  </div>
                </div>

                <div className="anomaly-stat">
                  <div className="anomaly-stat-icon">N</div>
                  <div>
                    <span className="anomaly-stat-label">
                      Samples
                    </span>
                    <strong className="anomaly-stat-value">
                      {predictive?.records_analyzed || 0}
                    </strong>
                  </div>
                </div>
              </div>

              <div className="panel">
                <div className="panel-header">
                  <div>
                    <span>RISK ANALYSIS</span>
                    <h2>Hardware Predictions</h2>
                  </div>

                  <StatusBadge
                    status={predictive?.status || "normal"}
                  />
                </div>

                <div className="prediction-grid">
                  {predictive?.predictions?.length ? (
                    predictive.predictions.map((prediction) => (
                      <PredictionCard
                        key={prediction.metric}
                        prediction={prediction}
                      />
                    ))
                  ) : (
                    <div className="empty-state">
                      Not enough telemetry data for predictive analysis.
                    </div>
                  )}
                </div>
              </div>

              <div className="panel">
                <div className="panel-header">
                  <div>
                    <span>HEALTH EVENTS</span>
                    <h2>Maintenance Signals</h2>
                  </div>
                </div>

                <div className="health-event">
                  <div className="health-event-icon">AI</div>
                  <div>
                    <div className="health-event-title">
                      <strong>Predictive analysis active</strong>
                    </div>

                    <div className="health-event-message">
                      The engine evaluates recent telemetry against
                      thresholds, historical baselines and trend direction
                      to generate maintenance risk signals.
                    </div>

                    <div className="health-event-time">
                      {predictive?.records_analyzed || 0} telemetry records
                      analyzed
                    </div>

                    <div className="health-event-metrics">
                      {predictive?.metrics_analyzed || 0} metrics currently
                      supported by the predictive engine
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </section>
      </main>
    </div>
  );
}

export default App;