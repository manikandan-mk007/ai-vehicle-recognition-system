import { useState } from "react";
import { Upload, Video as VideoIcon } from "lucide-react";
import API from "../api/axiosInstance";
import AlertDialog from "../components/AlertDialog";

function VideoDetection() {
  const [file, setFile]               = useState(null);
  const [enablePlateOCR, setEnablePlateOCR] = useState(false);
  const [result, setResult]           = useState(null);
  const [loading, setLoading]         = useState(false);

  const [alertBox, setAlertBox] = useState({
    isOpen: false,
    title: "",
    message: "",
  });

  const showAlert = (title, message) => {
    setAlertBox({
      isOpen: true,
      title,
      message,
    });
  };

  const closeAlert = () => {
    setAlertBox({
      isOpen: false,
      title: "",
      message: "",
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) {
      showAlert("Video Required", "Please select a video file");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    try {
      setLoading(true);
      setResult(null);
      const res = await API.post(
        `/analyze/video?enable_plate_ocr=${enablePlateOCR}`,
        formData,
        { headers: { "Content-Type": "multipart/form-data" } }
      );
      setResult(res.data);
    } catch (error) {
      showAlert("Video Detection Failed", error.response?.data?.detail || "Video detection failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <div style={{ padding: "2rem", display: "flex", flexDirection: "column", gap: "2rem" }}>
        {/* Header */}
        <div>
          <h1 className="vrs-page-title">Video Detection</h1>
          <p className="vrs-page-sub">Upload traffic video to detect and track vehicles, persons and number plates</p>
        </div>

        {/* Upload form */}
        <form onSubmit={handleSubmit} className="vrs-card" style={{ display: "flex", flexDirection: "column", gap: "1.25rem" }}>
          <h3 className="vrs-heading">Select Video</h3>

          <label
            className="vrs-upload-zone"
            style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: "12px" }}
          >
            <VideoIcon size={32} style={{ color: "#950101" }} />
            <div style={{ textAlign: "center" }}>
              <div style={{ fontWeight: 600, color: "#e5e7eb", fontSize: "14px" }}>
                {file ? file.name : "Click to upload video"}
              </div>
              <div style={{ fontSize: "12px", color: "#6b7280", marginTop: "4px" }}>
                {file ? `${(file.size / (1024 * 1024)).toFixed(1)} MB` : "MP4, AVI, MOV supported"}
              </div>
            </div>
            <input
              type="file"
              accept="video/*"
              onChange={(e) => setFile(e.target.files[0])}
              style={{ display: "none" }}
            />
          </label>

          <label style={{ display: "flex", alignItems: "center", gap: "10px", cursor: "pointer", fontSize: "13px", color: "#9ca3af", letterSpacing: "0.06em" }}>
            <input
              type="checkbox"
              checked={enablePlateOCR}
              onChange={(e) => setEnablePlateOCR(e.target.checked)}
            />
            Enable Number Plate OCR
          </label>

          <div style={{ display: "flex", alignItems: "center", gap: "1rem", flexWrap: "wrap" }}>
            <button
              type="submit"
              disabled={loading}
              className="vrs-btn vrs-btn--primary"
            >
              {loading ? (
                <>
                  <span className="vrs-spinner" style={{ width: "16px", height: "16px" }} />
                  Processing Video...
                </>
              ) : (
                <>
                  <Upload size={16} />
                  Analyze Video
                </>
              )}
            </button>

            {loading && (
              <p style={{ fontSize: "12px", color: "#eab308", letterSpacing: "0.04em" }}>
                ⚠ Video processing may take a while. Please wait.
              </p>
            )}
          </div>
        </form>

        {/* Results */}
        {result && (
          <div style={{ display: "flex", flexDirection: "column", gap: "1.5rem" }} className="vrs-fade-in">
            {/* Processed video */}
            <div className="vrs-card">
              <h2 className="vrs-heading">Processed Video</h2>
              <video
                src={result.output_video_url}
                controls
                style={{ width: "100%", borderRadius: "8px", border: "1px solid #3D0000", background: "#000", display: "block" }}
              />
            </div>

            {/* Stats */}
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(140px, 1fr))", gap: "1rem" }}>
              <Stat title="Unique Vehicles"  value={result.unique_vehicles} />
              <Stat title="Unique Persons"   value={result.unique_persons} />
              <Stat title="Tracked Objects"  value={result.unique_tracked_objects} />
              <Stat title="Plate Detections" value={result.total_plate_detections} />
            </div>

            {/* Video info */}
            <div className="vrs-card">
              <h2 className="vrs-heading">Video Information</h2>
              <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(120px, 1fr))", gap: "0.75rem" }}>
                <Info label="FPS"      value={result.video_info?.fps} />
                <Info label="Width"    value={result.video_info?.width} />
                <Info label="Height"   value={result.video_info?.height} />
                <Info label="Duration" value={`${result.video_info?.duration_seconds}s`} />
              </div>
            </div>

            {/* Vehicle type counts */}
            <div className="vrs-card">
              <h2 className="vrs-heading">Vehicle Type Counts</h2>
              {Object.keys(result.vehicle_type_counts || {}).length === 0 ? (
                <p style={{ color: "#6b7280", fontSize: "14px" }}>No vehicles found.</p>
              ) : (
                <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(140px, 1fr))", gap: "0.75rem" }}>
                  {Object.entries(result.vehicle_type_counts).map(([label, count]) => (
                    <Stat key={label} title={label} value={count} />
                  ))}
                </div>
              )}
            </div>

            {/* Plate texts */}
            <div className="vrs-card">
              <h2 className="vrs-heading">Plate Texts</h2>
              {!result.plate_texts?.length ? (
                <p style={{ color: "#6b7280", fontSize: "14px" }}>No plate text detected.</p>
              ) : (
                <div style={{ display: "flex", flexWrap: "wrap", gap: "10px" }}>
                  {result.plate_texts.map((plate, index) => (
                    <span key={index} className="vrs-plate">{plate}</span>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}
      </div>

      <AlertDialog
        isOpen={alertBox.isOpen}
        title={alertBox.title}
        message={alertBox.message}
        confirmText="OK"
        onConfirm={closeAlert}
        onCancel={closeAlert}
      />
    </>
  );
}

function Stat({ title, value }) {
  return (
    <div className="vrs-stat">
      <p className="vrs-stat__label">{title}</p>
      <h2 className="vrs-stat__value">{value ?? 0}</h2>
    </div>
  );
}

function Info({ label, value }) {
  return (
    <div className="vrs-info-item">
      <p className="vrs-info-label">{label}</p>
      <p className="vrs-info-value">{value}</p>
    </div>
  );
}

export default VideoDetection;