import { useEffect, useState } from "react";
import "./App.css";

const API_URL = "http://127.0.0.1:8000";

const cities = [
  "Ahmedabad",
  "Aizawl",
  "Amaravati",
  "Amritsar",
  "Bengaluru",
  "Bhopal",
  "Brajrajnagar",
  "Chandigarh",
  "Chennai",
  "Coimbatore",
  "Delhi",
  "Ernakulam",
  "Gurugram",
  "Guwahati",
  "Hyderabad",
  "Jaipur",
  "Jorapokhar",
  "Kochi",
  "Kolkata",
  "Lucknow",
  "Mumbai",
  "Patna",
  "Shillong",
  "Talcher",
  "Thiruvananthapuram",
  "Visakhapatnam"
];

const initialForm = {
  city: "Delhi",
  pm10: 80,
  no: 20,
  no2: 35,
  nox: 45,
  nh3: 20,
  co: 1,
  so2: 15,
  o3: 40,
  hour: 15,
  month: 12,
  day_of_week: 3,
  pm25_lag_24: 60,
  pm25_lag_48: 55,
  aqi: 350
};

function App() {
  const [form, setForm] = useState(initialForm);
  const [result, setResult] = useState(null);
  const [xai, setXai] = useState(null);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [historyLoading, setHistoryLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    fetchExplainability();
    fetchHistory();
  }, []);

  const handleChange = (e) => {
    const { name, value } = e.target;

    setForm((prev) => ({
      ...prev,
      [name]:
        name === "city"
          ? value
          : value === ""
            ? ""
            : Number(value)
    }));
  };

  const fetchExplainability = async () => {
    try {
      const response = await fetch(`${API_URL}/explain`);
      if (!response.ok) throw new Error("Explainability API failed");
      const data = await response.json();
      setXai(data.explainability);
    } catch (err) {
      console.error("XAI Error:", err);
    }
  };

  const fetchHistory = async () => {
    setHistoryLoading(true);
    try {
      const response = await fetch(`${API_URL}/history?limit=20`);
      if (!response.ok) throw new Error("History API failed");
      const data = await response.json();
      if (data.status === "success") {
        setHistory(data.history || []);
      }
    } catch (err) {
      console.error("History Error:", err);
    } finally {
      setHistoryLoading(false);
    }
  };

  const handlePredict = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    try {
      const response = await fetch(`${API_URL}/predict`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(form)
      });

      if (!response.ok) throw new Error("Prediction API failed");
      const data = await response.json();
      setResult(data);
      await fetchHistory();
    } catch (err) {
      console.error(err);
      setError("Unable to generate prediction. Please verify that the backend is active.");
    } finally {
      setLoading(false);
    }
  };

  const isNCR = result?.grap?.ncr_applicable === true;
  const policyValue = isNCR
    ? result?.grap?.grap_stage
    : result?.grap?.action_level;

  const formatTime = (timestamp) => {
    if (!timestamp) return "-";
    return new Date(timestamp).toLocaleString("en-IN", {
      day: "2-digit",
      month: "short",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit"
    });
  };

  const getRiskClass = (category) => {
    if (!category) return "";
    const cat = category.toLowerCase();
    if (cat.includes("good") || cat.includes("satisfactory")) return "risk-low";
    if (cat.includes("moderate")) return "risk-mod";
    if (cat.includes("poor") && !cat.includes("very")) return "risk-high";
    if (cat.includes("very poor")) return "risk-very-high";
    if (cat.includes("severe")) return "risk-severe";
    return "";
  };

  return (
    <div className="app">
      {/* HEADER */}
      <header className="topbar">
        <div className="brand">
          <div className="brand-icon">AC</div>
          <div>
            <div className="brand-name">
              Air<span>Cast</span>
              <small>AI ENGINE</small>
            </div>
            <div className="brand-subtitle">
              Intelligent 24H Air Quality Forecasting & Advisory System
            </div>
          </div>
        </div>

        <div className="system-status">
          <span className="status-dot"></span>
          <div>
            <strong>INFERENCE READY</strong>
            <small>FastAPI · PostgreSQL · Scikit-Learn</small>
          </div>
        </div>
      </header>

      {/* HERO */}
      <section className="hero">
        <div className="hero-content">
          <div className="eyebrow">
            ● HIGH-RESOLUTION ATMOSPHERIC MODELING
          </div>

          <h1>
            Predict the air.
            <span>Protect the future.</span>
          </h1>

          <p>
            AirCast utilizes histogram-based gradient boosting on multi-pollutant
            interactions and lag features to predict PM2.5 levels, classify health risks, 
            and evaluate dynamic policy thresholds across 26 cities.
          </p>

          <div className="hero-tags">
            <span>◆ 24H FORECAST</span>
            <span>◆ HISTGRADIENTBOOSTING</span>
            <span>◆ PERMUTATION XAI</span>
            <span>◆ CAQM GRAP MAPPING</span>
          </div>
        </div>

        <div className="hero-orbit">
          <div className="radar-grid"></div>
          <div className="orbit-circle">
            <div className="orbit-center">
              <small>PM2.5</small>
              <strong>FORECAST</strong>
              <span>24 HOURS</span>
            </div>
          </div>
        </div>
      </section>

      {/* INPUT PANEL */}
      <section className="panel input-panel">
        <div className="section-heading">
          <div>
            <div className="eyebrow">CONFIG / INPUT FEATURES</div>
            <h2>Air Quality Input Parameters</h2>
            <p>
              Enter current sensor readings and temporal parameters for model regression.
            </p>
          </div>

          <div className="model-badge">
            ● HistGradientBoostingRegressor
          </div>
        </div>

        <form onSubmit={handlePredict}>
          <div className="city-row">
            <div>
              <small>MONITORING STATION REGION</small>
              <strong>● {form.city} Station</strong>
            </div>

            <select
              name="city"
              value={form.city}
              onChange={handleChange}
            >
              {cities.map((city) => (
                <option key={city} value={city}>
                  {city}
                </option>
              ))}
            </select>
          </div>

          <div className="form-section-title">
            CURRENT POLLUTANT PARAMETERS (µg/m³)
          </div>

          <div className="input-grid">
            <InputField label="PM10" name="pm10" value={form.pm10} onChange={handleChange} suffix="µg/m³" />
            <InputField label="NO" name="no" value={form.no} onChange={handleChange} suffix="µg/m³" />
            <InputField label="NO₂" name="no2" value={form.no2} onChange={handleChange} suffix="µg/m³" />
            <InputField label="NOx" name="nox" value={form.nox} onChange={handleChange} suffix="µg/m³" />
            <InputField label="NH₃" name="nh3" value={form.nh3} onChange={handleChange} suffix="µg/m³" />
            <InputField label="CO" name="co" value={form.co} onChange={handleChange} suffix="mg/m³" />
            <InputField label="SO₂" name="so2" value={form.so2} onChange={handleChange} suffix="µg/m³" />
            <InputField label="O₃" name="o3" value={form.o3} onChange={handleChange} suffix="µg/m³" />
          </div>

          <div className="form-section-title">
            TEMPORAL & LAG PARAMETERS
          </div>

          <div className="input-grid">
            <InputField label="Hour" name="hour" value={form.hour} onChange={handleChange} suffix="00–23" />
            <InputField label="Month" name="month" value={form.month} onChange={handleChange} suffix="01–12" />
            <InputField label="Day of Week" name="day_of_week" value={form.day_of_week} onChange={handleChange} suffix="0(M)–6(S)" />
            <InputField label="Current AQI" name="aqi" value={form.aqi} onChange={handleChange} suffix="Index" />
          </div>

          <div className="form-section-title">
            HISTORICAL LAG VALUES
          </div>

          <div className="input-grid history-inputs">
            <InputField label="PM2.5 Lag (24h)" name="pm25_lag_24" value={form.pm25_lag_24} onChange={handleChange} suffix="µg/m³" />
            <InputField label="PM2.5 Lag (48h)" name="pm25_lag_48" value={form.pm25_lag_48} onChange={handleChange} suffix="µg/m³" />
          </div>

          <button
            type="submit"
            className="forecast-button"
            disabled={loading}
          >
            {loading ? "COMPUTING REGRESSION FORECAST..." : "✦ GENERATE 24-HOUR FORECAST →"}
          </button>
        </form>

        {error && <div className="error-box">{error}</div>}
      </section>

      {/* RESULTS DISPLAY */}
      {result && (
        <>
          <section className="results-section">
            <div className="results-title">
              <h2>Forecast Intelligence Summary</h2>
              <span>● Station: {result.city}</span>
            </div>

            <div className="result-grid">
              <ResultCard
                label="24H REGRESSION"
                title="Predicted PM2.5"
                value={result.prediction.predicted_pm25_24h}
                unit="µg/m³"
                tag="PM2.5"
              />

              <ResultCard
                label="EXPOSURE TIER"
                title="Pollution Category"
                value={result.risk.category}
                sub={`${result.risk.risk_level} Health Risk`}
                tag="RISK"
                className={getRiskClass(result.risk.category)}
              />

              <ResultCard
                label="INPUT BASELINE"
                title="Current AQI"
                value={result.grap.aqi ?? form.aqi ?? "—"}
                sub={result.grap.aqi_category ?? "CPCB Standard"}
                tag="AQI"
              />

              <ResultCard
                label="POLICY LEVEL"
                title={isNCR ? "GRAP Stage" : "Air Action Level"}
                value={policyValue || "AQI Required"}
                sub={isNCR ? "CAQM NCR Mandate" : "City Action Plan"}
                tag={isNCR ? "GRAP" : "ACTION"}
              />
            </div>
          </section>

          {/* HEALTH ADVISORY */}
          <section className="panel advisory-panel">
            <div className="section-heading compact">
              <div>
                <h2>Health Guidance Advisory</h2>
                <p>Personalized precautions based on predicted PM2.5 concentrations</p>
              </div>
              <span className="category-badge">
                {result.advisory.category} Advisory
              </span>
            </div>

            <div className="advisory-box">
              <div className="advisory-header">
                <div className="check-icon">🛡️</div>
                <div>
                  <strong>{result.advisory.summary}</strong>
                  <span>Mitigate respiratory particulate exposure and health risks</span>
                </div>
              </div>

              <div className="recommendation-grid">
                {result.advisory.recommendations.map((recommendation, index) => (
                  <div key={index} className="rec-item">
                    <span>✓</span> {recommendation}
                  </div>
                ))}
              </div>
            </div>
          </section>

          {/* POLICY SECTION */}
          <section className="panel grap-panel">
            <div className="section-heading compact">
              <div>
                <h2>
                  {isNCR ? "Delhi-NCR GRAP Status" : "AirCast Air Quality Action Plan"}
                </h2>
                <p>
                  {isNCR
                    ? "Delhi-NCR GRAP assessment"
                    : "AirCast air-quality action framework for non-NCR territory"}
                </p>
              </div>

              <span className="stage-badge">
                {policyValue || "AQI Required"}
              </span>
            </div>

            <div className="grap-cards">
              <div className="grap-card">
                <small>01 / LOCATION</small>
                <span>Territory Type</span>
                <strong>{result.city}</strong>
                <em>{isNCR ? "NCR Jurisdiction" : "Non-NCR Region"}</em>
              </div>

              <div className="grap-card">
                <small>02 / SEVERITY</small>
                <span>AQI Category</span>
                <strong>{result.grap.aqi_category || "—"}</strong>
                <em>Recorded AQI: {result.grap.aqi ?? form.aqi ?? "—"}</em>
              </div>

              <div className="grap-card">
                <small>03 / DIRECTIVE</small>
                <span>Applied Framework</span>
                <strong>{policyValue || "—"}</strong>
                <em>{isNCR ? "Enforced CAQM Stage" : "Advisory Action Level"}</em>
              </div>
            </div>

            <div className="grap-message">
              <strong>Statutory & Regional Guidance</strong>
              <span>
                {result.grap.message || "Action assessment based on reference AQI guidelines."}
              </span>
            </div>
          </section>

          {/* COMBINED ACTION ITEMS */}
          <section className="panel actions-panel">
            <div className="section-heading compact">
              <div>
                <h2>Recommended Civic & Citizen Actions</h2>
                <p>Consolidated citizen advisories and pollution control directives</p>
              </div>
            </div>

            <div className="actions-grid">
              {[
                ...(result.advisory.recommendations || []),
                ...(result.grap.recommendations || [])
              ]
                .filter((item, index, array) => array.indexOf(item) === index)
                .map((action, index) => (
                  <div className="action-item" key={index}>
                    <span>{String(index + 1).padStart(2, "0")}</span>
                    <p>{action}</p>
                    <b>→</b>
                  </div>
                ))}
            </div>
          </section>

          {/* XAI PANEL */}
          {xai && (
            <section className="panel xai-panel">
              <div className="section-heading compact">
                <div>
                  <h2>Model Interpretability (XAI)</h2>
                  <p>Permutation feature importance calculated on validation test split</p>
                </div>
                <span className="xai-badge">Scikit-Learn XAI</span>
              </div>

              <div className="xai-summary">
                <div>
                  <small>EVALUATED MODEL</small>
                  <strong>{xai.model}</strong>
                </div>
                <div>
                  <small>TEST SAMPLE SIZE</small>
                  <strong>{xai.sample_size?.toLocaleString()} Records</strong>
                </div>
                <div>
                  <small>BASELINE TEST MAE</small>
                  <strong>{xai.baseline_mae}</strong>
                </div>
              </div>

              <div className="feature-box">
                <h3>Top Influential Predictive Features</h3>
                <p>
                  Permutation drop: Magnitude of error increase when feature values are randomly shuffled.
                </p>

                {xai.top_features?.map((feature, index) => {
                  const maxImportance = Math.max(
                    ...xai.top_features.map((item) => item.importance)
                  );
                  const width = (feature.importance / maxImportance) * 100;

                  return (
                    <div className="feature-row" key={feature.feature}>
                      <div className="feature-name">
                        <strong>
                          {index + 1}. {feature.feature}
                        </strong>
                        <small>{feature.group}</small>
                      </div>

                      <div className="feature-bar">
                        <div style={{ width: `${width}%` }}></div>
                      </div>

                      <strong className="feature-value">
                        {feature.importance.toFixed(3)}
                      </strong>
                    </div>
                  );
                })}
              </div>

              <div className="feature-box">
                <h3>Feature Group Contributions</h3>
                <p>Aggregate importance distribution across feature categories.</p>

                {Object.entries(xai.group_importance || {}).map(([group, value]) => {
                  const maxGroup = Math.max(...Object.values(xai.group_importance));
                  const width = (value / maxGroup) * 100;

                  return (
                    <div className="group-row" key={group}>
                      <div className="group-header">
                        <strong>{group}</strong>
                        <span>{value.toFixed(3)}</span>
                      </div>
                      <div className="group-bar">
                        <div style={{ width: `${width}%` }}></div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </section>
          )}

          {/* DB STATUS */}
          <div className="database-status">
            <div>
              <small>RELATIONAL STORE</small>
              <strong>PostgreSQL 16</strong>
            </div>

            <div>
              <small>PREDICTION ID</small>
              <strong>#{result.database?.prediction_id ?? "OFFLINE"}</strong>
            </div>

            <div>
              <small>LOGGED AT</small>
              <strong>
                {result.database?.prediction_time
                  ? formatTime(result.database.prediction_time)
                  : "Not Logged"}
              </strong>
            </div>

            <div className="saved-status">
              <span></span>
              {result.database?.status === "saved"
                ? "Record Committed"
                : "Offline Node"}
            </div>
          </div>
        </>
      )}

      {/* HISTORY TABLE */}
      <section className="panel history-panel">
        <div className="section-heading compact">
          <div>
            <div className="eyebrow">PERSISTENCE LAYER</div>
            <h2>Recent Forecast History</h2>
            <p>Real-time telemetry queries logged in the PostgreSQL database</p>
          </div>

          <button
            className="refresh-button"
            onClick={fetchHistory}
            disabled={historyLoading}
          >
            {historyLoading ? "FETCHING..." : "↻ REFRESH HISTORY"}
          </button>
        </div>

        {history.length === 0 ? (
          <div className="empty-history">
            No forecast transactions logged in the database yet.
          </div>
        ) : (
          <div className="history-table-wrapper">
            <table className="history-table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Location</th>
                  <th>Predicted PM2.5</th>
                  <th>Risk Tier</th>
                  <th>AQI Input</th>
                  <th>Policy Stage</th>
                  <th>Timestamp</th>
                </tr>
              </thead>
              <tbody>
                {history.map((item, index) => (
                  <tr
                    key={item.prediction_id}
                    className={index === 0 ? "latest-row" : ""}
                  >
                    <td>
                      <strong>#{item.prediction_id}</strong>
                      {index === 0 && <span className="latest-tag">LATEST</span>}
                    </td>
                    <td>{item.city}</td>
                    <td>
                      <strong>{Number(item.predicted_pm25).toFixed(2)}</strong>
                      <small> µg/m³</small>
                    </td>
                    <td>
                      <span className={`risk-pill ${getRiskClass(item.risk_category)}`}>
                        {item.risk_category}
                      </span>
                    </td>
                    <td>{item.aqi !== null ? item.aqi : "—"}</td>
                    <td>
                      <span className="policy-pill">
                        {item.grap_stage || "—"}
                      </span>
                    </td>
                    <td>{formatTime(item.prediction_time)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>

      {/* FOOTER */}
      <footer>
        <div>
          <strong>AirCast Intelligence</strong>
          <span>Machine Learning Atmospheric Forecasting Framework</span>
        </div>
        <div>
          HistGradientBoostingRegressor · CAQM GRAP Protocols · PostgreSQL Telemetry
        </div>
      </footer>
    </div>
  );
}

function InputField({ label, name, value, onChange, suffix }) {
  return (
    <div className="input-field">
      <div className="input-label">
        <label>{label}</label>
        {suffix && <span>{suffix}</span>}
      </div>
      <input
        type="number"
        name={name}
        value={value}
        onChange={onChange}
        step="any"
      />
    </div>
  );
}

function ResultCard({ label, title, value, unit, sub, tag, className = "" }) {
  return (
    <div className={`result-card ${className}`}>
      <div className="card-top">
        <small>{label}</small>
        <span>{tag}</span>
      </div>
      <p>{title}</p>
      <strong>{value}</strong>
      {unit && <em>{unit}</em>}
      {sub && <div className="card-sub">{sub}</div>}
      <div className="card-line"></div>
    </div>
  );
}

export default App;