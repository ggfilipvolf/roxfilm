/* Roxfilm – 3D X z loga před sekcí reels (three.js, scroll řídí kameru) */
import * as THREE from 'three';
import { RoomEnvironment } from './three/RoomEnvironment.js';
import { Reflector } from './three/Reflector.js';

const q = new URLSearchParams(location.search);
const MODE = 'white';
const FIXED = q.has('p') ? parseFloat(q.get('p')) : null;

const sec = document.getElementById('reels-x');
if (!sec) throw 0;
const canvas = sec.querySelector('canvas');
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, powerPreference: 'high-performance' });
renderer.setPixelRatio(Math.min(devicePixelRatio || 1, 2));
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.0;
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;

const scene = new THREE.Scene();
const INK = new THREE.Color('#0F0F0E');
scene.background = INK;
scene.fog = new THREE.Fog(INK, 1500, 3200);
const pmrem = new THREE.PMREMGenerator(renderer);
scene.environment = pmrem.fromScene(new RoomEnvironment(), 0.04).texture;
scene.environmentIntensity = MODE === 'chrome' ? 0.9 : 0.35;

// --- X z loga: dvě poloviny přesně podle polygonů z brand manuálu ---
const L = [[0,0],[123,0],[144,124],[123,248],[0,248],[100,124]];
const R = [[22,0],[139,0],[42,124],[139,248],[22,248],[0,124]];
const OX = 158;                       // mezera mezi polovinami jako v logu
const shape = (pts, ox) => { const s = new THREE.Shape(); pts.forEach(([x, y], i) => { const X = x + ox, Y = 248 - y; i ? s.lineTo(X, Y) : s.moveTo(X, Y); }); s.closePath(); return s; };
const extr = { depth: 46, bevelEnabled: true, bevelThickness: 2.2, bevelSize: 1.8, bevelSegments: 4, curveSegments: 1 };
const mats = {
  white: new THREE.MeshPhysicalMaterial({ color: '#F2F0EB', roughness: 0.42, metalness: 0, clearcoat: 0.35, clearcoatRoughness: 0.4 }),
  black: new THREE.MeshPhysicalMaterial({ color: '#141413', roughness: 0.22, metalness: 0.15, clearcoat: 1, clearcoatRoughness: 0.12 }),
  chrome: new THREE.MeshPhysicalMaterial({ color: '#d9d7d2', roughness: 0.12, metalness: 1 }),
};
const mat = mats[MODE] || mats.white;
const xg = new THREE.Group();
[[L, 0], [R, OX]].forEach(([pts, ox]) => {
  const g = new THREE.ExtrudeGeometry(shape(pts, ox), extr);
  const m = new THREE.Mesh(g, mat); m.castShadow = true; m.receiveShadow = true; xg.add(m);
});
const W = OX + 139;
xg.position.set(-W / 2, 0, -23);       // střed X v počátku, stojí na podlaze
scene.add(xg);

// lesklá tmavá podlaha: zrcadlo + ztmavující vrstva = odraz X jako na mokrém betonu
const mirror = new Reflector(new THREE.PlaneGeometry(9000, 9000), { textureWidth: 1024 * Math.min(devicePixelRatio || 1, 2), textureHeight: 1024 * Math.min(devicePixelRatio || 1, 2), color: 0x3a3a38 });
mirror.rotation.x = -Math.PI / 2; mirror.position.y = -0.5; scene.add(mirror);
const floor = new THREE.Mesh(new THREE.PlaneGeometry(9000, 9000), new THREE.MeshStandardMaterial({ color: '#0F0F0E', roughness: 0.6, metalness: 0, transparent: true, opacity: 0.82 }));
floor.rotation.x = -Math.PI / 2; floor.receiveShadow = true; scene.add(floor);

// světla: úzký kužel shora (dramatický stín), kontra zezadu, minimum fill
const key = new THREE.SpotLight('#ffffff', 3.2e6, 0, Math.PI / 13, 0.55, 2);
key.position.set(-120, 1600, 260); key.target.position.set(0, 0, 0);
key.castShadow = true; key.shadow.mapSize.set(2048, 2048); key.shadow.bias = -0.0004; key.shadow.radius = 5;
scene.add(key, key.target);
const rim = new THREE.SpotLight('#e6ecff', 2.4e6, 0, Math.PI / 9, 0.5, 2);
rim.position.set(640, 420, -1000); rim.target.position.set(0, 130, 0); scene.add(rim, rim.target);
const rim2 = new THREE.SpotLight('#ffffff', 1.4e6, 0, Math.PI / 9, 0.5, 2);
rim2.position.set(-700, 300, -800); rim2.target.position.set(0, 130, 0); scene.add(rim2, rim2.target);
const fill = new THREE.HemisphereLight('#ffffff', '#0F0F0E', 0.12); scene.add(fill);

// viditelný paprsek světla shora (jemný, aditivní)
const beamMat = new THREE.ShaderMaterial({
  transparent: true, depthWrite: false, blending: THREE.AdditiveBlending, side: THREE.DoubleSide,
  uniforms: { uO: { value: 0.11 } },
  vertexShader: 'varying vec2 vUv; varying vec3 vN; varying vec3 vV; void main(){ vUv=uv; vN=normalize(normalMatrix*normal); vec4 mv=modelViewMatrix*vec4(position,1.); vV=normalize(-mv.xyz); gl_Position=projectionMatrix*mv; }',
  fragmentShader: 'uniform float uO; varying vec2 vUv; varying vec3 vN; varying vec3 vV; void main(){ float edge=pow(abs(dot(vN,vV)),2.2); float h=smoothstep(0.,1.,vUv.y); gl_FragColor=vec4(vec3(1.),uO*edge*h); }'
});
const beam = new THREE.Mesh(new THREE.CylinderGeometry(18, 330, 1500, 48, 1, true), beamMat);
beam.position.set(-130, 750, 190); beam.lookAt(key.position.x, 1500 + 750, key.position.z);
beam.position.copy(key.position).add(new THREE.Vector3(0, 0, 0)).lerp(new THREE.Vector3(0, 0, 0), 0.5);
beam.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), key.position.clone().sub(new THREE.Vector3(0, 0, 0)).normalize());
scene.add(beam);

// kamera: shora → kran dolů → zastaví přesně před X
const cam = new THREE.PerspectiveCamera(32, 1, 1, 10000);
const look = new THREE.Vector3();
const ease = t => t < .5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;
const clamp = (v, a = 0, b = 1) => Math.min(b, Math.max(a, v));
function camAt(t) {
  // t 0 = pohled seshora, t 1 = přímo před X ve výšce středu
  const e = ease(t);
  const pitch = THREE.MathUtils.lerp(THREE.MathUtils.degToRad(86), THREE.MathUtils.degToRad(4), e);
  const yaw = THREE.MathUtils.lerp(THREE.MathUtils.degToRad(-38), 0, ease(clamp(t * 1.15)));
  const dist = THREE.MathUtils.lerp(1150, 960, e);
  const cy = 124;
  cam.position.set(Math.sin(yaw) * Math.cos(pitch) * dist, cy + Math.sin(pitch) * dist, Math.cos(yaw) * Math.cos(pitch) * dist);
  look.set(0, THREE.MathUtils.lerp(60, 30, e), 0);
  cam.lookAt(look);
  cam.rotation.z += THREE.MathUtils.degToRad(THREE.MathUtils.lerp(-6, 0, e));
}

function size() {
  const w = sec.querySelector('.xs__pin').clientWidth, h = sec.querySelector('.xs__pin').clientHeight;
  renderer.setSize(w, h, false); cam.aspect = w / h;
  cam.fov = w / h < 0.8 ? 52 : 32; cam.updateProjectionMatrix();
}
addEventListener('resize', size); size();

let cur = FIXED ?? 0, vis = true;
new IntersectionObserver(es => { vis = es[0].isIntersecting; }, { rootMargin: '300px' }).observe(sec);
function frame() {
  if (!vis) { requestAnimationFrame(frame); return; }
  const r = sec.getBoundingClientRect();
  const p = FIXED ?? clamp(-r.top / (r.height - innerHeight));
  const target = clamp(p / 0.8);               // poslední pětina = kamera stojí a ukáže se titulek
  cur += (target - cur) * (FIXED != null ? 1 : 0.12);
  camAt(cur);
  sec.classList.toggle('is-on', p > 0.78);
  renderer.render(scene, cam);
  requestAnimationFrame(frame);
}
requestAnimationFrame(frame);
