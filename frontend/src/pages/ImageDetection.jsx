import { useState } from "react";
import { Upload, ImageIcon } from "lucide-react";
import API from "../api/axiosInstance";
import AlertDialog from "../components/AlertDialog";

function ImageDetection() {
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

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
      showAlert("Image Required", "Please select an image");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    try {
      setLoading(true);
      setResult(null);
      const res = await API.post("/analyze/image", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      setResult(res.data);
    } catch (error) {
      showAlert("Detection Failed", error.response?.data?.detail || "Detection failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <div style={{ padding: "2rem", display: "flex", flexDirection: "column", gap: "2rem" }}>
        {/* Header */}
        <div>
          <h1 className="vrs-page-title">Image Detection</h1>
          <p className="vrs-page-sub">Upload an image to detect vehicles, persons and number plates</p>
        </div>

        {/* Upload form */}
        <form onSubmit={handleSubmit} className="vrs-card" style={{ display: "flex", flexDirection: "column", gap: "1.25rem" }}>
          <h3 className="vrs-heading">Select Image</h3>

          <label
            className="vrs-upload-zone"
            style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: "12px" }}
          >
            <Upload size={32} style={{ color: "#950101" }} />
            <div style={{ textAlign: "center" }}>
              <div style={{ fontWeight: 600, color: "#e5e7eb", fontSize: "14px" }}>
                {file ? file.name : "Click to upload image"}
              </div>
              <div style={{ fontSize: "12px", color: "#6b7280", marginTop: "4px" }}>
                {file ? `${(file.size / 1024).toFixed(1)} KB` : "JPG, PNG, WEBP supported"}
              </div>
            </div>
            <input
              type="file"
              accept="image/*"
              onChange={(e) => setFile(e.target.files[0])}
              style={{ display: "none" }}
            />
          </label>

          <button
            type="submit"
            disabled={loading}
            className="vrs-btn vrs-btn--primary"
            style={{ alignSelf: "flex-start" }}
          >
            {loading ? (
              <>
                <span className="vrs-spinner" style={{ width: "16px", height: "16px" }} />
                Processing...
              </>
            ) : (
              <>
                <ImageIcon size={16} />
                Analyze Image
              </>
            )}
          </button>
        </form>

        {/* Results */}
        {result && (
          <div style={{ display: "flex", flexDirection: "column", gap: "1.5rem" }} className="vrs-fade-in">
            <div className="vrs-card">
              <h2 className="vrs-heading">Detection Output</h2>
              <img
                src={result.output_image_url}
                alt="Detection Output"
                className="vrs-output-img"
              />
            </div>

            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(140px, 1fr))", gap: "1rem" }}>
              {[
                { label: "Total",    val: result.total_detections },
                { label: "Vehicles", val: result.total_vehicles },
                { label: "Persons",  val: result.total_persons },
                { label: "Plates",   val: result.total_number_plates },
              ].map(({ label, val }) => (
                <div key={label} className="vrs-stat">
                  <p className="vrs-stat__label">{label}</p>
                  <h2 className="vrs-stat__value">{val}</h2>
                </div>
              ))}
            </div>

            <ResultSection title="Vehicles"      data={result.vehicles}      type="vehicle" />
            <ResultSection title="Persons"       data={result.persons}       type="person" />
            <ResultSection title="Number Plates" data={result.number_plates} type="plate" />
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

function ResultSection({ title, data, type }) {
  return (
    <div className="vrs-card">
      <h2 className="vrs-heading">{title}</h2>

      {data.length === 0 ? (
        <p style={{ color: "#6b7280", fontSize: "14px" }}>No records found.</p>
      ) : (
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(240px, 1fr))", gap: "1rem" }}>
          {data.map((item, index) => (
            <div key={index} className="vrs-detail-card">
              {item.crop_url && (
                <img src={item.crop_url} alt="crop" />
              )}
              <div className="vrs-detail-row">
                <span className="vrs-detail-label">Label</span>
                <span className="vrs-detail-value">{item.label}</span>
              </div>
              <div className="vrs-detail-row">
                <span className="vrs-detail-label">Confidence</span>
                <span className="vrs-detail-value">{item.confidence || item.detection_confidence}</span>
              </div>
              {type === "vehicle" && (
                <div className="vrs-detail-row">
                  <span className="vrs-detail-label">Model</span>
                  <span className="vrs-detail-value">{item.vehicle_model || "Unknown"}</span>
                </div>
              )}
              {type === "person" && (
                <div className="vrs-detail-row">
                  <span className="vrs-detail-label">Person Type</span>
                  <span className="vrs-detail-value">{item.person_type || "Unknown"}</span>
                </div>
              )}
              {type === "plate" && (
                <div className="vrs-detail-row">
                  <span className="vrs-detail-label">Plate Text</span>
                  <span className="vrs-plate">{item.plate_text || "—"}</span>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default ImageDetection;