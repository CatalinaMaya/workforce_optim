<img src="Holafly-logo.svg.webp" alt="Logo" width="200">

# **Optimización de asignación de turnos de operación**

## <font color='#E7485C'> **Descripción del problema** </font>
El departamento de ventas de la empresa Holafly, cuenta con 60 colaboradores distribuidos entre tres mercados (América, Europa y Asia). Cada día de una semana de planificación, los colaboradores pueden ser asignados a uno de tres turnos de trabajo (mañana, tarde o noche), cada uno con una duración de ocho horas. El objetivo es diseñar un modelo de optimización que determine la asignación diaria de turnos para cada colaborador, de manera que la disponibilidad de personal se ajuste lo mejor posible al personal requerido en cada mercado y turno, respetando las restricciones laborales y de disponibilidad de los colaboradores.

A continuación, se definen explícitamente los elementos que deben considerarse en la modelación:

### **Conjuntos** 
- Colaboradores: conjunto de empleados que deben asignarse
- Mercados: América, Europa, Asia
- Turnos de trabajo: Mañana (6:00-14:00), tarde (14:00-22:00), noche (22:00-6:00)
- Días de la semana de planificación (lunes, martes, miércoles, jueves, viernes, sábado, domingo)

### **Parámetros**
- Personal requerido por día, turno y mercado.
- Disponibilidad de cada colaborador para trabajar en un día y turno determinados.

### **Decisiones**
- Turno y mercado asignado a cada colaborador cada día

### **Objetivo**
- Minimizar la desviación absoluta entre el personal asignado y el personal requerido.

### **Restricciones**
- Cada colaborador puede ser asignado, como máximo, a un turno por día.
- Las asignaciones deben respetar la disponibilidad de cada colaborador.
- Un colaborador que trabaje en el turno de noche no puede ser asignado al turno de mañana del día siguiente.
- Cada colaborador debe tener al menos un día completo de descanso durante la semana.

### **Supuestos**
- Cada colaborador puede atender cualquiera de los tres mercados

## **Modelación**
### **Conjuntos**
- $C:$ Colaboradores ($i$)
- $M:$ Mercados ($m$)
- $T:$ Turnos ($t$)
- $D:$ Días de la semana ($d$)

### **Parámetros**
- $R_{dtm}:$ Personal requerido el día $d$, turno $t$, mercado $m$
- $A_{idt}:$ 1 si el colaborador $i$ está disponible el día $i$ en el turno $t$


### **Decisiones**
- $x_{idtm}:$ 1 si el colaborador $i$ trabaja el día $d$, turno $t$, mercado $m$, 0 en otro caso

Variables auxiliares:
- $e_{dtm} \geq 0$: exceso de personal
- $f_{dtm} \geq 0$: déficit de personal

### **Función objetivo**
Minimizar la desviación absoluta entre el personal asignado y el requerido.

min $ \sum_{d \in D}\sum_{t \in T}\sum_{m \in M} (e_{dtm} + f_{dtm})$


### **Restricciones**
1. Un turno por colaborador al día: Cada colaborador puede trabajar como máximo un turno diario.

$$ \sum_{t \in T}\sum_{m \in M} x_{idtm}\leq 1 \forall i \in C, d \in D $$

2. Respetar disponibilidad: Un colaborador solo puede ser asignado si está disponible.
$$ \sum_{m \in M} x_{idtm}\leq A_{ids} \forall i \in C, d \in D, t\in T$$

3. Balance entre asignación y requerimiento: La diferencia entre personal asignado y requerido se representa mediante exceso y déficit.
$$ \sum_{i \in C} x_{idtm} - R_{dtm} = e_{dtm} - f_{dtm} \forall d \in D, t \in T, m\in M$$

4. Descanso después de turno de noche
$$ \sum_{m \in M} x_{id,t_N,m} + \sum_{m \in M} x_{i,d+1,t_M,m} \leq 1 \forall i, d = 1, ..., 7 $$

5. Mínimo de descanso semanal: Cada colaborador debe tener al menos un día sin asignación.
$$ \sum_{d \in D}\sum_{t \in T}\sum_{m \in M} x_{idtm}\leq 6 \forall i \in C $$

6. Tipo de variables
$$x_{idtm} \in {0,1} $$
$$e_{dtm} \geq 0$$
$$f_{dtm} \geq 0$$
