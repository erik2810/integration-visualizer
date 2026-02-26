import { useState, useEffect } from 'react';
import { COLORS } from '../utils/constants';
import { fetchExamples } from '../utils/api';

export const ExamplesPanel = ({ integralType, onSelect }) => {
  const [examples, setExamples] = useState(null);
  const [physicsCategory, setPhysicsCategory] = useState('all');

  useEffect(() => {
    fetchExamples().then(setExamples).catch(() => {});
  }, []);

  if (!examples) return null;

  if (integralType === 'physics') {
    const physicsExamples = examples.physics || [];
    const categories = ['all', ...new Set(physicsExamples.map(e => e.category))];
    const filtered = physicsCategory === 'all' ? physicsExamples : physicsExamples.filter(e => e.category === physicsCategory);

    return (
      <div style={{ marginTop: '16px' }}>
        <h4 style={{ margin: '0 0 8px 0', fontSize: '11px', fontWeight: '600', color: COLORS.textMuted, textTransform: 'uppercase' }}>Physics Examples</h4>
        <div style={{ marginBottom: '8px' }}>
          <select value={physicsCategory} onChange={(e) => setPhysicsCategory(e.target.value)}
            style={{ padding: '6px 10px', background: COLORS.bg, border: `1px solid ${COLORS.border}`, borderRadius: '4px', color: COLORS.text, fontSize: '12px' }}>
            {categories.map(cat => (
              <option key={cat} value={cat}>{cat === 'all' ? 'All Categories' : cat.charAt(0).toUpperCase() + cat.slice(1)}</option>
            ))}
          </select>
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '4px', maxHeight: '300px', overflowY: 'auto' }}>
          {filtered.map((ex, i) => (
            <button key={i} onClick={() => onSelect(ex)}
              style={{ padding: '8px 10px', background: COLORS.bg, border: `1px solid ${COLORS.border}`, borderRadius: '4px', color: COLORS.text, fontSize: '11px', cursor: 'pointer', textAlign: 'left' }}>
              <div style={{ fontWeight: '600' }}>{ex.name}</div>
              <div style={{ fontSize: '10px', color: COLORS.textDim, marginTop: '2px' }}>{ex.description}</div>
              {ex.physics_note && <div style={{ fontSize: '9px', color: COLORS.accent, marginTop: '2px' }}>{ex.physics_note}</div>}
            </button>
          ))}
        </div>
      </div>
    );
  }

  if (integralType === 'theorems') {
    const theoremExamples = examples.theorems || [];
    return (
      <div style={{ marginTop: '16px' }}>
        <h4 style={{ margin: '0 0 8px 0', fontSize: '11px', fontWeight: '600', color: COLORS.textMuted, textTransform: 'uppercase' }}>Theorem Verification</h4>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
          {theoremExamples.map((ex, i) => (
            <button key={i} onClick={() => onSelect(ex)}
              style={{ padding: '8px 10px', background: COLORS.bg, border: `1px solid ${COLORS.border}`, borderRadius: '4px', color: COLORS.text, fontSize: '11px', cursor: 'pointer', textAlign: 'left' }}>
              <div style={{ fontWeight: '600' }}>{ex.name}</div>
              <div style={{ fontSize: '10px', color: COLORS.textDim, marginTop: '2px' }}>{ex.description}</div>
              {ex.expected && <div style={{ fontSize: '9px', color: COLORS.success, marginTop: '2px' }}>Expected: {ex.expected}</div>}
            </button>
          ))}
        </div>
      </div>
    );
  }

  const exList = examples[integralType] || [];
  if (exList.length === 0) return null;

  return (
    <div style={{ marginTop: '16px' }}>
      <h4 style={{ margin: '0 0 8px 0', fontSize: '11px', fontWeight: '600', color: COLORS.textMuted, textTransform: 'uppercase' }}>Examples</h4>
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
        {exList.slice(0, 12).map((ex, i) => (
          <button key={i} onClick={() => onSelect(ex)}
            style={{ padding: '6px 10px', background: COLORS.bg, border: `1px solid ${COLORS.border}`, borderRadius: '4px', color: COLORS.text, fontSize: '11px', cursor: 'pointer' }}
            title={ex.description || ''}>
            {ex.name}
          </button>
        ))}
      </div>
    </div>
  );
};
