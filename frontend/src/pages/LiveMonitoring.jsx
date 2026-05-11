import { useRef, useState } from "react";
import { Camera, StopCircle, Video, Save, Radio } from "lucide-react";
import API from "../api/axiosInstance";

function LiveMonitoring() {
  const videoRef = useRef(null);
  const outputCanvasRef = useRef(null);
  const captureCanvasRef = useRef(null);
  const socketRef = useRef(null);
  const intervalRef = useRef(null);

  const mediaRecorderRef = useRef(null);
  const recordedChunksRef = useRef([]);

  const [isRunning, setIsRunning] = useState(false);
  const [isRecording, setIsRecording] = useState(false);

  const [enablePlateOCR, setEnablePlateOCR] = useState(false);
  const [saveLogs, setSaveLogs] = useState(false);

  const [stats, setStats] = useState({
    total_detections: 0,
    total_vehicles: 0,
    total_persons: 0,
    total_number_plates: 0,
  });

  const [recordingStats, setRecordingStats] = useState({
    max_vehicles: 0,
    max_persons: 0,
    max_plates: 0,
  });

  const [lastSavedSession, setLastSavedSession] = useState(null);
  const [recordedVideoUrl, setRecordedVideoUrl] = useState(null);
  const [error, setError] = useState("");

  const startMonitoring = async () => {
    try {
      setError("");

      const stream = await navigator.mediaDevices.getUserMedia({
        video: {
          width: 640,
          height: 480,
        },
        audio: false,
      });

      videoRef.current.srcObject = stream;
      await videoRef.current.play();

      const wsBaseUrl = import.meta.env.VITE_WS_BASE_URL;
      const wsUrl = `${wsBaseUrl}/api/live/webcam?enable_plate_ocr=${enablePlateOCR}&save_logs=${saveLogs}`;

      const socket = new WebSocket(wsUrl);
      socketRef.current = socket;

      socket.onopen = () => {
        setIsRunning(true);
        startSendingFrames();
      };

      socket.onmessage = (event) => {
        const data = JSON.parse(event.data);

        if (!data.success) {
          setError(data.message || "Live detection failed");
          return;
        }

        const currentStats = {
          total_detections: data.total_detections,
          total_vehicles: data.total_vehicles,
          total_persons: data.total_persons,
          total_number_plates: data.total_number_plates,
        };

        setStats(currentStats);

        setRecordingStats((prev) => ({
          max_vehicles: Math.max(prev.max_vehicles, data.total_vehicles),
          max_persons: Math.max(prev.max_persons, data.total_persons),
          max_plates: Math.max(prev.max_plates, data.total_number_plates),
        }));

        if (data.saved_session_id) {
          setLastSavedSession(data.saved_session_id);
        }

        drawProcessedFrame(data.processed_frame);
      };

      socket.onerror = () => {
        setError("WebSocket connection error. Check backend is running.");
      };

      socket.onclose = () => {
        setIsRunning(false);
      };
    } catch (err) {
      setError("Camera permission denied or camera not available.");
    }
  };

  const startSendingFrames = () => {
    intervalRef.current = setInterval(() => {
      sendFrame();
    }, 400);
  };

  const sendFrame = () => {
    const video = videoRef.current;
    const canvas = captureCanvasRef.current;
    const socket = socketRef.current;

    if (!video || !canvas || !socket) return;
    if (socket.readyState !== WebSocket.OPEN) return;

    const width = video.videoWidth || 640;
    const height = video.videoHeight || 480;

    canvas.width = width;
    canvas.height = height;

    const ctx = canvas.getContext("2d");
    ctx.drawImage(video, 0, 0, width, height);

    const imageData = canvas.toDataURL("image/jpeg", 0.75);

    socket.send(
      JSON.stringify({
        image: imageData,
      })
    );
  };

  const drawProcessedFrame = (imageBase64) => {
    const canvas = outputCanvasRef.current;
    const ctx = canvas.getContext("2d");

    const img = new window.Image();

    img.onload = () => {
      canvas.width = img.width;
      canvas.height = img.height;

      ctx.drawImage(img, 0, 0, img.width, img.height);
    };

    img.src = imageBase64;
  };

  const startRecording = () => {
    const canvas = outputCanvasRef.current;

    if (!canvas) {
      alert("Output canvas not ready.");
      return;
    }

    recordedChunksRef.current = [];
    setRecordedVideoUrl(null);
    setLastSavedSession(null);

    setRecordingStats({
      max_vehicles: 0,
      max_persons: 0,
      max_plates: 0,
    });

    const stream = canvas.captureStream(15);

    const options = {
      mimeType: "video/webm;codecs=vp9",
    };

    let mediaRecorder;

    try {
      mediaRecorder = new MediaRecorder(stream, options);
    } catch (error) {
      mediaRecorder = new MediaRecorder(stream);
    }

    mediaRecorderRef.current = mediaRecorder;

    mediaRecorder.ondataavailable = (event) => {
      if (event.data && event.data.size > 0) {
        recordedChunksRef.current.push(event.data);
      }
    };

    mediaRecorder.onstop = async () => {
      const blob = new Blob(recordedChunksRef.current, {
        type: "video/webm",
      });

      const localUrl = URL.createObjectURL(blob);
      setRecordedVideoUrl(localUrl);

      await uploadRecording(blob);
    };

    mediaRecorder.start();
    setIsRecording(true);
  };

  const stopRecording = () => {
    const recorder = mediaRecorderRef.current;

    if (recorder && recorder.state !== "inactive") {
      recorder.stop();
    }

    setIsRecording(false);
  };

  const uploadRecording = async (blob) => {
    try {
      const formData = new FormData();

      formData.append("file", blob, "live_webcam_recording.webm");

      const res = await API.post(
        `/live/upload-recording?total_vehicles=${recordingStats.max_vehicles}&total_persons=${recordingStats.max_persons}&total_number_plates=${recordingStats.max_plates}`,
        formData,
        {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        }
      );

      setLastSavedSession(res.data.session_id);
    } catch (error) {
      setError(error.response?.data?.detail || "Failed to upload recording.");
    }
  };

  const stopMonitoring = () => {
    if (isRecording) {
      stopRecording();
    }

    if (intervalRef.current) {
      clearInterval(intervalRef.current);
    }

    if (socketRef.current) {
      socketRef.current.close();
    }

    const stream = videoRef.current?.srcObject;

    if (stream) {
      stream.getTracks().forEach((track) => track.stop());
    }

    if (videoRef.current) {
      videoRef.current.srcObject = null;
    }

    setIsRunning(false);
  };

  return (
    <div className="live-page">
      {/* Header */}
      <div className="live-page-header">
        <h1 className="vrs-page-title">Live Monitoring</h1>
        <p className="vrs-page-sub">
          Real-time webcam detection with processed video recording
        </p>
      </div>

      {/* Error */}
      {error && (
        <div className="live-alert-error">
          {error}
        </div>
      )}

      {/* Controls */}
      <div className="live-control-card">
        <h3 className="vrs-heading">Live Detection Controls</h3>

        <div className="live-options">
          <label className="live-option">
            <input
              type="checkbox"
              checked={enablePlateOCR}
              disabled={isRunning}
              onChange={(e) => setEnablePlateOCR(e.target.checked)}
            />
            Enable Plate OCR
          </label>

          <label className="live-option">
            <input
              type="checkbox"
              checked={saveLogs}
              disabled={isRunning}
              onChange={(e) => setSaveLogs(e.target.checked)}
            />
            Save Photo Logs
          </label>
        </div>

        <div className="live-actions">
          {!isRunning ? (
            <button
              onClick={startMonitoring}
              className="vrs-btn vrs-btn--primary"
            >
              <Camera size={16} />
              Start Live Monitoring
            </button>
          ) : (
            <button
              onClick={stopMonitoring}
              className="vrs-btn vrs-btn--danger"
            >
              <StopCircle size={16} />
              Stop Monitoring
            </button>
          )}

          {isRunning && !isRecording && (
            <button
              onClick={startRecording}
              className="vrs-btn vrs-btn--success"
            >
              <Radio size={16} />
              Start Recording
            </button>
          )}

          {isRunning && isRecording && (
            <button
              onClick={stopRecording}
              className="vrs-btn vrs-btn--primary"
            >
              <Save size={16} />
              Stop Recording & Save
            </button>
          )}
        </div>
      </div>

      {/* Stats */}
      <div className="live-grid-stats">
        <Stat title="Total" value={stats.total_detections} />
        <Stat title="Vehicles" value={stats.total_vehicles} />
        <Stat title="Persons" value={stats.total_persons} />
        <Stat title="Plates" value={stats.total_number_plates} />
      </div>

      {/* Recording status */}
      {isRecording && (
        <div className="live-alert-warning">
          Recording processed AI output video...
        </div>
      )}

      {/* Saved session status */}
      {lastSavedSession && (
        <div className="live-alert-success">
          Recorded webcam video saved as Session #{lastSavedSession}
        </div>
      )}

      {/* Video panels */}
      <div className="live-video-grid">
        <div className="live-video-card">
          <h2 className="live-video-title">Webcam Input</h2>

          <video
            ref={videoRef}
            className="live-video-box"
            muted
            playsInline
          />
        </div>

        <div className="live-video-card">
          <h2 className="live-video-title">AI Detection Output</h2>

          <canvas
            ref={outputCanvasRef}
            className="live-video-box"
          />
        </div>
      </div>

      {/* Recorded video */}
      {recordedVideoUrl && (
        <div className="live-recorded-card">
          <h2 className="live-video-title">Recorded Processed Video</h2>

          <video
            src={recordedVideoUrl}
            controls
            className="live-video-box"
          />
        </div>
      )}

      <canvas ref={captureCanvasRef} style={{ display: "none" }} />
    </div>
  );
}

function Stat({ title, value }) {
  return (
    <div className="live-stat-card">
      <p className="live-stat-label">{title}</p>
      <h2 className="live-stat-value">{value}</h2>
    </div>
  );
}

export default LiveMonitoring;