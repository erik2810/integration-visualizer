import { useEffect, useRef } from 'react';
import * as THREE from 'three';
import { COLORS } from '../utils/constants';

export const Visualization3D = ({ data }) => {
  const containerRef = useRef(null);
  const cleanupRef = useRef(null);

  useEffect(() => {
    if (!data || !containerRef.current) return;

    const container = containerRef.current;

    // Clean up previous scene
    if (cleanupRef.current) {
      cleanupRef.current();
    }

    const { width, height } = container.getBoundingClientRect();
    if (width < 10 || height < 10) return;

    const scene = new THREE.Scene();
    scene.background = new THREE.Color(COLORS.bg);
    const camera = new THREE.PerspectiveCamera(55, width / height, 0.1, 1000);
    camera.position.set(3, 3, 3);
    camera.lookAt(0, 0, 0);

    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(width, height);
    renderer.setPixelRatio(window.devicePixelRatio);
    container.innerHTML = '';
    container.appendChild(renderer.domElement);

    scene.add(new THREE.AmbientLight(0xffffff, 0.5));
    const dirLight = new THREE.DirectionalLight(0xffffff, 0.7);
    dirLight.position.set(5, 10, 5);
    scene.add(dirLight);
    scene.add(new THREE.AxesHelper(1.2));

    // Surface visualization
    if (data.surface) {
      const surf = data.surface;
      const rows = surf.x.length, cols = surf.x[0].length;
      let xMin = Infinity, xMax = -Infinity, yMin = Infinity, yMax = -Infinity, zMin = Infinity, zMax = -Infinity;
      for (let i = 0; i < rows; i++) for (let j = 0; j < cols; j++) {
        const sx = surf.x[i][j], sy = surf.y[i][j], sz = surf.z[i][j];
        if (isFinite(sx)) { xMin = Math.min(xMin, sx); xMax = Math.max(xMax, sx); }
        if (isFinite(sy)) { yMin = Math.min(yMin, sy); yMax = Math.max(yMax, sy); }
        if (isFinite(sz)) { zMin = Math.min(zMin, sz); zMax = Math.max(zMax, sz); }
      }
      const range = Math.max(xMax - xMin, yMax - yMin, zMax - zMin) || 1;
      const cx = (xMax + xMin) / 2, cy = (yMax + yMin) / 2, cz = (zMax + zMin) / 2;

      const geom = new THREE.BufferGeometry();
      const verts = [], colors = [], inds = [];
      for (let i = 0; i < rows; i++) for (let j = 0; j < cols; j++) {
        const x = (surf.x[i][j] - cx) / range * 2, y = (surf.y[i][j] - cy) / range * 2, z = (surf.z[i][j] - cz) / range * 2;
        verts.push(isFinite(x) ? x : 0, isFinite(z) ? z : 0, isFinite(y) ? y : 0);
        const t = isFinite(surf.z[i][j]) ? (surf.z[i][j] - zMin) / (zMax - zMin || 1) : 0.5;
        const c = new THREE.Color();
        c.setHSL(0.6 - t * 0.4, 0.8, 0.5);
        colors.push(c.r, c.g, c.b);
      }
      for (let i = 0; i < rows - 1; i++) for (let j = 0; j < cols - 1; j++) {
        const a = i * cols + j;
        inds.push(a, a + 1, a + cols, a + 1, a + cols + 1, a + cols);
      }
      geom.setAttribute('position', new THREE.Float32BufferAttribute(verts, 3));
      geom.setAttribute('color', new THREE.Float32BufferAttribute(colors, 3));
      geom.setIndex(inds);
      geom.computeVertexNormals();
      scene.add(new THREE.Mesh(geom, new THREE.MeshPhongMaterial({ vertexColors: true, side: THREE.DoubleSide, transparent: true, opacity: 0.85 })));
      scene.add(new THREE.LineSegments(new THREE.WireframeGeometry(geom), new THREE.LineBasicMaterial({ color: 0x000000, opacity: 0.1, transparent: true })));
    }

    // Point cloud
    if (data.points) {
      const pts = data.points, vals = data.values;
      let minV = Math.min(...vals.filter(isFinite)), maxV = Math.max(...vals.filter(isFinite));
      let xMin = Infinity, xMax = -Infinity, yMin = Infinity, yMax = -Infinity, zMin = Infinity, zMax = -Infinity;
      pts.forEach(([px, py, pz]) => {
        xMin = Math.min(xMin, px); xMax = Math.max(xMax, px);
        yMin = Math.min(yMin, py); yMax = Math.max(yMax, py);
        zMin = Math.min(zMin, pz); zMax = Math.max(zMax, pz);
      });
      const range = Math.max(xMax - xMin, yMax - yMin, zMax - zMin) || 1;
      const positions = [], colors = [];
      pts.forEach(([px, py, pz], i) => {
        positions.push((px - xMin) / range * 2 - 1, (pz - zMin) / range * 2 - 1, (py - yMin) / range * 2 - 1);
        const t = (vals[i] - minV) / (maxV - minV || 1);
        const c = new THREE.Color();
        c.setHSL(0.7 - t * 0.5, 0.9, 0.5);
        colors.push(c.r, c.g, c.b);
      });
      const pGeom = new THREE.BufferGeometry();
      pGeom.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
      pGeom.setAttribute('color', new THREE.Float32BufferAttribute(colors, 3));
      scene.add(new THREE.Points(pGeom, new THREE.PointsMaterial({ size: 0.04, vertexColors: true, transparent: true, opacity: 0.7 })));
    }

    // Curve
    if (data.curve) {
      const curveData = data.curve;
      const pts = [];
      for (let i = 0; i < curveData.x.length; i++) {
        pts.push(new THREE.Vector3(curveData.x[i], curveData.z[i], curveData.y[i]));
      }
      const lineGeom = new THREE.BufferGeometry().setFromPoints(pts);
      scene.add(new THREE.Line(lineGeom, new THREE.LineBasicMaterial({ color: 0x22d3ee, linewidth: 2 })));
    }

    // Vector field arrows
    const arrowData = data.arrows || data.field_arrows;
    if (arrowData && arrowData.length > 0) {
      arrowData.forEach(arr => {
        const dir = new THREE.Vector3(arr.direction[0], arr.direction[2], arr.direction[1]);
        const len = dir.length();
        if (len < 0.001) return;
        dir.normalize();
        const origin = new THREE.Vector3(arr.origin[0], arr.origin[2], arr.origin[1]);
        const arrowLen = Math.min(0.3, len * 0.3);
        scene.add(new THREE.ArrowHelper(dir, origin, arrowLen, 0xf59e0b, arrowLen * 0.3, arrowLen * 0.15));
      });
    }

    // Normal vectors
    if (data.normals && data.normals.length > 0) {
      data.normals.forEach(n => {
        const dir = new THREE.Vector3(n.direction[0], n.direction[2], n.direction[1]).normalize();
        const origin = new THREE.Vector3(n.origin[0], n.origin[2], n.origin[1]);
        scene.add(new THREE.ArrowHelper(dir, origin, 0.2, 0x10b981, 0.06, 0.03));
      });
    }

    // Field lines
    if (data.field_lines && data.field_lines.length > 0) {
      const lineColors = [0x22d3ee, 0x6366f1, 0x10b981, 0xf59e0b, 0xef4444];
      data.field_lines.forEach((line, idx) => {
        if (line.length < 2) return;
        const points = line.map(p => new THREE.Vector3(p[0], p[2], p[1]));
        const geometry = new THREE.BufferGeometry().setFromPoints(points);
        scene.add(new THREE.Line(geometry, new THREE.LineBasicMaterial({
          color: lineColors[idx % lineColors.length], linewidth: 2, transparent: true, opacity: 0.8,
        })));
        if (points.length >= 2) {
          const lastPt = points[points.length - 1];
          const prevPt = points[points.length - 2];
          const dir = new THREE.Vector3().subVectors(lastPt, prevPt).normalize();
          scene.add(new THREE.ArrowHelper(dir, lastPt, 0.1, lineColors[idx % lineColors.length], 0.08, 0.04));
        }
      });
    }

    // Mouse interaction
    let isDragging = false, prev = { x: 0, y: 0 }, rotation = { x: 0.5, y: 0.8 };
    let animating = true;

    const onDown = (e) => { isDragging = true; prev = { x: e.clientX, y: e.clientY }; };
    const onUp = () => { isDragging = false; };
    const onMove = (e) => {
      if (!isDragging) return;
      rotation.y += (e.clientX - prev.x) * 0.01;
      rotation.x += (e.clientY - prev.y) * 0.01;
      rotation.x = Math.max(-Math.PI / 2, Math.min(Math.PI / 2, rotation.x));
      prev = { x: e.clientX, y: e.clientY };
    };

    container.addEventListener('mousedown', onDown);
    container.addEventListener('mouseup', onUp);
    container.addEventListener('mousemove', onMove);
    container.addEventListener('mouseleave', onUp);

    const animate = () => {
      if (!animating) return;
      requestAnimationFrame(animate);
      camera.position.set(
        4 * Math.sin(rotation.y) * Math.cos(rotation.x),
        4 * Math.sin(rotation.x),
        4 * Math.cos(rotation.y) * Math.cos(rotation.x)
      );
      camera.lookAt(0, 0, 0);
      renderer.render(scene, camera);
    };
    animate();

    const cleanup = () => {
      animating = false;
      container.removeEventListener('mousedown', onDown);
      container.removeEventListener('mouseup', onUp);
      container.removeEventListener('mousemove', onMove);
      container.removeEventListener('mouseleave', onUp);
      renderer.dispose();
      // Dispose all geometries and materials in the scene
      scene.traverse((object) => {
        if (object.geometry) object.geometry.dispose();
        if (object.material) {
          if (Array.isArray(object.material)) {
            object.material.forEach(m => m.dispose());
          } else {
            object.material.dispose();
          }
        }
      });
    };

    cleanupRef.current = cleanup;

    return cleanup;
  }, [data]);

  return <div ref={containerRef} style={{ width: '100%', height: '380px', background: COLORS.bg, borderRadius: '8px', cursor: 'grab' }} />;
};
