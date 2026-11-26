# Política de protección de datos y transparencia

Marco: Ley N.° 29733 (Protección de Datos Personales) y su reglamento vigente, Ley N.° 27806
(Transparencia y Acceso a la Información Pública) y Decreto Legislativo N.° 1412 (Gobierno Digital).
Este documento debe ser revisado por el área legal de la municipalidad antes de su uso real.

## 1. Finalidad y datos tratados
Los datos se usan solo para gestionar trámites y notificar su estado.

| Dato | Para qué se usa |
|---|---|
| DNI y nombres | Identificar al solicitante |
| Teléfono y correo | Enviar notificaciones |
| Documentos adjuntos | Evaluar el trámite |
| Condición de vulnerabilidad | Priorizar la atención |

Principio de minimización: no se piden datos que el trámite no necesite.

## 2. Consentimiento
- El registro exige aceptar el tratamiento de datos; sin esto, el sistema lo rechaza.
- Cada aceptación se guarda con su finalidad, versión del texto y fecha (tabla `consentimientos`).
- El texto completo se muestra en el registro antes de aceptar.

## 3. Derechos ARCO
El ciudadano puede solicitar acceso, rectificación, cancelación y oposición a la municipalidad.
Estado actual: se atienden por solicitud al administrador. Queda pendiente automatizarlos.

## 4. Medidas de seguridad
- Contraseñas cifradas con bcrypt; nunca se guardan en texto plano.
- Sesiones con token JWT de duración limitada (8 horas).
- Permisos por rol: el ciudadano solo ve sus trámites; la administración requiere rol ADMIN.
- DNI enmascarado en listados administrativos y en la bitácora (ej. `12****78`).
- Archivos adjuntos limitados a PDF, JPG y PNG de hasta 5 MB.
- Configuración sensible fuera del código (`.env`, excluido del repositorio).

## 5. Auditoría
Se registran inicios de sesión (incluidos los fallidos), registros, cambios de estado, altas
y bajas de usuarios y cambios de configuración, con fecha, usuario e IP. Es consultable por el
administrador en *Auditoría*.

## 6. Transparencia
- Indicadores públicos (trámites, tiempos de atención, observaciones, satisfacción).
- Consulta pública por código: muestra estado e historial, nunca datos personales.
- Historial completo de cada trámite visible para su titular.

## 7. Uso responsable del machine learning
- El modelo apoya la decisión; no reemplaza al funcionario.
- Los criterios de prioridad son explicables y cada trámite guarda su motivo.
- Las reglas legales fijan la prioridad máxima sin depender del modelo.
- No se usan variables discriminatorias (sexo, origen, ingresos, etc.).
- Cada reentrenamiento queda registrado con versión y métricas (`modelos_ml`).

## 8. Pendiente de definir por la municipalidad
Plazo de conservación de datos, responsable del banco de datos y su inscripción ante la
Autoridad Nacional de Protección de Datos Personales.