import React, { useRef, useMemo, Suspense } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { OrbitControls, Text, Sphere, Line } from '@react-three/drei';
import * as THREE from 'three';

// Loading fallback
function Loader() {
  return (
    <mesh>
      <sphereGeometry args={[0.5, 32, 32]} />
      <meshStandardMaterial color="#4a9eff" />
    </mesh>
  );
}

// Position Point in 3D Strategic Space
function PositionPoint({ position, color, label, size = 0.3, isHighlighted }) {
  const meshRef = useRef();
  
  useFrame((state) => {
    if (meshRef.current && isHighlighted) {
      meshRef.current.scale.setScalar(1 + Math.sin(state.clock.elapsedTime * 3) * 0.2);
    }
  });

  return (
    <group position={position}>
      <Sphere ref={meshRef} args={[size]}>
        <meshStandardMaterial 
          color={color}
          emissive={color}
          emissiveIntensity={isHighlighted ? 0.8 : 0.3}
          metalness={0.5}
          roughness={0.2}
        />
      </Sphere>
      {isHighlighted && (
        <>
          <Text
            position={[0, size + 0.5, 0]}
            fontSize={0.3}
            color={color}
            anchorX="center"
            anchorY="middle"
            outlineWidth={0.02}
            outlineColor="#000000"
          >
            {label}
          </Text>
          {/* Glow effect */}
          <Sphere args={[size * 1.5]}>
            <meshBasicMaterial 
              color={color}
              transparent
              opacity={0.2}
            />
          </Sphere>
        </>
      )}
    </group>
  );
}

// Axis Lines and Labels
function AxisSystem() {
  const axisLength = 5;
  
  return (
    <>
      {/* X-axis - Material Balance */}
      <Line
        points={[[-axisLength, 0, 0], [axisLength, 0, 0]]}
        color="#ef4444"
        lineWidth={2}
      />
      <Text position={[axisLength + 1, 0, 0]} fontSize={0.4} color="#ef4444">
        Material →
      </Text>
      
      {/* Y-axis - King Safety */}
      <Line
        points={[[0, -axisLength, 0], [0, axisLength, 0]]}
        color="#22c55e"
        lineWidth={2}
      />
      <Text position={[0, axisLength + 1, 0]} fontSize={0.4} color="#22c55e">
        King Safety →
      </Text>
      
      {/* Z-axis - Piece Activity */}
      <Line
        points={[[0, 0, -axisLength], [0, 0, axisLength]]}
        color="#4a9eff"
        lineWidth={2}
      />
      <Text position={[0, 0, axisLength + 1]} fontSize={0.4} color="#4a9eff">
        Activity →
      </Text>
      
      {/* Origin marker */}
      <Sphere args={[0.1]} position={[0, 0, 0]}>
        <meshBasicMaterial color="#ffffff" />
      </Sphere>
    </>
  );
}

// Strategic Zones (colored regions)
function StrategicZones() {
  const zones = [
    { position: [3, 3, 3], color: '#22c55e', label: 'Winning', size: 1.5 },
    { position: [-3, -3, -3], color: '#ef4444', label: 'Losing', size: 1.5 },
    { position: [0, 0, 0], color: '#eab308', label: 'Equal', size: 1.2 },
    { position: [3, -2, 2], color: '#f97316', label: 'Risky', size: 1 },
    { position: [-2, 3, 2], color: '#967CB2', label: 'Solid', size: 1 },
  ];

  return zones.map((zone, i) => (
    <group key={i} position={zone.position}>
      <Sphere args={[zone.size]}>
        <meshStandardMaterial 
          color={zone.color}
          transparent
          opacity={0.15}
          side={THREE.DoubleSide}
        />
      </Sphere>
      <Text
        position={[0, 0, 0]}
        fontSize={0.25}
        color={zone.color}
        anchorX="center"
        anchorY="middle"
        outlineWidth={0.02}
        outlineColor="#000000"
      >
        {zone.label}
      </Text>
    </group>
  ));
}

// Path Trail showing position evolution
function PathTrail({ positions, color }) {
  const points = useMemo(() => {
    return positions.map(pos => new THREE.Vector3(...pos));
  }, [positions]);

  return (
    <Line
      points={points}
      color={color}
      lineWidth={3}
      transparent
      opacity={0.6}
      dashed
      dashScale={2}
      dashSize={0.2}
      gapSize={0.1}
    />
  );
}

// Animated particles showing strategic flow
function StrategicParticles() {
  const particlesRef = useRef();
  const particleCount = 50;
  
  const positions = useMemo(() => {
    const pos = new Float32Array(particleCount * 3);
    for (let i = 0; i < particleCount; i++) {
      pos[i * 3] = (Math.random() - 0.5) * 10;
      pos[i * 3 + 1] = (Math.random() - 0.5) * 10;
      pos[i * 3 + 2] = (Math.random() - 0.5) * 10;
    }
    return pos;
  }, []);

  useFrame((state) => {
    if (particlesRef.current) {
      particlesRef.current.rotation.y = state.clock.elapsedTime * 0.05;
    }
  });

  return (
    <points ref={particlesRef}>
      <bufferGeometry>
        <bufferAttribute
          attach="attributes-position"
          count={particleCount}
          array={positions}
          itemSize={3}
        />
      </bufferGeometry>
      <pointsMaterial
        size={0.05}
        color="#4a9eff"
        transparent
        opacity={0.4}
        sizeAttenuation
      />
    </points>
  );
}

// Main Scene
function Scene3D({ currentPosition, pathHistory, selectedPath }) {
  // Calculate position in strategic space
  const calculateStrategicPosition = (evalData) => {
    // X: Material balance (-5 to 5)
    const material = Math.max(-5, Math.min(5, (evalData.material || 0) / 200));
    
    // Y: King safety (0 to 5)
    const kingSafety = Math.max(-5, Math.min(5, (evalData.kingSafety || 2) - 2));
    
    // Z: Piece activity (0 to 5)
    const activity = Math.max(-5, Math.min(5, (evalData.activity || 2) - 2));
    
    return [material, kingSafety, activity];
  };

  const currentPos = calculateStrategicPosition(currentPosition);
  
  // Generate path history positions
  const pathPositions = useMemo(() => {
    const positions = [];
    for (let i = 0; i < 10; i++) {
      const t = i / 10;
      positions.push([
        currentPos[0] * t,
        currentPos[1] * t,
        currentPos[2] * t
      ]);
    }
    return positions;
  }, [currentPos]);

  const pathColors = {
    your: '#4a9eff',
    best: '#22c55e',
    aggressive: '#f97316',
    defensive: '#967CB2'
  };

  return (
    <>
      <ambientLight intensity={0.4} />
      <pointLight position={[10, 10, 10]} intensity={1} />
      <pointLight position={[-10, -10, -10]} intensity={0.5} />
      <spotLight position={[0, 10, 0]} angle={0.3} penumbra={1} intensity={0.8} />
      
      <AxisSystem />
      <StrategicZones />
      <StrategicParticles />
      
      {/* Path trail */}
      <PathTrail positions={pathPositions} color={pathColors[selectedPath]} />
      
      {/* Current position */}
      <PositionPoint
        position={currentPos}
        color={pathColors[selectedPath]}
        label="Current Position"
        size={0.4}
        isHighlighted={true}
      />
      
      {/* Reference positions */}
      <PositionPoint
        position={[0, 0, 0]}
        color="#888888"
        label="Starting Position"
        size={0.2}
        isHighlighted={false}
      />
      
      {/* Grid helper */}
      <gridHelper args={[10, 10, '#333333', '#1a1a1a']} />
      
      <OrbitControls 
        enablePan={true}
        enableZoom={true}
        enableRotate={true}
        minDistance={5}
        maxDistance={25}
        autoRotate={true}
        autoRotateSpeed={0.5}
      />
    </>
  );
}

// Main Component
export default function StrategicSpace3D({ currentPosition, pathHistory, selectedPath }) {
  return (
    <div style={{ 
      width: '100%', 
      height: '500px', 
      background: '#0a0a0a', 
      borderRadius: '12px', 
      overflow: 'hidden',
      position: 'relative'
    }}>
      <Canvas
        camera={{ position: [10, 8, 10], fov: 60 }}
        style={{ background: 'linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 100%)' }}
        gl={{ antialias: true }}
      >
        <Suspense fallback={<Loader />}>
          <Scene3D 
            currentPosition={currentPosition} 
            pathHistory={pathHistory}
            selectedPath={selectedPath}
          />
        </Suspense>
      </Canvas>
      <div style={{
        position: 'absolute',
        bottom: '20px',
        left: '50%',
        transform: 'translateX(-50%)',
        textAlign: 'center',
        color: '#888',
        fontSize: '12px',
        fontStyle: 'italic',
        background: 'rgba(0, 0, 0, 0.7)',
        padding: '8px 16px',
        borderRadius: '20px',
        backdropFilter: 'blur(10px)'
      }}>
        🖱️ Drag to rotate • Scroll to zoom • Auto-rotating
      </div>
      
      {/* Legend */}
      <div style={{
        position: 'absolute',
        top: '20px',
        right: '20px',
        background: 'rgba(0, 0, 0, 0.8)',
        padding: '15px',
        borderRadius: '10px',
        color: '#fff',
        fontSize: '12px',
        backdropFilter: 'blur(10px)',
        border: '1px solid rgba(74, 158, 255, 0.3)'
      }}>
        <div style={{ fontWeight: 'bold', marginBottom: '10px', color: '#4a9eff' }}>
          Strategic Dimensions
        </div>
        <div style={{ marginBottom: '5px' }}>
          <span style={{ color: '#ef4444' }}>●</span> Material Balance
        </div>
        <div style={{ marginBottom: '5px' }}>
          <span style={{ color: '#22c55e' }}>●</span> King Safety
        </div>
        <div>
          <span style={{ color: '#4a9eff' }}>●</span> Piece Activity
        </div>
      </div>
    </div>
  );
}
