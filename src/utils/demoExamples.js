/** Subset of examples for demo mode. Mirrors backend/examples.py structure. */

export const DEMO_EXAMPLES = {
  '1d': [
    { name: 'Polynomial', integrand: 'x^2', lower_bound: '0', upper_bound: '1' },
    { name: 'Trigonometric', integrand: 'sin(x)', lower_bound: '0', upper_bound: 'pi' },
    { name: 'Gaussian', integrand: 'exp(-x^2)', lower_bound: '-3', upper_bound: '3' },
    { name: 'Rational', integrand: '1/(1+x^2)', lower_bound: '-10', upper_bound: '10' },
  ],
  '2d': [
    { name: 'Rectangle - Polynomial', integrand: 'x^2 + y^2', region: { type: 'rectangle', x_min: 0, x_max: 1, y_min: 0, y_max: 1 } },
    { name: 'Disk - Area (pi)', integrand: '1', region: { type: 'disk', center: [0, 0], radius: 1 } },
  ],
  '3d': [
    { name: 'Unit Cube Volume', integrand: '1', region: { type: 'box', x_min: 0, x_max: 1, y_min: 0, y_max: 1, z_min: 0, z_max: 1 } },
    { name: 'Sphere Volume (4pi/3)', integrand: '1', region: { type: 'sphere', center: [0, 0, 0], radius: 1 } },
  ],
  'line_scalar': [
    { name: 'Circle Arc Length (2pi)', integrand: '1', curve: { x: 'cos(t)', y: 'sin(t)', z: '0' }, t_start: 0, t_end: '2*pi', description: 'Circumference of unit circle' },
  ],
  'line_vector': [
    { name: 'Circulation (2pi)', vector_field: { x: '-y', y: 'x', z: '0' }, curve: { x: 'cos(t)', y: 'sin(t)', z: '0' }, t_start: 0, t_end: '2*pi', description: 'Vortex field circulation' },
  ],
  'surface_scalar': [
    { name: 'Hemisphere Area (2pi)', integrand: '1', surface: { x: 'sin(u)*cos(v)', y: 'sin(u)*sin(v)', z: 'cos(u)' }, u_range: [0, 'pi/2'], v_range: [0, '2*pi'], description: 'Upper hemisphere' },
  ],
  'flux': [
    { name: 'Radial Flux (Hemisphere)', vector_field: { x: 'x', y: 'y', z: 'z' }, surface: { x: 'sin(u)*cos(v)', y: 'sin(u)*sin(v)', z: 'cos(u)' }, u_range: [0, 'pi/2'], v_range: [0, '2*pi'], description: 'F = r through hemisphere' },
  ],
  'vector_operations': [
    { name: 'Gradient: Distance', operation: 'gradient', scalar_field: 'sqrt(x^2 + y^2 + z^2)', description: 'grad r = r_hat' },
    { name: 'Divergence: Position', operation: 'divergence', vector_field: { x: 'x', y: 'y', z: 'z' }, description: 'div r = 3' },
    { name: 'Curl: Rotation', operation: 'curl', vector_field: { x: '-y', y: 'x', z: '0' }, description: 'curl(-y,x,0) = 2k_hat' },
  ],
  'vector_fields': [
    { name: 'Radial Source', vector_field: { x: 'x', y: 'y', z: 'z' }, region: { x_min: -2, x_max: 2, y_min: -2, y_max: 2, z_min: -2, z_max: 2 }, description: 'Expanding flow' },
    { name: 'Vortex (z-axis)', vector_field: { x: '-y', y: 'x', z: '0' }, region: { x_min: -2, x_max: 2, y_min: -2, y_max: 2, z_min: -1, z_max: 1 }, description: 'Rotation about z' },
  ],
  'physics': [
    { name: 'Point Charge E-field', category: 'electromagnetism', type: 'vector_field', vector_field: { x: 'x/(x^2+y^2+z^2)^(3/2)', y: 'y/(x^2+y^2+z^2)^(3/2)', z: 'z/(x^2+y^2+z^2)^(3/2)' }, description: 'E = kq/r^2 radial field', physics_note: 'Coulombs law' },
    { name: 'Gravitational Field', category: 'mechanics', type: 'vector_field', vector_field: { x: '-x/(x^2+y^2+z^2)^(3/2)', y: '-y/(x^2+y^2+z^2)^(3/2)', z: '-z/(x^2+y^2+z^2)^(3/2)' }, description: 'g = -GM/r^2 radial', physics_note: 'Newtons gravitation' },
  ],
  'theorems': [
    { name: "Green's Theorem (Area)", type: 'greens', vector_field: { x: '-y/2', y: 'x/2' }, curve: { x: 'cos(t)', y: 'sin(t)' }, t_start: 0, t_end: '2*pi', description: 'oint(-y dx + x dy)/2 = Area', expected: 'pi' },
    { name: 'Divergence Theorem', type: 'divergence', vector_field: { x: 'x', y: 'y', z: 'z' }, surface: { x: 'sin(u)*cos(v)', y: 'sin(u)*sin(v)', z: 'cos(u)' }, u_range: [0, 'pi'], v_range: [0, '2*pi'], description: 'iint F.n dS = iiint div F dV', expected: '4pi (since div r = 3)' },
  ],
};
