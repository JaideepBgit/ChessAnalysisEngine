import React, { useRef, useMemo, Suspense } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { OrbitControls, Text, Line, Sphere } from '@react-three/drei';
import * as THREE from 'three';

// Loading fallback
function Loader() {
  return (
    <mesh>
      <boxGeometry args={[1, 1, 1]} />
      <meshStandardMaterial color="#4a9eff" />
    </mesh>
  );
}

// 3D Surface for Position Evaluation over Time
function EvaluationSurface({ moves, selectedPath, pathData }) {
  const meshRef = useRef();
  
  useFrame((state) => {
    if (meshRef.current) {
      meshRef.current.rotation.z = Math.sin(state.clock.elapsedTime * 0.2) * 0.05;
    }
  });

  const geometry = useMemo(() => {
    const geo = new THREE.BufferGeometry();
    const vertices = [];
    const colors = [];
    const indices = [];
    
    const steps = 20; // 20 moves
    const width = 10;
    
    for (let i = 0; i <= steps; i++) {
      const x = (i / steps) * width - width / 2;
      const eval1 = pathData[i] || 0;
      const complexity = Math.sin(i * 0.5) * 0.5 + 1.5; // Simulated complexity
      
      // Create two rows for surface
      vertices.push(x, eval1, -complexity);
      vertices.push(x, eval1, complexity);
      
      // Color based on evaluation
      const color = new THREE.Color();
      if (eval1 > 1) {
        color.setHSL(0.3, 0.8, 0.5); // Green
      } else if (eval1 > 0) {
        color.setHSL(0.15, 0.8, 0.6); // Yellow
      } else if (eval1 > -1) {
        color.setHSL(0.08, 0.8, 0.5); // Orange
      } else {
        color.setHSL(0, 0.8, 0.5); // Red
      }
      
      colors.push(color.r, color.g, color.b);
      colors.push(color.r, color.g, color.b);
      
      // Create triangles
      if (i < steps) {
        const base = i * 2;
        indices.push(base, base + 1, base + 2);
        indices.push(base + 1, base + 3, base + 2);
      }
    }
    
    geo.setAttribute('position', new THREE.Float32BufferAttribute(vertices, 3));
    geo.setAttribute('color', new THREE.Float32BufferAttribute(colors, 3));
    geo.setIndex(indices);
    geo.computeVertexNormals();
    
    return geo;
  }, [pathData]);

  return (
    <mesh ref={meshRef} geometry={geometry}>
      <meshStandardMaterial 
        vertexColors 
        side={THREE.DoubleSide}
        metalness={0.3}
        roughness={0.4}
        transparent
        opacity={0.9}
      />
    </mesh>
  );
}

// 3D Path Lines
function PathLine({ pathData, color, isSelected }) {
  const points = useMemo(() => {
    return pathData.map((y, i) => {
      const x = (i / 20) * 10 - 5;
      const z = 0;
      return new THREE.Vector3(x, y, z);
    });
  }, [pathData]);

  return (
    <Line
      points={points}
      color={color}
      lineWidth={isSelected ? 4 : 2}
      transparent
      opacity={isSelected ? 1 : 0.4}
    />
  );
}

// Move Markers
function MoveMarkers({ pathData, color, isSelected }) {
  return pathData.map((y, i) => {
    if (i % 5 !== 0) return null; // Show every 5th move
    
    const x = (i / 20) * 10 - 5;
    const z = 0;
    
    return (
      <group key={i} position={[x, y, z]}>
        <Sphere args={[isSelected ? 0.15 : 0.08]} position={[0, 0, 0]}>
          <meshStandardMaterial 
            color={color} 
            emissive={color}
            emissiveIntensity={isSelected ? 0.5 : 0.2}
          />
        </Sphere>
        {isSelected && (
          <Text
            position={[0, 0.5, 0]}
            fontSize={0.3}
            color={color}
            anchorX="center"
            anchorY="middle"
          >
            +{i}
          </Text>
        )}
      </group>
    );
  });
}

// Grid Helper
function CustomGrid() {
  return (
    <>
      <gridHelper args={[12, 20, '#444444', '#222222']} rotation={[Math.PI / 2, 0, 0]} />
      <gridHelper args={[12, 20, '#444444', '#222222']} />
    </>
  );
}

// Axis Labels
function AxisLabels() {
  return (
    <>
      {/* X-axis label */}
      <Text position={[6, -3, 0]} fontSize={0.4} color="#888">
        Move Number →
      </Text>
      
      {/* Y-axis label */}
      <Text position={[-6, 0, 0]} fontSize={0.4} color="#888" rotation={[0, 0, Math.PI / 2]}>
        Evaluation →
      </Text>
      
      {/* Z-axis label */}
      <Text position={[0, -3, 3]} fontSize={0.4} color="#888">
        Complexity →
      </Text>
    </>
  );
}

// Main 3D Scene
function Scene3D({ paths, selectedPath }) {
  const pathColors = {
    your: '#4a9eff',
    best: '#22c55e',
    aggressive: '#f97316',
    defensive: '#967CB2'
  };

  return (
    <>
      <ambientLight intensity={0.5} />
      <pointLight position={[10, 10, 10]} intensity={1} />
      <pointLight position={[-10, -10, -10]} intensity={0.5} />
      <spotLight position={[0, 10, 0]} angle={0.3} penumbra={1} intensity={1} castShadow />
      
      <CustomGrid />
      <AxisLabels />
      
      {/* Evaluation Surface for selected path */}
      <EvaluationSurface 
        pathData={paths[selectedPath].data} 
        selectedPath={selectedPath}
      />
      
      {/* All path lines */}
      {Object.entries(paths).map(([key, path]) => (
        <React.Fragment key={key}>
          <PathLine 
            pathData={path.data} 
            color={pathColors[key]}
            isSelected={key === selectedPath}
          />
          <MoveMarkers 
            pathData={path.data}
            color={pathColors[key]}
            isSelected={key === selectedPath}
          />
        </React.Fragment>
      ))}
      
      <OrbitControls 
        enablePan={true}
        enableZoom={true}
        enableRotate={true}
        minDistance={5}
        maxDistance={20}
        autoRotate={false}
        autoRotateSpeed={0.5}
      />
    </>
  );
}

// Main Component
export default function PositionEvaluation3D({ paths, selectedPath }) {
  return (
    <div style={{ width: '100%', height: '500px', background: '#0a0a0a', borderRadius: '12px', overflow: 'hidden' }}>
      <Canvas
        camera={{ position: [8, 6, 8], fov: 60 }}
        style={{ background: 'linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 100%)' }}
        gl={{ antialias: true }}
      >
        <Suspense fallback={<Loader />}>
          <Scene3D paths={paths} selectedPath={selectedPath} />
        </Suspense>
      </Canvas>
      <div style={{
        position: 'relative',
        marginTop: '-40px',
        textAlign: 'center',
        color: '#888',
        fontSize: '12px',
        fontStyle: 'italic',
        zIndex: 10,
        pointerEvents: 'none'
      }}>
        🖱️ Drag to rotate • Scroll to zoom • Right-click to pan
      </div>
    </div>
  );
}
