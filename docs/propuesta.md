# Propuesta: Sistema automatizado de gestión de trámites con Machine Learning
**Municipalidad Provincial de Yau**

## 1. Problema
La gestión manual de trámites produce largas colas, errores frecuentes y falta de transparencia.
Al no existir registros digitales, no se pueden identificar cuellos de botella ni priorizar
los casos críticos. Esto deteriora la calidad del servicio y la imagen institucional.

## 2. Objetivos
- Automatizar el registro, seguimiento y atención de trámites.
- Priorizar los trámites críticos y reducir los errores de procesamiento con ML.
- Notificar al ciudadano cada cambio de estado de su solicitud.
- Medir el servicio con indicadores y detectar cuellos de botella.

## 3. Solución
Aplicación web con tres capas, desplegada con Docker:

| Capa | Tecnología | Función |
|---|---|---|
| Frontend | React + Vite + Nginx | Portal del ciudadano, panel administrativo y consulta pública |
| Backend | FastAPI (Python) | API REST, reglas del flujo, seguridad y notificaciones |
| Datos | PostgreSQL | Trámites, historial, usuarios, consentimientos y auditoría |

Los modelos de ML se entrenan con scikit-learn y se cargan en el backend.

## 4. Machine Learning
| Modelo | Algoritmo | Uso | Métrica (datos sintéticos) |
|---|---|---|---|
| Prioridad | Gradient Boosting | Probabilidad de que un trámite sea crítico | F1 macro 0.871 |
| Tiempo de atención | Gradient Boosting (regresión) | Días estimados | Error medio 0.649 días |
| Clasificador de tipo | TF-IDF + Regresión Logística | Sugiere el tipo de trámite según el asunto | Exactitud 1.0 |
| Anomalías | Isolation Forest | Marca expedientes atípicos | Contaminación 3 % |

**Priorización híbrida:** puntaje = 60 % reglas explicables + 40 % modelo. Las reglas legales
(trámite de salud o solicitante vulnerable) fijan siempre prioridad ALTA, sin depender del modelo.
Cada trámite guarda el motivo de su prioridad para que sea auditable. Si el modelo falla, el
sistema sigue operando solo con reglas.

**Reducción de errores:** el sistema compara los documentos requeridos del TUPA con los adjuntos,
calcula el riesgo de observación, impide finalizar trámites incompletos y exige el motivo al
observar o rechazar.

## 5. Alertas y notificaciones
- Eventos: registro, revisión, observación (con motivo), finalización, rechazo y plazo por vencer.
- Canales: WhatsApp, con respaldo por SMS, y correo electrónico, con 3 reintentos.
- Alertas programadas cada hora para trámites cercanos al vencimiento.
- Línea de tiempo visible para el ciudadano y consulta pública por código.

## 6. Cumplimiento de las condiciones del caso
| Condición | Cómo se cumple |
|---|---|
| Escalable con infraestructura existente | Contenedores Docker, servicios independientes, PostgreSQL y herramientas de código abierto |
| Adaptada a los flujos existentes | Áreas, plazos y documentos del TUPA configurables desde el panel, sin cambiar código |
| Protección de datos y transparencia | Consentimiento registrado, datos mínimos, DNI enmascarado, auditoría, indicadores públicos (ver `politica_datos.md`) |

## 7. Resultados de las pruebas
Pruebas automáticas (`pytest`) sobre seguridad, priorización, reglas del flujo, protección de
datos y modelos de ML. Se prueban además el flujo completo desde la interfaz web y las alertas.

## 8. Limitaciones y trabajo futuro
- Los modelos se entrenaron con datos **sintéticos**. Deben reentrenarse con el histórico real
  (opción *Reentrenar modelos* del panel). Las métricas actuales no representan el desempeño real.
- Los envíos de WhatsApp, SMS y correo están **simulados**; falta conectar proveedores reales.
- La condición de vulnerabilidad es declarada por el ciudadano y la verifica el personal.
- Pendientes: derechos ARCO automatizados, integración con RENIEC, firma digital y roles por área.