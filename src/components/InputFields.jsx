import { useState } from 'react';

export const InfoTooltip = ({ text }) => {
  const [show, setShow] = useState(false);
  return (
    <span
      className="tooltip-wrap"
      onMouseEnter={() => setShow(true)}
      onMouseLeave={() => setShow(false)}
    >
      <span className="tooltip-icon">?</span>
      {show && <div className="tooltip-popup">{text}</div>}
    </span>
  );
};

export const InputField = ({ label, value, onChange, placeholder, tooltip }) => (
  <div className="field-group">
    <label className="field-label">
      {label}
      {tooltip && <InfoTooltip text={tooltip} />}
    </label>
    <input
      type="text"
      className="field-input"
      value={value}
      onChange={(e) => onChange(e.target.value)}
      placeholder={placeholder}
    />
  </div>
);

export const SelectField = ({ label, value, onChange, options, tooltip }) => (
  <div className="field-group">
    <label className="field-label">
      {label}
      {tooltip && <InfoTooltip text={tooltip} />}
    </label>
    <select
      className="field-select"
      value={value}
      onChange={(e) => onChange(e.target.value)}
    >
      {options.map(o => <option key={o.value} value={o.value}>{o.label}</option>)}
    </select>
  </div>
);

export const Button = ({ children, onClick, disabled, style = {} }) => (
  <button
    className="btn-primary"
    onClick={onClick}
    disabled={disabled}
    style={style}
  >
    {children}
  </button>
);

export const LoadingSpinner = () => (
  <div className="loading">
    <div className="spinner" />
    Computing...
  </div>
);

export const ErrorMessage = ({ message }) => (
  <div className="error-box">
    <strong>Error:</strong> {message}
  </div>
);
