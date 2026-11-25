CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE areas (
  id SERIAL PRIMARY KEY,
  nombre VARCHAR(80) UNIQUE NOT NULL
);

CREATE TABLE usuarios (
  id SERIAL PRIMARY KEY,
  dni VARCHAR(12) UNIQUE NOT NULL,
  nombres VARCHAR(120) NOT NULL,
  email VARCHAR(120),
  telefono VARCHAR(20),
  password_hash VARCHAR(100) NOT NULL,
  rol VARCHAR(12) NOT NULL CHECK (rol IN ('ADMIN','CIUDADANO')),
  area_id INT REFERENCES areas(id),
  activo BOOLEAN NOT NULL DEFAULT TRUE,
  creado TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE consentimientos (            -- Ley 29733
  id SERIAL PRIMARY KEY,
  usuario_id INT NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
  finalidad VARCHAR(200) NOT NULL,
  version VARCHAR(10) NOT NULL DEFAULT '1.0',
  aceptado BOOLEAN NOT NULL,
  fecha TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE tipos_tramite (
  id SERIAL PRIMARY KEY,
  nombre VARCHAR(80) UNIQUE NOT NULL,
  area_id INT NOT NULL REFERENCES areas(id),
  plazo_dias INT NOT NULL,                -- plazo legal (TUPA)
  documentos_requeridos TEXT NOT NULL DEFAULT ''   -- separados por coma
);

CREATE TABLE tramites (
  id SERIAL PRIMARY KEY,
  codigo VARCHAR(12) UNIQUE NOT NULL,
  tipo_id INT NOT NULL REFERENCES tipos_tramite(id),
  ciudadano_id INT NOT NULL REFERENCES usuarios(id),
  responsable_id INT REFERENCES usuarios(id),
  asunto VARCHAR(200),
  estado VARCHAR(12) NOT NULL DEFAULT 'REGISTRADO'
    CHECK (estado IN ('REGISTRADO','EN_REVISION','OBSERVADO','FINALIZADO','RECHAZADO')),
  prioridad VARCHAR(5) NOT NULL DEFAULT 'MEDIA' CHECK (prioridad IN ('ALTA','MEDIA','BAJA')),
  puntaje REAL,
  motivo_prioridad VARCHAR(200),
  prob_error REAL,
  dias_estimados REAL,
  vulnerable BOOLEAN NOT NULL DEFAULT FALSE,
  anomalia BOOLEAN NOT NULL DEFAULT FALSE,
  creado TIMESTAMP NOT NULL DEFAULT NOW(),
  actualizado TIMESTAMP NOT NULL DEFAULT NOW(),
  finalizado TIMESTAMP
);
CREATE INDEX idx_tramites_cola ON tramites (estado, prioridad);

CREATE TABLE historial (
  id SERIAL PRIMARY KEY,
  tramite_id INT NOT NULL REFERENCES tramites(id) ON DELETE CASCADE,
  estado VARCHAR(12) NOT NULL,
  comentario VARCHAR(300) DEFAULT '',
  usuario_id INT REFERENCES usuarios(id),
  fecha TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE documentos (
  id SERIAL PRIMARY KEY,
  tramite_id INT NOT NULL REFERENCES tramites(id) ON DELETE CASCADE,
  tipo_documento VARCHAR(60) NOT NULL,
  nombre_original VARCHAR(200) NOT NULL,
  ruta VARCHAR(300) NOT NULL,
  fecha TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE encuestas (
  id SERIAL PRIMARY KEY,
  tramite_id INT UNIQUE NOT NULL REFERENCES tramites(id) ON DELETE CASCADE,
  calificacion INT NOT NULL CHECK (calificacion BETWEEN 1 AND 5),
  comentario VARCHAR(300) DEFAULT '',
  fecha TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE notificaciones (
  id SERIAL PRIMARY KEY,
  tramite_id INT REFERENCES tramites(id) ON DELETE CASCADE,
  usuario_id INT NOT NULL REFERENCES usuarios(id),
  canal VARCHAR(10) NOT NULL CHECK (canal IN ('EMAIL','SMS','WHATSAPP')),
  mensaje VARCHAR(300) NOT NULL,
  estado_envio VARCHAR(10) NOT NULL DEFAULT 'PENDIENTE'
    CHECK (estado_envio IN ('PENDIENTE','ENVIADO','FALLIDO')),
  intentos INT NOT NULL DEFAULT 0,
  fecha TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE auditoria (
  id SERIAL PRIMARY KEY,
  usuario_id INT,
  accion VARCHAR(60) NOT NULL,
  entidad VARCHAR(60),
  detalle VARCHAR(300) DEFAULT '',
  ip VARCHAR(45),
  fecha TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE modelos_ml (
  id SERIAL PRIMARY KEY,
  nombre VARCHAR(60) NOT NULL,            -- prioridad, tiempo, clasificador, anomalias
  version VARCHAR(20) NOT NULL,
  metricas JSONB,
  ruta VARCHAR(300),
  activo BOOLEAN NOT NULL DEFAULT TRUE,
  entrenado TIMESTAMP NOT NULL DEFAULT NOW()
);

-- ===== DATOS BASE =====
INSERT INTO areas (nombre) VALUES
  ('Mesa de Partes'), ('Licencias'), ('Registro Civil'), ('Desarrollo Urbano'), ('Salud');

INSERT INTO tipos_tramite (nombre, area_id, plazo_dias, documentos_requeridos) VALUES
  ('licencia_funcionamiento', (SELECT id FROM areas WHERE nombre='Licencias'), 15, 'dni,declaracion_jurada,titulo_propiedad'),
  ('certificado_posesion', (SELECT id FROM areas WHERE nombre='Desarrollo Urbano'), 10, 'dni,plano_ubicacion,recibo_servicios'),
  ('partida_nacimiento', (SELECT id FROM areas WHERE nombre='Registro Civil'), 5, 'dni,constancia_nacimiento'),
  ('licencia_construccion', (SELECT id FROM areas WHERE nombre='Desarrollo Urbano'), 30, 'dni,plano_arquitectura,titulo_propiedad'),
  ('salud_emergencia', (SELECT id FROM areas WHERE nombre='Salud'), 2, 'dni');

-- Administrador inicial (DNI 00000000 / Admin123!) -> cambiar la clave después
INSERT INTO usuarios (dni, nombres, email, telefono, password_hash, rol) VALUES
  ('00000000', 'Administrador Municipal', 'admin@muniyau.gob.pe', '999000000',
   crypt('Admin123!', gen_salt('bf')), 'ADMIN');

INSERT INTO consentimientos (usuario_id, finalidad, aceptado) VALUES
  ((SELECT id FROM usuarios WHERE dni='00000000'), 'Gestión de trámites municipales', TRUE);