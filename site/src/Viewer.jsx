import React, { Suspense, useEffect, useMemo, useState } from "react";
import { Canvas, useThree } from "@react-three/fiber";
import { Bounds, ContactShadows, Environment, Lightformer, OrbitControls, useGLTF } from "@react-three/drei";
import * as THREE from "three";

// Studio lighting built from local light panels: no HDR download, so the site stays self-contained.
function Studio() {
  return (
    <Environment resolution={256} frames={1}>
      <Lightformer intensity={3} position={[0, 6, 0]} rotation-x={Math.PI / 2} scale={[12, 6, 1]} />
      <Lightformer intensity={2} position={[-6, 2, 3]} rotation-y={Math.PI / 2} scale={[8, 2, 1]} />
      <Lightformer intensity={2} position={[6, 2, -3]} rotation-y={-Math.PI / 2} scale={[8, 2, 1]} />
      <Lightformer intensity={1.2} color="#ff4b1f" position={[0, 1, -8]} scale={[12, 1.2, 1]} />
      <Lightformer form="ring" intensity={1.5} position={[4, 4, 6]} scale={3} />
    </Environment>
  );
}

function Model({ url, paint }) {
  const { scene } = useGLTF(url);
  // Clone once per scene so this viewer's paint never leaks into another viewer of the same file.
  const cloned = useMemo(() => {
    const s = scene.clone(true);
    s.traverse((o) => {
      if (!o.isMesh) return;
      o.castShadow = true;
      o.receiveShadow = true;
      o.material = o.material.clone();
    });
    return s;
  }, [scene]);
  useEffect(() => {
    cloned.traverse((o) => { if (o.isMesh && o.material.name === "body" && paint) o.material.color.set(paint); });
  }, [cloned, paint]);
  return <primitive object={cloned} />;
}

function ResetOnChange({ token }) {
  const controls = useThree((s) => s.controls);
  useEffect(() => { controls?.reset?.(); }, [token, controls]);
  return null;
}

const PAINTS = [
  { id: "bone", label: "Bone", color: "#e9e2d3" },
  { id: "carbon", label: "Carbon", color: "#1b1b1e" },
  { id: "orange", label: "Blood orange", color: "#d8401a" },
];

export default function Viewer({ vehicle, big = false }) {
  const [paint, setPaint] = useState(PAINTS[2].color);
  const [spin, setSpin] = useState(true);
  const [resetToken, setResetToken] = useState(0);
  const reduced = typeof matchMedia !== "undefined" && matchMedia("(prefers-reduced-motion: reduce)").matches;

  return (
    <div className={`stage ${big ? "stage--big" : ""}`}>
      <Canvas
        shadows
        dpr={[1, 2]}
        camera={{ position: [5.2, 2.2, 6.2], fov: 32 }}
        gl={{ antialias: true, toneMapping: THREE.ACESFilmicToneMapping }}
        aria-label={`3D model of ${vehicle.name}. Drag to orbit, scroll to zoom.`}
        role="img"
      >
        <Studio />
        <ambientLight intensity={0.25} />
        <directionalLight position={[5, 8, 4]} intensity={1.4} castShadow shadow-mapSize={[1024, 1024]} />
        <Suspense fallback={null}>
          <Bounds fit clip observe margin={1.15}>
            <Model url={vehicle.glb} paint={paint} />
          </Bounds>
        </Suspense>
        <ContactShadows position={[0, 0, 0]} opacity={0.65} scale={14} blur={2.4} far={3} />
        <mesh rotation-x={-Math.PI / 2} position={[0, -0.002, 0]} receiveShadow>
          <circleGeometry args={[7, 64]} />
          <meshStandardMaterial color="#141416" roughness={0.55} metalness={0.2} transparent opacity={0.85} />
        </mesh>
        <OrbitControls makeDefault enablePan={false} minDistance={3} maxDistance={16} maxPolarAngle={Math.PI / 2.05}
          autoRotate={spin && !reduced} autoRotateSpeed={0.6} />
        <ResetOnChange token={`${vehicle.slug}-${resetToken}`} />
      </Canvas>
      <div className="stage__controls">
        <div className="az-seg" role="group" aria-label="Paint">
          {PAINTS.map((p) => (
            <button key={p.id} type="button" aria-pressed={paint === p.color} onClick={() => setPaint(p.color)} title={p.label}>
              <span className="paint" style={{ background: p.color }} aria-hidden="true" />
              <span className="az-visually-hidden">{p.label}</span>
            </button>
          ))}
        </div>
        <button type="button" className="az-chip" aria-pressed={spin} onClick={() => setSpin((s) => !s)}>Turntable</button>
        <button type="button" className="az-chip" aria-pressed="false" onClick={() => setResetToken((t) => t + 1)}>Reset view</button>
      </div>
      <div className="stage__label az-muted small">Recreation · not factory CAD</div>
    </div>
  );
}
