import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { Eye, FileDown, Trash2 } from "lucide-react";
import API from "../api/axiosInstance";
import AlertDialog from "../components/AlertDialog";

function DetectionHistory() {
  const [history, setHistory] = useState([]);

  const [confirmBox, setConfirmBox] = useState({
    isOpen: false,
    id: null,
  });

  const fetchHistory = async () => {
    const res = await API.get("/history");
    setHistory(res.data.data);
  };

  const deleteSession = async (id) => {
    setConfirmBox({
      isOpen: true,
      id,
    });
  };

  const confirmDeleteSession = async () => {
    if (!confirmBox.id) return;

    await API.delete(`/history/${confirmBox.id}`);

    setConfirmBox({
      isOpen: false,
      id: null,
    });

    fetchHistory();
  };

  const closeConfirmBox = () => {
    setConfirmBox({
      isOpen: false,
      id: null,
    });
  };

  useEffect(() => { fetchHistory(); }, []);

  const renderPreview = (item) => {
    if (!item.output_file_url) {
      return (
        <div
          style={{
            width: "112px",
            height: "64px",
            borderRadius: "8px",
            background: "#0a0000",
            border: "1px solid #3D0000",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            color: "#6b7280",
            fontSize: "11px",
            fontWeight: 600,
            letterSpacing: "0.06em",
            textTransform: "uppercase",
          }}
        >
          No preview
        </div>
      );
    }

    if (item.input_type === "video" || item.input_type === "webcam_video") {
      return (
        <video
          src={item.output_file_url}
          style={{
            width: "112px",
            height: "64px",
            objectFit: "cover",
            borderRadius: "8px",
            border: "1px solid #3D0000",
            background: "#000",
            display: "block",
            boxShadow: "0 0 12px rgba(149, 1, 1, 0.18)",
          }}
          muted
          preload="metadata"
        />
      );
    }

    return (
      <img
        src={item.output_file_url}
        alt="output"
        style={{
          width: "112px",
          height: "64px",
          objectFit: "cover",
          borderRadius: "8px",
          border: "1px solid #3D0000",
          background: "#000",
          display: "block",
          boxShadow: "0 0 12px rgba(149, 1, 1, 0.18)",
        }}
      />
    );
  };

  return (
    <>
      <div style={{ padding: "2rem", display: "flex", flexDirection: "column", gap: "2rem" }}>
        {/* Header */}
        <div>
          <h1 className="vrs-page-title">Detection History</h1>
          <p className="vrs-page-sub">All previous detection sessions</p>
        </div>

        {/* Table */}
        <div className="vrs-card">
          <div style={{ overflowX: "auto" }}>
            <table className="vrs-table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Preview</th>
                  <th>Type</th>
                  <th>Vehicles</th>
                  <th>Persons</th>
                  <th>Plates</th>
                  <th>Date</th>
                  <th>Actions</th>
                </tr>
              </thead>

              <tbody>
                {history.map((item) => (
                  <tr key={item.id}>
                    <td className="id-cell">#{item.id}</td>

                    <td style={{ padding: "10px 16px" }}>
                      {renderPreview(item)}
                    </td>

                    <td>
                      <span className="vrs-badge vrs-badge--gray" style={{ textTransform: "capitalize" }}>
                        {item.input_type}
                      </span>
                    </td>

                    <td style={{ fontFamily: "'JetBrains Mono', monospace" }}>{item.total_vehicles}</td>
                    <td style={{ fontFamily: "'JetBrains Mono', monospace" }}>{item.total_persons}</td>
                    <td style={{ fontFamily: "'JetBrains Mono', monospace" }}>{item.total_number_plates}</td>

                    <td style={{ color: "#6b7280", fontSize: "13px", whiteSpace: "nowrap" }}>
                      {new Date(item.created_at).toLocaleString()}
                    </td>

                    <td>
                      <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
                        <Link
                          to={`/history/${item.id}`}
                          style={{ color: "#950101", textDecoration: "none", display: "flex", alignItems: "center", gap: "4px", fontSize: "13px", fontWeight: 600, letterSpacing: "0.06em" }}
                        >
                          <Eye size={14} />
                          View
                        </Link>

                        <a
                          href={`${import.meta.env.VITE_BACKEND_BASE_URL}/api/history/${item.id}/report`}
                          target="_blank"
                          rel="noreferrer"
                          style={{ color: "#4ade80", textDecoration: "none", display: "flex", alignItems: "center", gap: "4px", fontSize: "13px", fontWeight: 600, letterSpacing: "0.06em" }}
                        >
                          <FileDown size={14} />
                          Report
                        </a>

                        <button
                          onClick={() => deleteSession(item.id)}
                          style={{ background: "none", border: "none", color: "#FF0000", cursor: "pointer", display: "flex", alignItems: "center", gap: "4px", fontSize: "13px", fontWeight: 600, letterSpacing: "0.06em", padding: 0 }}
                        >
                          <Trash2 size={14} />
                          Delete
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}

                {history.length === 0 && (
                  <tr>
                    <td
                      colSpan="8"
                      style={{ padding: "3rem", textAlign: "center", color: "#6b7280", letterSpacing: "0.06em", fontSize: "14px" }}
                    >
                      No detection history found.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <AlertDialog
        isOpen={confirmBox.isOpen}
        type="confirm"
        title="Delete Session"
        message="Are you sure you want to delete this session?"
        confirmText="Delete"
        cancelText="Cancel"
        showCancel={true}
        onConfirm={confirmDeleteSession}
        onCancel={closeConfirmBox}
      />
    </>
  );
}

export default DetectionHistory;