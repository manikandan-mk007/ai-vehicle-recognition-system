import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { FileDown } from "lucide-react";
import API from "../api/axiosInstance";

function SessionDetails() {
  const { id } = useParams();
  const [details, setDetails] = useState(null);

  const fetchDetails = async () => {
    const res = await API.get(`/history/${id}`);
    setDetails(res.data.data);
  };

  useEffect(() => { fetchDetails(); }, [id]);

  if (!details) {
    return (
      <div style={{ padding: "3rem 2rem", display: "flex", alignItems: "center", gap: "12px" }}>
        <span className="vrs-spinner" />
        <span style={{ color: "#6b7280", letterSpacing: "0.08em", textTransform: "uppercase", fontSize: "13px" }}>
          Loading session details...
        </span>
      </div>
    );
  }

  const { session, vehicles, persons, number_plates } = details;

  const renderOutput = () => {
    if (!session.output_file_url) {
      return <p style={{ color: "#6b7280" }}>No output file found.</p>;
    }
    if (session.input_type === "video" || session.input_type === "webcam_video") {
      return (
        <video
          src={session.output_file_url}
          controls
          style={{
            width: "100%",
            borderRadius: "8px",
            border: "1px solid #3D0000",
            background: "#000",
            display: "block",
            boxShadow: "0 0 18px rgba(149, 1, 1, 0.18)",
          }}
        />
      );
    }
    return (
      <img
        src={session.output_file_url}
        alt="output"
        className="vrs-output-img"
      />
    );
  };

  return (
    <div style={{ padding: "2rem", display: "flex", flexDirection: "column", gap: "2rem" }}>
      {/* Header */}
      <div>
        <div style={{ display: "flex", alignItems: "center", gap: "12px", flexWrap: "wrap" }}>
          <h1 className="vrs-page-title">Session</h1>
          <span className="vrs-badge vrs-badge--red" style={{ fontSize: "14px", padding: "4px 14px" }}>
            #{session.id}
          </span>
          <span className="vrs-badge vrs-badge--gray" style={{ textTransform: "capitalize" }}>
            {session.input_type}
          </span>
        </div>
        <p className="vrs-page-sub">{new Date(session.created_at).toLocaleString()}</p>

        <a
          href={`http://127.0.0.1:8000/api/history/${session.id}/report`}
          target="_blank"
          rel="noreferrer"
          className="vrs-btn vrs-btn--success"
          style={{ display: "inline-flex", marginTop: "1rem", textDecoration: "none" }}
        >
          <FileDown size={16} />
          Download PDF Report
        </a>
      </div>

      {/* Output preview */}
      <div className="vrs-card">
        <h3 className="vrs-heading">Output Preview</h3>
        {renderOutput()}
      </div>

      <Section title="Vehicles"      data={vehicles}       type="vehicle" />
      <Section title="Persons"       data={persons}        type="person" />
      <Section title="Number Plates" data={number_plates}  type="plate" />
    </div>
  );
}

function Section({ title, data, type }) {
  return (
    <div className="vrs-card">
      <h2 className="vrs-heading">{title}</h2>

      {data.length === 0 ? (
        <p style={{ color: "#6b7280", fontSize: "14px" }}>No data found.</p>
      ) : (
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(220px, 1fr))", gap: "1rem" }}>
          {data.map((item) => (
            <div key={item.id} className="vrs-detail-card">
              {item.crop_url && (
                <img src={item.crop_url} alt="crop" />
              )}

              <div className="vrs-detail-row">
                <span className="vrs-detail-label">Label</span>
                <span className="vrs-detail-value">{item.label}</span>
              </div>

              {type === "vehicle" && (
                <>
                  <div className="vrs-detail-row">
                    <span className="vrs-detail-label">Model</span>
                    <span className="vrs-detail-value">{item.vehicle_model || "Unknown"}</span>
                  </div>
                  <div className="vrs-detail-row">
                    <span className="vrs-detail-label">Confidence</span>
                    <span className="vrs-detail-value">{item.vehicle_model_confidence || "N/A"}</span>
                  </div>
                </>
              )}

              {type === "person" && (
                <>
                  <div className="vrs-detail-row">
                    <span className="vrs-detail-label">Type</span>
                    <span className="vrs-detail-value">{item.person_type || "Unknown"}</span>
                  </div>
                  <div className="vrs-detail-row">
                    <span className="vrs-detail-label">Confidence</span>
                    <span className="vrs-detail-value">{item.person_type_confidence || "N/A"}</span>
                  </div>
                </>
              )}

              {type === "plate" && (
                <>
                  <div className="vrs-detail-row">
                    <span className="vrs-detail-label">Plate</span>
                    <span className="vrs-plate">{item.plate_text || "—"}</span>
                  </div>
                  <div className="vrs-detail-row">
                    <span className="vrs-detail-label">OCR Conf.</span>
                    <span className="vrs-detail-value">{item.ocr_confidence || "N/A"}</span>
                  </div>
                </>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default SessionDetails;