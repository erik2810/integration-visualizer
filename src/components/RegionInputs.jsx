import { InputField, SelectField } from './InputFields';

export const VectorFieldInput = ({ field, onChange }) => (
  <div style={{ marginBottom: '12px' }}>
    <label className="section-label section-label--accent">
      Vector Field F = (Fx, Fy, Fz)
    </label>
    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '6px' }}>
      <InputField label="Fx" value={field.x} onChange={(v) => onChange({ ...field, x: v })} placeholder="-y" />
      <InputField label="Fy" value={field.y} onChange={(v) => onChange({ ...field, y: v })} placeholder="x" />
      <InputField label="Fz" value={field.z} onChange={(v) => onChange({ ...field, z: v })} placeholder="0" />
    </div>
  </div>
);

export const CurveInput = ({ curve, onChange, tRange, onTRangeChange }) => (
  <div style={{ marginBottom: '12px' }}>
    <label className="section-label section-label--accent">
      Curve r(t) = (x(t), y(t), z(t))
    </label>
    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '6px' }}>
      <InputField label="x(t)" value={curve.x} onChange={(v) => onChange({ ...curve, x: v })} placeholder="cos(t)" />
      <InputField label="y(t)" value={curve.y} onChange={(v) => onChange({ ...curve, y: v })} placeholder="sin(t)" />
      <InputField label="z(t)" value={curve.z} onChange={(v) => onChange({ ...curve, z: v })} placeholder="0" />
    </div>
    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '6px', marginTop: '6px' }}>
      <InputField label="t start" value={tRange.start} onChange={(v) => onTRangeChange({ ...tRange, start: v })} placeholder="0" />
      <InputField label="t end" value={tRange.end} onChange={(v) => onTRangeChange({ ...tRange, end: v })} placeholder="2*pi" />
    </div>
  </div>
);

export const SurfaceInput = ({ surface, onChange, uRange, vRange, onURangeChange, onVRangeChange }) => (
  <div style={{ marginBottom: '12px' }}>
    <label className="section-label section-label--accent">
      Surface r(u,v)
    </label>
    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '6px' }}>
      <InputField label="x(u,v)" value={surface.x} onChange={(v) => onChange({ ...surface, x: v })} placeholder="sin(u)*cos(v)" />
      <InputField label="y(u,v)" value={surface.y} onChange={(v) => onChange({ ...surface, y: v })} placeholder="sin(u)*sin(v)" />
      <InputField label="z(u,v)" value={surface.z} onChange={(v) => onChange({ ...surface, z: v })} placeholder="cos(u)" />
    </div>
    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr 1fr', gap: '6px', marginTop: '6px' }}>
      <InputField label="u0" value={uRange[0]} onChange={(v) => onURangeChange([v, uRange[1]])} placeholder="0" />
      <InputField label="u1" value={uRange[1]} onChange={(v) => onURangeChange([uRange[0], v])} placeholder="pi" />
      <InputField label="v0" value={vRange[0]} onChange={(v) => onVRangeChange([v, vRange[1]])} placeholder="0" />
      <InputField label="v1" value={vRange[1]} onChange={(v) => onVRangeChange([vRange[0], v])} placeholder="2*pi" />
    </div>
  </div>
);

export const Region1DInput = ({ bounds, onChange }) => (
  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '6px' }}>
    <InputField label="Lower (a)" value={bounds.lower} onChange={(v) => onChange({ ...bounds, lower: v })} placeholder="0" tooltip="Lower limit of integration" />
    <InputField label="Upper (b)" value={bounds.upper} onChange={(v) => onChange({ ...bounds, upper: v })} placeholder="1" tooltip="Upper limit of integration" />
  </div>
);

export const Region2DInput = ({ region, onChange }) => (
  <div>
    <SelectField label="Region Type" value={region.type} onChange={(type) => onChange({ ...region, type })} options={[
      { value: 'rectangle', label: 'Rectangle [a,b]x[c,d]' },
      { value: 'disk', label: 'Disk x^2+y^2<=r^2' },
      { value: 'type_1', label: 'Type 1: g(x)<=y<=h(x)' },
      { value: 'type_2', label: 'Type 2: g(y)<=x<=h(y)' },
    ]} />
    {region.type === 'rectangle' && (
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '6px' }}>
        <InputField label="x min" value={region.x_min || ''} onChange={(v) => onChange({ ...region, x_min: v })} />
        <InputField label="x max" value={region.x_max || ''} onChange={(v) => onChange({ ...region, x_max: v })} />
        <InputField label="y min" value={region.y_min || ''} onChange={(v) => onChange({ ...region, y_min: v })} />
        <InputField label="y max" value={region.y_max || ''} onChange={(v) => onChange({ ...region, y_max: v })} />
      </div>
    )}
    {region.type === 'disk' && (
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '6px' }}>
        <InputField label="Cx" value={region.center?.[0] ?? ''} onChange={(v) => onChange({ ...region, center: [v, region.center?.[1] || 0] })} />
        <InputField label="Cy" value={region.center?.[1] ?? ''} onChange={(v) => onChange({ ...region, center: [region.center?.[0] || 0, v] })} />
        <InputField label="r" value={region.radius || ''} onChange={(v) => onChange({ ...region, radius: v })} />
      </div>
    )}
    {region.type === 'type_1' && (
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '6px' }}>
        <InputField label="x min" value={region.x_min || ''} onChange={(v) => onChange({ ...region, x_min: v })} />
        <InputField label="x max" value={region.x_max || ''} onChange={(v) => onChange({ ...region, x_max: v })} />
        <InputField label="y lower" value={region.y_lower || ''} onChange={(v) => onChange({ ...region, y_lower: v })} tooltip="Lower bound g(x)" />
        <InputField label="y upper" value={region.y_upper || ''} onChange={(v) => onChange({ ...region, y_upper: v })} tooltip="Upper bound h(x)" />
      </div>
    )}
    {region.type === 'type_2' && (
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '6px' }}>
        <InputField label="y min" value={region.y_min || ''} onChange={(v) => onChange({ ...region, y_min: v })} />
        <InputField label="y max" value={region.y_max || ''} onChange={(v) => onChange({ ...region, y_max: v })} />
        <InputField label="x lower" value={region.x_lower || ''} onChange={(v) => onChange({ ...region, x_lower: v })} tooltip="Lower bound g(y)" />
        <InputField label="x upper" value={region.x_upper || ''} onChange={(v) => onChange({ ...region, x_upper: v })} tooltip="Upper bound h(y)" />
      </div>
    )}
  </div>
);

export const Region3DInput = ({ region, onChange }) => (
  <div>
    <SelectField label="Region Type" value={region.type} onChange={(type) => onChange({ ...region, type })} options={[
      { value: 'box', label: 'Box' }, { value: 'sphere', label: 'Sphere' }, { value: 'cylinder', label: 'Cylinder' },
    ]} />
    {region.type === 'box' && (
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '6px' }}>
        <InputField label="x min" value={region.x_min || ''} onChange={(v) => onChange({ ...region, x_min: v })} />
        <InputField label="x max" value={region.x_max || ''} onChange={(v) => onChange({ ...region, x_max: v })} />
        <InputField label="y min" value={region.y_min || ''} onChange={(v) => onChange({ ...region, y_min: v })} />
        <InputField label="y max" value={region.y_max || ''} onChange={(v) => onChange({ ...region, y_max: v })} />
        <InputField label="z min" value={region.z_min || ''} onChange={(v) => onChange({ ...region, z_min: v })} />
        <InputField label="z max" value={region.z_max || ''} onChange={(v) => onChange({ ...region, z_max: v })} />
      </div>
    )}
    {region.type === 'sphere' && (
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '6px' }}>
        <InputField label="Cx" value={region.center?.[0] ?? ''} onChange={(v) => onChange({ ...region, center: [v, region.center?.[1] || 0, region.center?.[2] || 0] })} />
        <InputField label="Cy" value={region.center?.[1] ?? ''} onChange={(v) => onChange({ ...region, center: [region.center?.[0] || 0, v, region.center?.[2] || 0] })} />
        <InputField label="Cz" value={region.center?.[2] ?? ''} onChange={(v) => onChange({ ...region, center: [region.center?.[0] || 0, region.center?.[1] || 0, v] })} />
        <InputField label="r" value={region.radius || ''} onChange={(v) => onChange({ ...region, radius: v })} />
      </div>
    )}
    {region.type === 'cylinder' && (
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '6px' }}>
        <InputField label="Cx" value={region.center?.[0] ?? ''} onChange={(v) => onChange({ ...region, center: [v, region.center?.[1] || 0] })} />
        <InputField label="Cy" value={region.center?.[1] ?? ''} onChange={(v) => onChange({ ...region, center: [region.center?.[0] || 0, v] })} />
        <InputField label="r" value={region.radius || ''} onChange={(v) => onChange({ ...region, radius: v })} />
        <InputField label="z min" value={region.z_min || ''} onChange={(v) => onChange({ ...region, z_min: v })} />
        <InputField label="z max" value={region.z_max || ''} onChange={(v) => onChange({ ...region, z_max: v })} />
      </div>
    )}
  </div>
);
