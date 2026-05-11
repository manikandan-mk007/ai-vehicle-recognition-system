import { AlertTriangle, CheckCircle, Info, XCircle } from "lucide-react";

function AlertDialog({
  isOpen,
  type = "warning",
  title = "Notice",
  message = "",
  confirmText = "OK",
  cancelText = "Cancel",
  showCancel = false,
  onConfirm,
  onCancel,
}) {
  if (!isOpen) return null;

  const icons = {
    warning: <AlertTriangle size={22} />,
    success: <CheckCircle size={22} />,
    error: <XCircle size={22} />,
    info: <Info size={22} />,
  };

  const handleConfirm = () => {
    if (onConfirm) onConfirm();
  };

  const handleCancel = () => {
    if (onCancel) onCancel();
  };

  return (
    <div className="vrs-overlay" onClick={handleCancel}>
      <div
        className="vrs-dialog"
        onClick={(e) => e.stopPropagation()}
        role="alertdialog"
        aria-modal="true"
      >
        <div className={`vrs-dialog__icon vrs-dialog__icon--${type}`}>
          {icons[type] || icons.warning}
        </div>

        <p className="vrs-dialog__title">{title}</p>
        <p className="vrs-dialog__message">{message}</p>

        <div className="vrs-dialog__actions">
          {showCancel && (
            <button className="vrs-btn vrs-btn--ghost" onClick={handleCancel}>
              {cancelText}
            </button>
          )}

          <button
            className={
              type === "error" || type === "warning"
                ? "vrs-btn vrs-btn--danger"
                : "vrs-btn vrs-btn--primary"
            }
            onClick={handleConfirm}
            autoFocus
          >
            {confirmText}
          </button>
        </div>
      </div>
    </div>
  );
}

export default AlertDialog;