"""
modelo.py
Definición del modelo de programación lineal para la
asignación de turnos. Solo construye el modelo; no lo resuelve
(ver solver.py).
"""

from pyomo.environ import (
    ConcreteModel, Set, Param, Var, Objective, Constraint,
    NonNegativeIntegers, NonNegativeReals, Binary, RangeSet, minimize
)


def construir_modelo(colaboradores, dias, turnos, mercados, R, A):
    """Construye y devuelve el ConcreteModel de Pyomo, sin resolverlo.

    Parámetros
    ----------
    colaboradores : list[str]
    dias : list[str]
    turnos : list[str]  (debe incluir exactamente "Mañana" y "Noche" por night_rest_rule)
    mercados : list[str]
    R : dict[(dia, turno, mercado)] -> int   Personal requerido
    A : dict[(colaborador, dia, turno)] -> 0/1   Disponibilidad
    """
    model = ConcreteModel()

    # CONJUNTOS
    model.C = Set(initialize=colaboradores)
    model.D = Set(initialize=dias)
    model.T = Set(initialize=turnos)
    model.M = Set(initialize=mercados)

    # PARÁMETROS
    model.R = Param(model.D, model.T, model.M, initialize=R, within=NonNegativeIntegers)
    model.A = Param(model.C, model.D, model.T, initialize=A, within=Binary)

    # VARIABLES DE DECISIÓN
    model.x = Var(model.C, model.D, model.T, model.M, within=Binary)  # Asignación
    model.e = Var(model.D, model.T, model.M, within=NonNegativeReals)  # Exceso
    model.f = Var(model.D, model.T, model.M, within=NonNegativeReals)  # Déficit

    # FUNCIÓN OBJETIVO: minimizar la desviación total (exceso + déficit)
    def objective_rule(model):
        return sum(
            model.e[d, t, m] + model.f[d, t, m]
            for d in model.D for t in model.T for m in model.M
        )
    model.obj = Objective(rule=objective_rule, sense=minimize)

    # RESTRICCIONES

    # Un turno como máximo por colaborador por día
    def one_shift_rule(model, i, d):
        return sum(model.x[i, d, t, m] for t in model.T for m in model.M) <= 1
    model.one_shift = Constraint(model.C, model.D, rule=one_shift_rule)

    # Solo se puede asignar si el colaborador está disponible
    def availability_rule(model, i, d, t):
        return sum(model.x[i, d, t, m] for m in model.M) <= model.A[i, d, t]
    model.availability = Constraint(model.C, model.D, model.T, rule=availability_rule)

    # Balance entre personal asignado y requerido (vía exceso/déficit)
    def balance_rule(model, d, t, m):
        return (
            sum(model.x[i, d, t, m] for i in model.C) - model.R[d, t, m]
            == model.e[d, t, m] - model.f[d, t, m]
        )
    model.balance = Constraint(model.D, model.T, model.M, rule=balance_rule)

    # Descanso después de turno noche (no Noche seguido de Mañana al día siguiente)
    dias_list = list(model.D)

    def night_rest_rule(model, i, idx):
        if idx == len(dias_list) - 1:
            return Constraint.Skip
        d = dias_list[idx]
        d_sig = dias_list[idx + 1]
        return (
            sum(model.x[i, d, "Noche", m] for m in model.M) +
            sum(model.x[i, d_sig, "Mañana", m] for m in model.M) <= 1
        )
    model.night_rest = Constraint(model.C, RangeSet(0, len(dias_list) - 1), rule=night_rest_rule)

    # Al menos un día libre por semana (máximo 6 turnos asignados)
    def weekly_rest_rule(model, i):
        return sum(
            model.x[i, d, t, m] for d in model.D for t in model.T for m in model.M
        ) <= 6
    model.weekly_rest = Constraint(model.C, rule=weekly_rest_rule)

    return model