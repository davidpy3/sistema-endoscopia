# Requerimientos de Negocio — Sistema de Endoscopia
### Hospital Regional de Tumbes — JAMO II-2 · Servicio de Gastroenterología

> Documento generado a partir del análisis de los prototipos funcionales:
> - `prototipo_informe_colonoscopia.html`
> - `prototipo_informe_eda.html`

---

## 1. Contexto y objetivo

El servicio de Gastroenterología del Hospital Regional de Tumbes (JAMO II-2) requiere
digitalizar la generación de informes de **Colonoscopía** y **Endoscopía Digestiva Alta (EDA)**,
reemplazando el llenado manual/texto libre por un modelo de **captura híbrida**:

> *"Cada segmento tiene un selector Normal/Alterado con frase estándar autocompletada.
> Los indicadores de calidad se capturan como campos discretos —no como texto— para que
> la Fase 2 los explote sin re-parsear."* — nota de ambos prototipos.

Esto implica dos objetivos de negocio simultáneos:

1. **Fase 1 (alcance de este proyecto):** capturar el informe endoscópico completo y generar
   el documento imprimible con el membrete y formato oficial del hospital.
2. **Fase 2 (fuera de alcance inmediato, pero condiciona el diseño de datos):** explotar los
   indicadores de calidad de forma agregada (ej. ADR/PDR — Adenoma/Polyp Detection Rate,
   tasa de intubación cecal, tiempos de retiro/examinación) para un dashboard de calidad del
   servicio. Por eso ningún indicador puede quedar como texto libre.

Ambos prototipos comparten la misma identidad visual, estructura de secciones y lógica de
interacción; solo difieren en los segmentos anatómicos explorados y los scores de calidad
propios de cada procedimiento.

---

## 2. Actores

| Actor | Rol en el sistema |
|---|---|
| Médico endoscopista | Registra los hallazgos, genera y firma el informe |
| Enfermera asistente | Registrada como personal de apoyo del procedimiento |
| Paciente | Sujeto del procedimiento; identificado por DNI |
| (Fase 2) Jefatura de servicio | Consumidor de indicadores agregados de calidad |

---

## 3. Requerimientos funcionales comunes (EDA y Colonoscopía)

### RF-01 · Datos del paciente y del procedimiento
Ambos formularios capturan como sección 1:

- Paciente (nombre), DNI, edad, fecha del procedimiento
- Médico endoscopista, enfermera asistente
- Motivo del procedimiento (texto libre)
- Antecedentes (texto libre)
- Tipo de sedación: `Ninguna | Consciente | Profunda | NAAP / propofol`
- Fármacos utilizados (texto libre, ej. "Midazolam 5mg EV")

### RF-02 · Captura híbrida por segmento anatómico
Cada procedimiento define una lista fija de segmentos (colon o tramo alto digestivo). Por cada
segmento:

- Selector de estado: **Normal** / **Alterado**
- Si es **Normal** → autocompleta una frase estándar predefinida (no editable por defecto,
  pero el texto sigue siendo un campo editable)
- Si es **Alterado** → limpia el campo, lo marca visualmente ("● hallazgo registrado") y exige
  redacción del hallazgo
- El texto final por segmento siempre queda como campo estructurado (`segmento`, `estado`, `texto`),
  nunca como bloque de texto libre indiferenciado

### RF-03 · Biopsias / muestras (repetidor)
Lista dinámica de biopsias, cada una con:

- N.º de frasco (ej. "A")
- Descripción / sitio / técnica (ej. "Pólipos en sigmoides, asa fría")
- N.º de lesiones

El conteo de lesiones queda como dato estructurado — insumo directo para métricas de Fase 2
(ADR/PDR mencionado explícitamente en el prototipo de colonoscopía).

### RF-04 · Diagnósticos endoscópicos (repetidor)
Lista dinámica de líneas de diagnóstico en texto libre, agregables/eliminables individualmente.

### RF-05 · Sugerencias / plan (repetidor)
Lista dinámica de sugerencias/plan de manejo, misma mecánica que diagnósticos.

### RF-06 · Imágenes endoscópicas
- Carga por drag&drop o selección de archivo (JPG/PNG)
- Cada imagen admite un epígrafe editable (ej. "Pólipo sigmoides NBI")
- Deben poder eliminarse individualmente antes de generar el informe

### RF-07 · Persistencia del caso en progreso
El prototipo permite **guardar** el estado del formulario como archivo `.json` descargable y
**volver a abrirlo** para continuar editando — funcionalidad de borrador que el backend debe
poder reproducir (guardar caso incompleto y reanudar).

### RF-08 · Generación del informe imprimible
Un botón "Generar informe" arma un documento con:

- Membrete: **HOSPITAL REGIONAL DE TUMBES — JAMO II-2 / SERVICIO DE GASTROENTEROLOGÍA**
- Título del procedimiento (COLONOSCOPÍA / ENDOSCOPÍA DIGESTIVA ALTA)
- Tabla de datos paciente/procedimiento a 2 columnas
- Bloque de hallazgos endoscópicos por segmento, en orden anatómico fijo
- Bloques de biopsias, diagnósticos y sugerencias (con viñetas, o "—"/"Sin biopsias" si están vacíos)
- Grilla de imágenes con epígrafe
- Pie de firma: nombre del médico + "Médico Endoscopista"

El documento debe ser **imprimible/exportable** (el prototipo usa `window.print()` con CSS de
media `print`; en el backend esto se traduce a generación de PDF sin depender del navegador
del usuario).

### RF-09 · Valores por defecto en campos vacíos
Todo campo vacío en el informe final se muestra como **"—"** (no como celda en blanco ni `null`
crudo) — patrón repetido en todo el prototipo (`${x || '—'}`).

---

## 4. Requerimientos específicos — Colonoscopía

### RF-C01 · Segmentos explorados (orden fijo, sentido de retiro)
1. Ciego
2. Colon ascendente
3. Colon transverso
4. Colon descendente
5. Colon sigmoides
6. Recto

### RF-C02 · Indicadores de calidad de colonoscopía
- **Intubación cecal**: Sí/No
- **Foto-documentación de ciego**: Sí/No
- **Ileoscopía distal**: Sí/No
- **Escala de Boston** por segmento: Colon derecho (CD), Colon transverso (CT), Colon
  izquierdo (CI) — cada uno de 0 a 3 puntos
- **Preparación adecuada** (calculado, no capturado): `Boston total ≥ 6 Y cada segmento ≥ 2`
- **Tiempo de retiro** en minutos (decimal, incrementos de 0.5)

### RF-C03 · Inspección anal y tacto rectal (sección exclusiva de colonoscopía)
- Inspección pasiva (texto)
- Inspección activa (texto)
- Tacto rectal (texto)
- Canal anal (texto)

---

## 5. Requerimientos específicos — EDA

### RF-E01 · Segmentos explorados (orden fijo)
1. Esófago
2. Estómago — Fondo *(con sub-campo: Cardias, escala de Hill I–IV)*
3. Estómago — Cuerpo
4. Estómago — Ángulo
5. Estómago — Antro *(con sub-campo: Píloro — Céntrico y permeable / Deformado / Estenótico)*
6. Duodeno — Bulbo
7. Duodeno — 2.ª porción

### RF-E02 · Indicadores de calidad de EDA
- **Score PEACE** por tramo: Esófago, Estómago, Duodeno (cada uno de 1 a 3)
- **Score PEACE total** (calculado = suma de los 3)
- **Tiempo de examinación** en minutos (entero)

> A diferencia de colonoscopía, EDA no tiene "preparación adecuada" calculada ni sección de
> inspección anal/tacto rectal.

---

## 6. Reglas de negocio transversales

| Regla | Detalle |
|---|---|
| RN-01 | El estado de un segmento (`normal`/`alterado`) determina el texto sugerido, pero el texto siempre queda editable manualmente |
| RN-02 | Cambiar un segmento de "Alterado" a "Normal" restaura la frase estándar; el texto libre escrito se pierde (comportamiento del prototipo, a confirmar si se desea advertencia antes de sobrescribir) |
| RN-03 | El total y la evaluación de Boston/PEACE **nunca se guardan como texto**, se derivan siempre de los campos numéricos discretos |
| RN-04 | Los repetidores (biopsias, diagnósticos, sugerencias) no tienen límite máximo de filas en el prototipo |
| RN-05 | Un informe sin biopsias muestra explícitamente "Sin biopsias." (no una sección vacía) |

---

## 7. Fuera de alcance de los prototipos (pendiente de definir con el cliente)

- Autenticación/roles de usuario (los prototipos no contemplan login)
- Validaciones de negocio sobre campos obligatorios antes de generar el informe
- Historial de versiones de un mismo informe (edición posterior a firma)
- Métricas y dashboard de Fase 2 (ADR/PDR, indicadores agregados por médico/período)
- Firma digital/electrónica del informe
- Envío del informe (email, portal del paciente, HL7/FHIR con otros sistemas del hospital)
- Compresión/almacenamiento óptimo de imágenes (el prototipo las maneja en base64 en memoria)

---

## 8. Trazabilidad hacia el modelo de datos implementado

| Requerimiento | Modelo Django |
|---|---|
| RF-01 | `procedimientos.ProcedimientoBase` (abstracto), `pacientes.Paciente`, `personal.Personal` |
| RF-02, RF-C01, RF-C03 | `colonoscopia.Colonoscopia`, `colonoscopia.SegmentoColon` |
| RF-02, RF-E01 | `eda.EDA`, `eda.SegmentoEDA` |
| RF-C02 | Campos `boston_cd/ct/ci`, `intubacion_cecal`, `foto_doc_ciego`, `ileoscopia_distal` en `Colonoscopia` + propiedades `boston_total`, `preparacion_adecuada` |
| RF-E02 | Campos `peace_esofago/estomago/duodeno` en `EDA` + propiedad `peace_total` |
| RF-03 | `colonoscopia.BiopsiaColonoscopia`, `eda.BiopsiaEDA` |
| RF-04 | `colonoscopia.DiagnosticoColonoscopia`, `eda.DiagnosticoEDA` |
| RF-05 | `colonoscopia.SugerenciaColonoscopia`, `eda.SugerenciaEDA` |
| RF-06 | `imagenes.ImagenEndoscopica` (genérica vía `ContentType`) |
| RF-08 | App `reportes` (WeasyPrint + templates `colonoscopia_pdf.html` / `eda_pdf.html`) |
| RF-09 | Filtro de template `dash` en `reportes/templatetags/reportes_extras.py` |
| RF-07 | Pendiente — cubierto parcialmente por los endpoints DRF (`PATCH` permite guardar un caso incompleto); falta UI de "borrador" |