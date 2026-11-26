# Sistema de Trámites - Municipalidad Provincial de Yau

Gestión automatizada de trámites con Machine Learning: priorización de casos críticos,
validación de documentos, alertas al ciudadano e indicadores de gestión.

## Estructura
```
sistema-tramites/
├── docker-compose.yml
├── database/init.sql      # tablas y datos base
├── backend/               # API FastAPI, modelos ML y tests
├── frontend/              # React + Vite servido con Nginx
└── docs/                  # propuesta y política de datos
```

## Requisitos
Docker Desktop (con Docker Compose).

## Puesta en marcha
1. Revisar `backend/.env` y cambiar `SECRET_KEY` y las contraseñas.
2. Ejecutar:
```bat
docker compose up -d --build
```

| Servicio | URL |
|---|---|
| Aplicación web | http://localhost:8081 |
| API y documentación | http://localhost:8000/docs |

Detener: `docker compose down`. Detener y borrar la base de datos: `docker compose down -v`.
`init.sql` solo se ejecuta cuando la base se crea desde cero.

## Usuario inicial
Administrador: DNI `00000000`, contraseña `Admin123!`. **Cambiarla antes de cualquier uso real.**
Los ciudadanos se registran desde la web.

## Pruebas
```bat
docker compose exec api python -m pytest -q
```

## Machine Learning
Los modelos se entrenan al primer arranque con datos sintéticos y se reentrenan desde
*Configuración > Reentrenar modelos*. Con datos reales de la municipalidad, reemplazar
`backend/app/ml/datos_sinteticos.py` por la carga del histórico.

## Limitaciones
Notificaciones simuladas (falta conectar WhatsApp, SMS y correo) y modelos entrenados con
datos sintéticos. Ver `docs/propuesta.md`.