import { useState } from 'react';
import { INTEGRAL_TYPES } from './utils/constants';
import { useComputation } from './hooks/useComputation';
import { isDemoMode } from './utils/api';
import { ErrorBoundary } from './components/ErrorBoundary';
import { InputField, SelectField, Button, LoadingSpinner, ErrorMessage } from './components/InputFields';
import { VectorFieldInput, CurveInput, SurfaceInput, Region1DInput, Region2DInput, Region3DInput } from './components/RegionInputs';
import { ExamplesPanel } from './components/ExamplesPanel';
import { ResultDisplay, VectorOperationResult, TheoremResult, FieldLinesResult } from './components/ResultDisplay';
import { Visualization1D } from './components/Visualization1D';
import { Visualization3D } from './components/Visualization3D';

export default function App() {
  const [integralType, setIntegralType] = useState('1d');
  const [integrand, setIntegrand] = useState('x^2');
  const [bounds1D, setBounds1D] = useState({ lower: '0', upper: '1' });
  const [region2D, setRegion2D] = useState({ type: 'rectangle', x_min: '0', x_max: '1', y_min: '0', y_max: '1' });
  const [region3D, setRegion3D] = useState({ type: 'box', x_min: '0', x_max: '1', y_min: '0', y_max: '1', z_min: '0', z_max: '1' });
  const [vectorField, setVectorField] = useState({ x: '-y', y: 'x', z: '0' });
  const [curve, setCurve] = useState({ x: 'cos(t)', y: 'sin(t)', z: '0' });
  const [tRange, setTRange] = useState({ start: '0', end: '2*pi' });
  const [surface, setSurface] = useState({ x: 'sin(u)*cos(v)', y: 'sin(u)*sin(v)', z: 'cos(u)' });
  const [uRange, setURange] = useState(['0', 'pi/2']);
  const [vRange, setVRange] = useState(['0', '2*pi']);
  const [scalarField, setScalarField] = useState('x^2 + y^2 + z^2');
  const [vectorOp, setVectorOp] = useState('gradient');
  const [theoremType, setTheoremType] = useState('greens');
  const [P_field, setP_field] = useState('-y/2');
  const [Q_field, setQ_field] = useState('x/2');

  const { result, visualization, loading, error, compute } = useComputation();

  const handleCompute = () => {
    compute(integralType, {
      integrand, bounds1D, region2D, region3D, vectorField, curve, tRange,
      surface, uRange, vRange, scalarField, vectorOp, theoremType, P_field, Q_field,
    });
  };

  const handleExampleSelect = (ex) => {
    if (ex.type && integralType === 'physics') {
      const typeMap = {
        vector_field: 'vector_fields', flux: 'flux', line_vector: 'line_vector',
        line_scalar: 'line_scalar', '2d': '2d', '3d': '3d', '1d': '1d',
      };
      if (typeMap[ex.type]) setIntegralType(typeMap[ex.type]);
    }
    if (ex.integrand) setIntegrand(ex.integrand);
    if (ex.lower_bound) setBounds1D({ lower: ex.lower_bound, upper: ex.upper_bound });
    if (ex.region) {
      if (['box', 'sphere', 'cylinder'].includes(ex.region.type)) setRegion3D(ex.region);
      else setRegion2D(ex.region);
    }
    if (ex.vector_field) setVectorField(ex.vector_field);
    if (ex.curve) setCurve({ x: ex.curve.x || 'cos(t)', y: ex.curve.y || 'sin(t)', z: ex.curve.z || '0' });
    if (ex.t_start !== undefined) setTRange({ start: String(ex.t_start), end: String(ex.t_end) });
    if (ex.surface) setSurface(ex.surface);
    if (ex.u_range) setURange(ex.u_range.map(String));
    if (ex.v_range) setVRange(ex.v_range.map(String));
    if (ex.scalar_field) setScalarField(ex.scalar_field);
    if (ex.operation) setVectorOp(ex.operation);
    if (ex.P) setP_field(ex.P);
    if (ex.Q) setQ_field(ex.Q);
  };

  const needsIntegrand = ['1d', '2d', '3d', 'line_scalar', 'surface_scalar'].includes(integralType);
  const needsVectorField = ['line_vector', 'flux', 'vector_fields', 'physics', 'field_lines'].includes(integralType)
    || (integralType === 'vector_operations' && vectorOp !== 'gradient')
    || (integralType === 'theorems' && theoremType !== 'greens');
  const needsCurve = ['line_scalar', 'line_vector'].includes(integralType)
    || (integralType === 'theorems' && (theoremType === 'greens' || theoremType === 'stokes'));
  const needsSurface = ['surface_scalar', 'flux'].includes(integralType)
    || (integralType === 'theorems' && (theoremType === 'stokes' || theoremType === 'divergence'));

  return (
    <ErrorBoundary>
      <div>
        <header className="app-header">
          <h1>
            Integration &amp; Vector Calculus Visualizer
            {isDemoMode() && <span className="demo-badge">Demo</span>}
          </h1>
          <p>Compute integrals, line integrals, surface integrals, flux, and vector operations</p>
        </header>

        <main className="app-main">
          <aside className="sidebar">
            {/* Type Selector */}
            <div style={{ marginBottom: '16px' }}>
              <label className="section-label">Integral Type</label>
              <div className="type-grid">
                {INTEGRAL_TYPES.map(t => (
                  <button
                    key={t.value}
                    onClick={() => setIntegralType(t.value)}
                    className={`type-btn${integralType === t.value ? ' active' : ''}`}
                  >
                    <div className="icon">{t.label}</div>
                    <div className="desc">{t.desc}</div>
                  </button>
                ))}
              </div>
            </div>

            {integralType === 'vector_operations' && (
              <SelectField label="Operation" value={vectorOp} onChange={setVectorOp} options={[
                { value: 'gradient', label: 'Gradient' },
                { value: 'divergence', label: 'Divergence' },
                { value: 'curl', label: 'Curl' },
              ]} />
            )}

            {integralType === 'theorems' && (
              <SelectField label="Theorem" value={theoremType} onChange={setTheoremType} options={[
                { value: 'greens', label: "Green's Theorem (2D)" },
                { value: 'stokes', label: "Stokes' Theorem" },
                { value: 'divergence', label: "Divergence Theorem" },
              ]} />
            )}

            {integralType === 'theorems' && theoremType === 'greens' && (
              <div style={{ marginBottom: '12px' }}>
                <label className="section-label section-label--accent">
                  Line integral (P dx + Q dy)
                </label>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '6px' }}>
                  <InputField label="P(x,y)" value={P_field} onChange={setP_field} placeholder="-y/2" />
                  <InputField label="Q(x,y)" value={Q_field} onChange={setQ_field} placeholder="x/2" />
                </div>
              </div>
            )}

            {needsIntegrand && <InputField label="Integrand f" value={integrand} onChange={setIntegrand} placeholder="x^2 + y^2" />}

            {integralType === 'vector_operations' && vectorOp === 'gradient' && (
              <InputField label="Scalar Field f" value={scalarField} onChange={setScalarField} placeholder="x^2 + y^2 + z^2" />
            )}

            {needsVectorField && <VectorFieldInput field={vectorField} onChange={setVectorField} />}
            {needsCurve && <CurveInput curve={curve} onChange={setCurve} tRange={tRange} onTRangeChange={setTRange} />}
            {needsSurface && <SurfaceInput surface={surface} onChange={setSurface} uRange={uRange} vRange={vRange} onURangeChange={setURange} onVRangeChange={setVRange} />}

            {integralType === '1d' && <Region1DInput bounds={bounds1D} onChange={setBounds1D} />}
            {integralType === '2d' && <Region2DInput region={region2D} onChange={setRegion2D} />}
            {integralType === '3d' && <Region3DInput region={region3D} onChange={setRegion3D} />}

            <Button onClick={handleCompute} disabled={loading} style={{ width: '100%', marginTop: '16px' }}>
              {loading ? 'Computing...' : 'Compute'}
            </Button>

            <ExamplesPanel integralType={integralType} onSelect={handleExampleSelect} />
          </aside>

          <section className="content-area">
            {loading && <LoadingSpinner />}
            {error && <ErrorMessage message={error} />}

            {visualization && !loading && (
              <ErrorBoundary>
                <div>
                  <h3 className="viz-title">Visualization</h3>
                  {integralType === '1d'
                    ? <Visualization1D data={visualization} />
                    : <Visualization3D data={visualization} />
                  }
                  <p className="viz-caption">
                    {integralType === '1d' ? 'Cyan: curve, Purple: Riemann sum' :
                      needsCurve ? 'Cyan: curve, Orange: vector field' :
                        needsSurface ? 'Surface colored by height, Green: normals, Orange: field' :
                          'Drag to rotate. Colors indicate function values.'}
                  </p>
                </div>
              </ErrorBoundary>
            )}

            {result && !loading && <ResultDisplay result={result} />}
            {integralType === 'vector_operations' && result && !loading && <VectorOperationResult result={result} vectorOp={vectorOp} />}
            {integralType === 'theorems' && result && !loading && <TheoremResult result={result} />}
            {integralType === 'field_lines' && result && !loading && <FieldLinesResult result={result} />}

            {!visualization && !result && !loading && !error && (
              <div className="empty-state">
                <div className="icon">&#8747;</div>
                <p>Select an integral type, configure parameters, and click Compute</p>
              </div>
            )}
          </section>
        </main>
      </div>
    </ErrorBoundary>
  );
}
