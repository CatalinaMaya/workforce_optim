# <font color='#E7485C'> ** Optimización de asignación de turnos de operación** </font>

## <font color='#E7485C'> **Descripción del problema** </font>

El departamento de ventas de la empresa Holafly, cuenta con 60 colaboradores distribuidos entre tres mercados (América, Europa y Asia). Cada día de una semana de planificación, los colaboradores pueden ser asignados a uno de tres turnos de trabajo (mañana, tarde o noche), cada uno con una duración de ocho horas. El objetivo es diseñar un modelo de optimización que determine la asignación diaria de turnos para cada colaborador, de manera que la disponibilidad de personal se ajuste lo mejor posible al personal requerido en cada mercado y turno, respetando las restricciones laborales y de disponibilidad de los colaboradores.

A continuación, se definen explícitamente los elementos que deben considerarse en la modelación:

### <font color='#cc7285'> **Conjuntos** </font>
- Colaboradores: conjunto de empleados que deben asignarse
- Mercados: América, Europa, Asia
- Turnos de trabajo: Mañana (6:00-14:00), tarde (14:00-22:00), noche (22:00-6:00)
- Días de la semana de planificación (lunes, martes, miércoles, jueves, viernes, sábado, domingo)

### <font color='#cc7285'> **Parámetros** </font>
- Personal requerido por día, turno y mercado.
- Disponibilidad de cada colaborador para trabajar en un día y turno determinados.

### <font color='#cc7285'> **Decisiones** </font>
- Turno y mercado asignado a cada colaborador cada día

### <font color='#cc7285'> **Objetivo** </font>
- Minimizar la desviación absoluta entre el personal asignado y el personal requerido.

### <font color='#cc7285'> **Restricciones** </font>
- Cada colaborador puede ser asignado, como máximo, a un turno por día.
- Las asignaciones deben respetar la disponibilidad de cada colaborador.
- Un colaborador que trabaje en el turno de noche no puede ser asignado al turno de mañana del día siguiente.
- Cada colaborador debe tener al menos un día completo de descanso durante la semana.

### <font color='#cc7285'> **Supuestos** </font>
- Cada colaborador puede atender cualquiera de los tres mercados
