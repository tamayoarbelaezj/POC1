// Pruebas de carga del Asistente de Consulta de Pólizas con k6.
//
// Cada iteración simula una conversación de 4 turnos (promedio observado en el piloto):
// estado de póliza -> coberturas -> estado de siniestro -> cierre.
//
// Uso:
//   export BASE_URL=https://agente-polizas-<hash>-uc.a.run.app
//   export ID_TOKEN=$(gcloud auth print-identity-token)
//   k6 run -e SCENARIO=nominal load-tests/script.js
//   k6 run -e SCENARIO=pico    --summary-export load-tests/resultados/pico.json load-tests/script.js
//
// Escenarios: nominal | pico | estres | soak
//
// Los números de póliza y siniestro corresponden al conjunto sintético cargado en
// Firestore del entorno de pruebas (POL-10000001..POL-10002000, SIN-20000001..SIN-20000800).

import http from 'k6/http';
import { check, sleep, group } from 'k6';
import { Counter, Rate, Trend } from 'k6/metrics';
import { randomIntBetween, uuidv4 } from 'https://jslib.k6.io/k6-utils/1.4.0/index.js';

const BASE_URL = __ENV.BASE_URL || 'http://localhost:8080';
const ID_TOKEN = __ENV.ID_TOKEN || '';
const APP_NAME = 'agente_polizas';
const SCENARIO = __ENV.SCENARIO || 'nominal';

const latenciaTurno = new Trend('latencia_turno', true);
const erroresTurno = new Rate('errores_turno');
const turnos = new Counter('turnos');
const tokensEntrada = new Counter('tokens_entrada');
const tokensSalida = new Counter('tokens_salida');

const ESCENARIOS = {
  // 2x la hora pico real (~0,23 turnos/s): ~0,5 turnos/s
  nominal: {
    executor: 'constant-vus',
    vus: 4,
    duration: '15m',
  },
  // 10x la hora pico real: ~2,3 turnos/s
  pico: {
    executor: 'ramping-vus',
    startVUs: 0,
    stages: [
      { duration: '2m', target: 16 },
      { duration: '16m', target: 16 },
      { duration: '2m', target: 0 },
    ],
  },
  // Rampa hasta saturación para encontrar el punto de quiebre
  estres: {
    executor: 'ramping-vus',
    startVUs: 0,
    stages: [
      { duration: '5m', target: 20 },
      { duration: '5m', target: 40 },
      { duration: '10m', target: 60 },
      { duration: '5m', target: 0 },
    ],
  },
  // Resistencia: carga moderada sostenida durante 2 horas
  soak: {
    executor: 'constant-vus',
    vus: 8,
    duration: '2h',
  },
};

export const options = {
  scenarios: { [SCENARIO]: ESCENARIOS[SCENARIO] },
  thresholds: {
    latencia_turno: ['p(50)<2500', 'p(90)<4000', 'p(99)<8000'],
    errores_turno: ['rate<0.01'],
    http_req_failed: ['rate<0.01'],
  },
  summaryTrendStats: ['avg', 'med', 'p(90)', 'p(95)', 'p(99)', 'max'],
};

function headers() {
  const h = { 'Content-Type': 'application/json' };
  if (ID_TOKEN) {
    h.Authorization = `Bearer ${ID_TOKEN}`;
  }
  return h;
}

function pad8(n) {
  return String(n).padStart(8, '0');
}

function crearSesion(userId, sessionId) {
  const url = `${BASE_URL}/apps/${APP_NAME}/users/${userId}/sessions/${sessionId}`;
  const res = http.post(url, JSON.stringify({}), { headers: headers(), tags: { name: 'crear_sesion' } });
  check(res, { 'sesión creada': (r) => r.status === 200 });
}

function turno(userId, sessionId, texto) {
  const payload = {
    app_name: APP_NAME,
    user_id: userId,
    session_id: sessionId,
    new_message: { role: 'user', parts: [{ text: texto }] },
  };
  const res = http.post(`${BASE_URL}/run`, JSON.stringify(payload), {
    headers: headers(),
    timeout: '60s',
    tags: { name: 'run' },
  });

  turnos.add(1);
  latenciaTurno.add(res.timings.duration);

  const ok = check(res, {
    'status 200': (r) => r.status === 200,
    'respuesta con texto': (r) => {
      try {
        const eventos = r.json();
        return eventos.some((e) => e.content && e.content.parts && e.content.parts.some((p) => p.text));
      } catch (_) {
        return false;
      }
    },
  });
  erroresTurno.add(!ok);

  if (res.status === 200) {
    try {
      for (const e of res.json()) {
        if (e.usage_metadata || e.usageMetadata) {
          const u = e.usage_metadata || e.usageMetadata;
          tokensEntrada.add(u.prompt_token_count || u.promptTokenCount || 0);
          tokensSalida.add(
            (u.candidates_token_count || u.candidatesTokenCount || 0) +
              (u.thoughts_token_count || u.thoughtsTokenCount || 0),
          );
        }
      }
    } catch (_) {
      // El conteo de tokens es informativo; no afecta el resultado del turno.
    }
  }
  return res;
}

export default function () {
  const userId = `carga-${__VU}`;
  const sessionId = uuidv4();
  const poliza = `POL-1${pad8(randomIntBetween(1, 2000)).slice(1)}`;
  const siniestro = `SIN-2${pad8(randomIntBetween(1, 800)).slice(1)}`;

  group('conversacion', () => {
    crearSesion(userId, sessionId);
    turno(userId, sessionId, `Hola, ¿cuál es el estado de mi póliza ${poliza}?`);
    sleep(randomIntBetween(3, 6));
    turno(userId, sessionId, '¿Qué coberturas tiene?');
    sleep(randomIntBetween(3, 6));
    turno(userId, sessionId, `También quiero saber cómo va el siniestro ${siniestro}`);
    sleep(randomIntBetween(3, 6));
    turno(userId, sessionId, 'Gracias, eso es todo');
  });
  sleep(randomIntBetween(2, 4));
}
