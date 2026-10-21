/* Roxfilm – 3D X z loga před sekcí reels (three.js, scroll řídí kameru)
   Kamera začíná těsně u hrany černého X, přetočí se, oddálí a zastaví přímo před ním. */
import * as THREE from 'three';
import { Reflector } from './three/Reflector.js';

const q = new URLSearchParams(location.search);
const FIXED = q.has('p') ? parseFloat(q.get('p')) : null;

const sec = document.getElementById('reels-x');
if (!sec) throw 0;
const pin = sec.querySelector('.xs__pin');
const canvas = sec.querySelector('canvas');
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, powerPreference: 'high-performance' });
const DPR = Math.min(devicePixelRatio || 1, 2);
renderer.setPixelRatio(DPR);
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.05;
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;

const scene = new THREE.Scene();
const INK = new THREE.Color('#0F0F0E');
scene.background = INK;
scene.fog = new THREE.Fog(INK, 1400, 3000);

// --- studiové prostředí: tmavý ateliér s dlouhými softboxy, které se odráží v lesklé černé ---
function studio() {
  const env = new THREE.Scene();
  env.add(new THREE.Mesh(new THREE.BoxGeometry(100, 100, 100), new THREE.MeshBasicMaterial({ color: '#050505', side: THREE.BackSide })));
  const box = (w, h, x, y, z, ry, rx, k) => {
    const m = new THREE.Mesh(new THREE.PlaneGeometry(w, h), new THREE.MeshBasicMaterial({ color: new THREE.Color(k, k, k), side: THREE.DoubleSide }));
    m.position.set(x, y, z); m.rotation.set(rx, ry, 0); env.add(m);
  };
  box(36, 3.2, 0, 30, 6, 0, Math.PI / 2, 6);        // dlouhý softbox nad hlavou
  box(3, 30, -40, 6, 14, Math.PI / 2, 0, 3.2);      // úzký pruh vlevo
  box(3, 30, 40, 6, 10, -Math.PI / 2, 0, 2.2);      // úzký pruh vpravo
  box(26, 8, 0, 8, -46, 0, 0, 1.6);                 // kontra zezadu
  box(18, 2, 0, -8, 40, Math.PI, 0, 0.6);           // slabý odraz zespodu
  box(44, 14, 0, 26, 44, Math.PI, -0.5, 0.55);      // velká měkká plocha před X: jemný přechod na čelní stěně
  const pm = new THREE.PMREMGenerator(renderer);
  const t = pm.fromScene(env, 0.02).texture; pm.dispose(); return t;
}
scene.environment = studio();

// --- X z loga: dvě poloviny přesně podle polygonů z brand manuálu ---
const L = [[0,0],[123,0],[144,124],[123,248],[0,248],[100,124]];
const R = [[22,0],[139,0],[42,124],[139,248],[22,248],[0,124]];
const OX = 158;                       // mezera mezi polovinami jako v logu
const shape = (pts, ox) => { const s = new THREE.Shape(); pts.forEach(([x, y], i) => { const X = x + ox, Y = 248 - y; i ? s.lineTo(X, Y) : s.moveTo(X, Y); }); s.closePath(); return s; };
const extr = { depth: 52, bevelEnabled: true, bevelThickness: 3.2, bevelSize: 2.6, bevelSegments: 8, curveSegments: 1 };
// černá s jemným leskem: matnější základ + čistý lak, ve kterém se odráží softboxy
const mat = new THREE.MeshPhysicalMaterial({ color: '#0b0b0b', roughness: 0.34, metalness: 0.05, clearcoat: 1, clearcoatRoughness: 0.07, envMapIntensity: 1.25 });
const xg = new THREE.Group();
[[L, 0], [R, OX]].forEach(([pts, ox]) => {
  const g = new THREE.ExtrudeGeometry(shape(pts, ox), extr);
  const m = new THREE.Mesh(g, mat); m.castShadow = true; m.receiveShadow = true; xg.add(m);
});
const W = OX + 139;
xg.position.set(-W / 2, 3.2, -26);    // střed X v počátku, stojí na podlaze
scene.add(xg);

// tmavá podlaha s jemným odrazem
const RT = 1024 * DPR;
const mirror = new Reflector(new THREE.PlaneGeometry(9000, 9000), { textureWidth: RT, textureHeight: RT, color: 0x2a2a28 });
mirror.rotation.x = -Math.PI / 2; mirror.position.y = -0.5; scene.add(mirror);
const floor = new THREE.Mesh(new THREE.PlaneGeometry(9000, 9000), new THREE.MeshStandardMaterial({ color: '#0F0F0E', roughness: 0.7, metalness: 0, transparent: true, opacity: 0.86 }));
floor.rotation.x = -Math.PI / 2; floor.receiveShadow = true; scene.add(floor);

// světla: kužel shora, dvě kontry zezadu kreslí obrys černého X
const key = new THREE.SpotLight('#ffffff', 2.6e6, 0, Math.PI / 12, 0.6, 2);
key.position.set(-160, 1600, 300); key.target.position.set(0, 0, 0);
key.castShadow = true; key.shadow.mapSize.set(2048, 2048); key.shadow.bias = -0.0004; key.shadow.radius = 5;
scene.add(key, key.target);
const rimL = new THREE.SpotLight('#ffffff', 3.4e6, 0, Math.PI / 10, 0.5, 2);
rimL.position.set(-760, 360, -820); rimL.target.position.set(0, 124, 0); scene.add(rimL, rimL.target);
const rimR = new THREE.SpotLight('#eef2ff', 3.0e6, 0, Math.PI / 10, 0.5, 2);
rimR.position.set(760, 420, -760); rimR.target.position.set(0, 124, 0); scene.add(rimR, rimR.target);

// kamera: těsně u hrany → přetočení → oddálení → zastaví přímo před X
const cam = new THREE.PerspectiveCamera(32, 1, 0.5, 10000);
const look = new THREE.Vector3(), T0 = new THREE.Vector3(-26, 150, 26), T1 = new THREE.Vector3(0, 100, 0);
const smooth = t => t * t * (3 - 2 * t);
const ease = t => t < .5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;
const clamp = (v, a = 0, b = 1) => Math.min(b, Math.max(a, v));
const D = THREE.MathUtils.degToRad;
let D1 = 840;
function camAt(t) {
  const e = ease(t);
  const yaw = THREE.MathUtils.lerp(D(68), 0, smooth(clamp(t * 1.12)));
  const pitch = THREE.MathUtils.lerp(D(16), D(4), e);
  const dist = 120 * Math.pow(D1 / 120, ease(clamp(t * 1.04)));   // oddálení jako jízda jeřábem
  look.lerpVectors(T0, T1, e);
  cam.position.set(look.x + Math.sin(yaw) * Math.cos(pitch) * dist, look.y + Math.sin(pitch) * dist, look.z + Math.cos(yaw) * Math.cos(pitch) * dist);
  cam.lookAt(look);
  cam.rotation.z += D(THREE.MathUtils.lerp(-9, 0, e));
}

function size() {
  const w = pin.clientWidth, h = pin.clientHeight;
  renderer.setSize(w, h, false); cam.aspect = w / h;
  const portrait = w / h < 0.8;
  cam.fov = portrait ? 52 : 32; D1 = portrait ? 1000 : 840;
  cam.updateProjectionMatrix();
}
addEventListener('resize', size); size();

let cur = FIXED ?? 0, vis = true, lastT = 0;
new IntersectionObserver(es => { vis = es[0].isIntersecting; }, { rootMargin: '400px' }).observe(sec);
function frame(now) {
  requestAnimationFrame(frame);
  const dt = Math.min(100, lastT ? now - lastT : 16); lastT = now;
  if (!vis) return;
  const r = sec.getBoundingClientRect(), vh = innerHeight;
  // sekce je podsunutá pod předchozí (o 100vh); pohyb začíná, jakmile spodek světlé sekce
  // začne mizet, tedy ještě nad karty Osobní značky / Firmy / Instituce
  const p = FIXED ?? clamp((vh * 0.75 - r.top) / (r.height - vh * 0.25));
  const target = clamp(p / 0.84);
  cur += (target - cur) * (FIXED != null ? 1 : 1 - Math.pow(0.0015, dt / 1000));
  camAt(cur);
  sec.classList.toggle('is-on', p > 0.87);
  renderer.render(scene, cam);
}
requestAnimationFrame(frame);
