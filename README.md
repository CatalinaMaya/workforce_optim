<img src="Holafly-logo.svg.webp" alt="Logo" width="200">

# **Optimización de asignación de turnos de operación**

## <font color='#E7485C'> **1. Descripción del problema** </font>
El departamento de ventas de la empresa Holafly, cuenta con 60 colaboradores distribuidos entre tres mercados (América, Europa y Asia). Cada día de una semana de planificación, los colaboradores pueden ser asignados a uno de tres turnos de trabajo (mañana, tarde o noche), cada uno con una duración de ocho horas. El objetivo es diseñar un modelo de optimización que determine la asignación diaria de turnos para cada colaborador, de manera que la disponibilidad de personal se ajuste lo mejor posible al personal requerido en cada mercado y turno, respetando las restricciones laborales y de disponibilidad de los colaboradores.

A continuación, se definen explícitamente los elementos que deben considerarse en la modelación:

### Conjuntos
- Colaboradores: conjunto de empleados que deben asignarse
- Mercados: América, Europa, Asia
- Turnos de trabajo: Mañana (6:00-14:00), tarde (14:00-22:00), noche (22:00-6:00)
- Días de la semana de planificación (lunes, martes, miércoles, jueves, viernes, sábado, domingo)

### Parámetros
- Personal requerido por día, turno y mercado.
- Disponibilidad de cada colaborador para trabajar en un día y turno determinados.

### Decisiones
- Turno y mercado asignado a cada colaborador cada día

### Objetivo
- Minimizar la desviación absoluta entre el personal asignado y el personal requerido.

### Restricciones
- Cada colaborador puede ser asignado, como máximo, a un turno por día.
- Las asignaciones deben respetar la disponibilidad de cada colaborador.
- Un colaborador que trabaje en el turno de noche no puede ser asignado al turno de mañana del día siguiente.
- Cada colaborador debe tener al menos un día completo de descanso durante la semana.

### **Supuestos**
- Cada colaborador puede atender cualquiera de los tres mercados

---

## **2. Modelación**
### Conjuntos
- $C:$ Colaboradores ($i$)
- $M:$ Mercados ($m$)
- $T:$ Turnos ($t$)
- $D:$ Días de la semana ($d$)

### Parámetros
- $R_{dtm}:$ Personal requerido el día $d$, turno $t$, mercado $m$
- $A_{idt}:$ 1 si el colaborador $i$ está disponible el día $i$ en el turno $t$


### Decisiones
- $x_{idtm}:$ 1 si el colaborador $i$ trabaja el día $d$, turno $t$, mercado $m$, 0 en otro caso

Variables auxiliares:
- $e_{dtm} \geq 0$: exceso de personal
- $f_{dtm} \geq 0$: déficit de personal

### Función objetivo
Minimizar la desviación absoluta entre el personal asignado y el requerido.

min $\sum_{d \in D}\sum_{t \in T}\sum_{m \in M} (e_{dtm} + f_{dtm})$


### Restricciones
1. Un turno por colaborador al día: Cada colaborador puede trabajar como máximo un turno diario.

$$\sum_{t \in T}\sum_{m \in M} x_{idtm}\leq 1 \forall i \in C, d \in D$$

2. Respetar disponibilidad: Un colaborador solo puede ser asignado si está disponible.

$$\sum_{m \in M} x_{idtm}\leq A_{ids} \forall i \in C, d \in D, t\in T$$

3. Balance entre asignación y requerimiento: La diferencia entre personal asignado y requerido se representa mediante exceso y déficit.

$$\sum_{i \in C} x_{idtm} - R_{dtm} = e_{dtm} - f_{dtm} \forall d \in D, t \in T, m\in M$$

4. Descanso después de turno de noche

$$\sum_{m \in M} x_{id,t_N,m} + \sum_{m \in M} x_{i,d+1,t_M,m} \leq 1 \forall i, d = 1, ..., 7$$

5. Mínimo de descanso semanal: Cada colaborador debe tener al menos un día sin asignación.

$$\sum_{d \in D}\sum_{t \in T}\sum_{m \in M} x_{idtm}\leq 6 \forall i \in C$$

6. Tipo de variables

$$x_{idtm} \in {0,1}$$
$$e_{dtm} \geq 0$$
$$f_{dtm} \geq 0$$

---
## **3. Implementación**

[Visitar interfaz interactiva 🚀](https://workforceholafly.streamlit.app/)

### Guía de la interfaz

- _Barra lateral - Parámetros_

| Parámetro | Qué hace |
|---|---|
| **Origen de los datos** | `Generar aleatoriamente`: crea A y R con los parámetros habilitados en la barra lateral `Cargar desde data/*.xlsx`: usa los archivos existentes en `data/`|
| **Total de colaboradores** | Tamaño del equipo a asignar (por defecto 60). |
| **Mercados** | Lista separada por comas (por defecto `America, Europa, Asia`). |
| **Días** | Fijo: Lunes a Domingo. No editable, porque la restricción de descanso post-turno-noche depende del orden de los días. |
| **Turnos** | Fijo: Mañana, Tarde, Noche. No editable — el modelo referencia estas etiquetas exactas internamente. |
| **Probabilidad de disponibilidad (%)** | Probabilidad de que un colaborador esté disponible en un turno/día dado (por defecto 90%). Solo aplica si el origen es "Generar aleatoriamente". |
| **Rango de personal requerido** | Rango (mínimo, máximo) del que se sortea el requerido por turno/mercado/día (por defecto 4–10). |
| **Guardar esta instancia en data/*.xlsx** | Checkbox que, al generar, sobreescribe los archivos en `data/` con la instancia actual — útil para dejar fija la versión que usarás en una demo. |
| **🚀 Ejecutar Optimización** | Construye el modelo con los datos actuales y lo resuelve. |
  
- _Pestaña "Instancia_
  
  Muestra, antes de optimizar, cómo quedaron los datos de entrada:
  - Gráfico de barras de disponibilidad total por día y turno.
  - Gráfico de barras de personal requerido por día y turno.
  - Tabla completa de personal requerido desplegable.

  Sirve para verificar visualmente los insumos del modelo antes de correrlo, para explicar qué está entrando al optimizador.

- _Pestaña "Resultados_
  
  **Métricas:**
  - Total asignaciones: número de turnos efectivamente cubiertos.
  - Utilización de headcount: % del total colaborador-días disponibles que se usó.
  - Desviación total (obj.): valor de la función objetivo — suma de exceso + déficit en todo el periodo. Cuanto más bajo, mejor ajustada quedó la asignación a la demanda.
  - Turnos con déficit: cuántas combinaciones día-turno-mercado quedaron por debajo de lo requerido.
  - Tiempo del solver: cuánto tardó en resolver el modelo de optimización.

  **Gráficos:**
  - Requerido vs. asignado, agregado por turno y por mercado.
  - Evolución diaria de requerido vs. asignado.
  - Mapa de calor de déficit/exceso neto por turno-mercado.
  - Distribución de turnos asignados por colaborador (para verificar balance de carga).

  **Tablas y exportación:**
  - Tabla de resumen (cobertura por día/turno/mercado) y tabla de asignación detallada (colaborador → día, turno, mercado).
  - Los resultados quedan guardados automáticamente en `outputs/asignaciones.xlsx` y `outputs/resumen.xlsx` al correr el modelo.

---

## **4. Próximos pasos sugeridos**

- Incorporar un módulo de predicción de la demanda que alimente el personal requerido automáticamente en vez de generarlo sintéticamente o cargarlo manualmente.
- Permitir editar la disponibilidad directamente desde la interfaz (producto mínimo viable solo vía generación aleatoria o carga de Excel).
- Evaluar otras funciones objetivo de interés para la compañía
- Revisar otras restricciones que se puedan encontrar en el día a día con los colaboradores
