import { useEffect, useRef } from 'react';
import * as THREE from 'three';

/**
 * A decorative, client-only scene. It intentionally contains no commerce data
 * or controls: the visual reinforces the agent network without becoming an
 * authority or execution surface.
 */
export const CommerceOrbit = () => {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    // Avoid touching the canvas in environments without a WebGL implementation
    // (for example, server rendering and DOM-only test environments).
    if (!window.WebGLRenderingContext && !window.WebGL2RenderingContext) return;

    const webglContext = canvas.getContext('webgl2') || canvas.getContext('webgl');
    if (!webglContext) return;

    let renderer: THREE.WebGLRenderer;
    try {
      renderer = new THREE.WebGLRenderer({ canvas, alpha: true, antialias: true });
    } catch {
      return;
    }

    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(40, 1, 0.1, 100);
    camera.position.set(0, 0, 8);

    const system = new THREE.Group();
    scene.add(system);

    const core = new THREE.Mesh(
      new THREE.IcosahedronGeometry(1.03, 3),
      new THREE.MeshBasicMaterial({ color: '#7dd3fc', wireframe: true, transparent: true, opacity: 0.9 }),
    );
    system.add(core);

    const coreHalo = new THREE.Mesh(
      new THREE.IcosahedronGeometry(0.78, 2),
      new THREE.MeshBasicMaterial({ color: '#a3e635', transparent: true, opacity: 0.1 }),
    );
    system.add(coreHalo);

    const orbitMaterial = new THREE.LineBasicMaterial({ color: '#38bdf8', transparent: true, opacity: 0.42 });
    const orbitDots: THREE.Mesh[] = [];
    [
      { radius: 2.0, tilt: 0.55, phase: 0 },
      { radius: 2.55, tilt: -0.7, phase: 1.7 },
      { radius: 3.1, tilt: 0.12, phase: 3.6 },
    ].forEach(({ radius, tilt, phase }, index) => {
      const curve = new THREE.EllipseCurve(0, 0, radius, radius * 0.34, 0, Math.PI * 2, false, 0);
      const points = curve.getPoints(80).map((point) => new THREE.Vector3(point.x, point.y, 0));
      const orbit = new THREE.LineLoop(new THREE.BufferGeometry().setFromPoints(points), orbitMaterial);
      orbit.rotation.x = tilt;
      orbit.rotation.z = index * 0.72;
      system.add(orbit);

      const dot = new THREE.Mesh(
        new THREE.SphereGeometry(0.1, 16, 16),
        new THREE.MeshBasicMaterial({ color: index === 1 ? '#a3e635' : '#f8fafc' }),
      );
      dot.userData = { radius, tilt, phase, rotationZ: index * 0.72, speed: 0.42 + index * 0.08 };
      system.add(dot);
      orbitDots.push(dot);
    });

    const particlesGeometry = new THREE.BufferGeometry();
    const particles = new Float32Array(180);
    for (let index = 0; index < particles.length; index += 3) {
      particles[index] = (Math.random() - 0.5) * 9;
      particles[index + 1] = (Math.random() - 0.5) * 7;
      particles[index + 2] = (Math.random() - 0.5) * 4 - 1;
    }
    particlesGeometry.setAttribute('position', new THREE.BufferAttribute(particles, 3));
    const particleField = new THREE.Points(
      particlesGeometry,
      new THREE.PointsMaterial({ color: '#7dd3fc', size: 0.035, transparent: true, opacity: 0.58 }),
    );
    scene.add(particleField);

    let pointerX = 0;
    let pointerY = 0;
    let frameId = 0;
    const onPointerMove = (event: PointerEvent) => {
      pointerX = (event.clientX / window.innerWidth - 0.5) * 0.45;
      pointerY = (event.clientY / window.innerHeight - 0.5) * 0.25;
    };
    window.addEventListener('pointermove', onPointerMove, { passive: true });

    const resize = () => {
      const { width, height } = canvas.getBoundingClientRect();
      if (width === 0 || height === 0) return;
      renderer.setSize(width, height, false);
      camera.aspect = width / height;
      camera.updateProjectionMatrix();
    };
    const resizeObserver = new ResizeObserver(resize);
    resizeObserver.observe(canvas);
    resize();

    const clock = new THREE.Clock();
    const render = () => {
      const elapsed = clock.getElapsedTime();
      system.rotation.y += (pointerX - system.rotation.y) * 0.025;
      system.rotation.x += (pointerY - system.rotation.x) * 0.025;
      core.rotation.x = elapsed * 0.18;
      core.rotation.z = elapsed * 0.12;
      coreHalo.scale.setScalar(1 + Math.sin(elapsed * 1.5) * 0.04);
      particleField.rotation.z = elapsed * 0.018;

      orbitDots.forEach((dot) => {
        const { radius, tilt, phase, rotationZ, speed } = dot.userData as Record<string, number>;
        const angle = elapsed * speed + phase;
        dot.position.set(radius * Math.cos(angle), radius * 0.34 * Math.sin(angle), 0);
        dot.position.applyAxisAngle(new THREE.Vector3(1, 0, 0), tilt);
        dot.position.applyAxisAngle(new THREE.Vector3(0, 0, 1), rotationZ);
      });

      renderer.render(scene, camera);
      frameId = window.requestAnimationFrame(render);
    };
    render();

    return () => {
      window.cancelAnimationFrame(frameId);
      window.removeEventListener('pointermove', onPointerMove);
      resizeObserver.disconnect();
      core.geometry.dispose();
      (core.material as THREE.Material).dispose();
      coreHalo.geometry.dispose();
      (coreHalo.material as THREE.Material).dispose();
      orbitDots.forEach((dot) => {
        dot.geometry.dispose();
        (dot.material as THREE.Material).dispose();
      });
      particlesGeometry.dispose();
      (particleField.material as THREE.Material).dispose();
      orbitMaterial.dispose();
      renderer.dispose();
    };
  }, []);

  return (
    <div className="absolute inset-y-0 right-0 hidden w-[54%] overflow-hidden lg:block" aria-hidden="true">
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,rgba(56,189,248,0.13),transparent_58%)]" />
      <canvas ref={canvasRef} className="h-full w-full" />
    </div>
  );
};
