import { COLORS } from '../utils/constants';

export const ResultDisplay = ({ result }) => {
  if (!result) return null;
  return (
    <div style={{ padding: '16px', background: COLORS.surface, border: `1px solid ${COLORS.border}`, borderRadius: '8px', marginTop: '16px' }}>
      <h4 style={{ margin: '0 0 12px 0', fontSize: '12px', fontWeight: '600', color: COLORS.textMuted, textTransform: 'uppercase' }}>Result</h4>
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
        <div style={{ padding: '12px', background: COLORS.bg, borderRadius: '6px' }}>
          <div style={{ fontSize: '10px', color: COLORS.textDim, marginBottom: '4px', textTransform: 'uppercase' }}>Numerical</div>
          <div style={{ fontSize: '20px', fontWeight: '700', color: COLORS.accent, fontFamily: "'JetBrains Mono', monospace" }}>
            {typeof result.numerical === 'number' ? result.numerical.toFixed(6) : result.numerical}
          </div>
          {result.error && <div style={{ fontSize: '10px', color: COLORS.textDim }}>+/- {result.error.toExponential(2)}</div>}
        </div>
        <div style={{ padding: '12px', background: COLORS.bg, borderRadius: '6px' }}>
          <div style={{ fontSize: '10px', color: COLORS.textDim, marginBottom: '4px', textTransform: 'uppercase' }}>Symbolic</div>
          <div style={{ fontSize: '14px', color: COLORS.text, fontFamily: "'JetBrains Mono', monospace", wordBreak: 'break-all' }}>
            {result.symbolic || 'N/A'}
          </div>
        </div>
      </div>
      {result.normal_vector && (
        <div style={{ marginTop: '12px', padding: '12px', background: COLORS.bg, borderRadius: '6px' }}>
          <div style={{ fontSize: '10px', color: COLORS.textDim, marginBottom: '4px', textTransform: 'uppercase' }}>Normal Vector</div>
          <div style={{ fontSize: '12px', color: COLORS.text, fontFamily: "'JetBrains Mono', monospace" }}>({result.normal_vector.join(', ')})</div>
        </div>
      )}
    </div>
  );
};

export const VectorOperationResult = ({ result, vectorOp }) => {
  if (!result?.result) return null;
  return (
    <div style={{ padding: '16px', background: COLORS.surface, border: `1px solid ${COLORS.border}`, borderRadius: '8px', marginTop: '16px' }}>
      <h4 style={{ margin: '0 0 12px 0', fontSize: '12px', fontWeight: '600', color: COLORS.textMuted, textTransform: 'uppercase' }}>
        {vectorOp === 'gradient' ? 'Gradient f' : vectorOp === 'divergence' ? 'Div F' : 'Curl F'}
      </h4>
      {typeof result.result === 'object' ? (
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '8px' }}>
          {['x', 'y', 'z'].map(k => (
            <div key={k} style={{ padding: '10px', background: COLORS.bg, borderRadius: '4px' }}>
              <div style={{ fontSize: '10px', color: COLORS.textDim }}>{k}</div>
              <div style={{ fontSize: '14px', color: COLORS.accent, fontFamily: 'monospace' }}>{result.result[k]}</div>
            </div>
          ))}
        </div>
      ) : (
        <div style={{ padding: '12px', background: COLORS.bg, borderRadius: '6px' }}>
          <div style={{ fontSize: '18px', color: COLORS.accent, fontFamily: 'monospace' }}>{result.result}</div>
        </div>
      )}
    </div>
  );
};

export const TheoremResult = ({ result }) => {
  if (!result) return null;
  return (
    <div style={{ padding: '16px', background: COLORS.surface, border: `1px solid ${COLORS.border}`, borderRadius: '8px', marginTop: '16px' }}>
      <h4 style={{ margin: '0 0 12px 0', fontSize: '14px', fontWeight: '600', color: COLORS.accent }}>
        {result.theorem || 'Theorem Verification'}
      </h4>
      <p style={{ fontSize: '12px', color: COLORS.textMuted, marginBottom: '12px' }}>{result.description}</p>

      {result.line_integral && (
        <IntegralBox label="Line Integral" value={result.line_integral} />
      )}
      {result.surface_integral && (
        <IntegralBox label="Surface Integral" value={result.surface_integral} />
      )}
      {result.flux_integral && (
        <IntegralBox label="Flux F dot n dS" value={result.flux_integral} />
      )}
      {result.volume_integral && (
        <IntegralBox label="Volume Integral div F dV" value={result.volume_integral} />
      )}

      {result.verification && (
        <div style={{ padding: '12px', background: `${COLORS.success}15`, border: `1px solid ${COLORS.success}40`, borderRadius: '6px', marginTop: '12px' }}>
          <div style={{ fontSize: '12px', color: COLORS.success, fontWeight: '600' }}>
            Verification: Difference = {result.verification.difference.toExponential(3)}
          </div>
        </div>
      )}

      {result.curl_z && (
        <div style={{ marginTop: '12px', padding: '12px', background: COLORS.bg, borderRadius: '6px' }}>
          <div style={{ fontSize: '10px', color: COLORS.textDim }}>dQ/dx - dP/dy =</div>
          <div style={{ fontSize: '14px', color: COLORS.text, fontFamily: 'monospace' }}>{result.curl_z}</div>
        </div>
      )}

      {result.curl_F && (
        <div style={{ marginTop: '12px', padding: '12px', background: COLORS.bg, borderRadius: '6px' }}>
          <div style={{ fontSize: '10px', color: COLORS.textDim }}>curl F =</div>
          <div style={{ fontSize: '12px', color: COLORS.text, fontFamily: 'monospace' }}>({result.curl_F.x}, {result.curl_F.y}, {result.curl_F.z})</div>
        </div>
      )}
    </div>
  );
};

const IntegralBox = ({ label, value }) => (
  <div style={{ marginBottom: '12px', padding: '12px', background: COLORS.bg, borderRadius: '6px' }}>
    <div style={{ fontSize: '10px', color: COLORS.textDim, textTransform: 'uppercase' }}>{label}</div>
    <div style={{ fontSize: '18px', color: COLORS.accent, fontFamily: 'monospace' }}>
      {typeof value.numerical === 'number' ? value.numerical.toFixed(6) : value.numerical}
    </div>
    {value.symbolic && <div style={{ fontSize: '11px', color: COLORS.textMuted }}>= {value.symbolic}</div>}
  </div>
);

export const FieldLinesResult = ({ result }) => {
  if (!result?.field_lines) return null;
  return (
    <div style={{ padding: '16px', background: COLORS.surface, border: `1px solid ${COLORS.border}`, borderRadius: '8px', marginTop: '16px' }}>
      <h4 style={{ margin: '0 0 8px 0', fontSize: '12px', fontWeight: '600', color: COLORS.textMuted, textTransform: 'uppercase' }}>Field Lines</h4>
      <p style={{ fontSize: '12px', color: COLORS.text }}>Generated {result.num_lines} streamlines</p>
      <p style={{ fontSize: '11px', color: COLORS.textDim }}>Field lines show the flow direction of the vector field</p>
    </div>
  );
};
