from dataclasses import dataclass

import networkx as nx

from conlog.datatypes import (
    Addition,
    ConditionalDecrement,
    ConditionalIncrement,
    Initial,
    Subtraction,
)


@dataclass(frozen=True)
class Positive:
    var: str


@dataclass(frozen=True)
class Negative:
    var: str


@dataclass(frozen=True)
class Var:
    var: str


PositiveTerminal = object()

NegativeTerminal = object()


def find_initial(g: nx.Graph) -> Initial:
    for node in g.nodes:
        match node.op:
            case Initial():
                return node.op
            case _:
                pass

    raise ValueError("No Initial node")


def compute_monotone_variables(g: nx.Graph) -> tuple[set[str], set[str]]:
    """Identify whether each variable is monotone increasing, monotone decreasing, or neither."""

    # For each variable v, we produce nodes v, v+, and v-. We make nodes + and
    # - as well.
    #
    # Whenever a node modifies a variable v by a constant non-negative quantity,
    # we map v -> +, v+ -> +, and v- -> -.
    #
    # Whenever a node modifies a variable v by a constant non-positive quantity,
    # we map v -> -, v+ -> -, and v- -> +.
    #
    # Whenever a node modifies a variable v by adding a variable w, we map
    # v -> w+.
    #
    # Whenever a node modifies a variable v by subtracting a variable w, we map
    # v -> w-.
    #
    # If a variable v can only reach + nodes (or cannot reach -) it is monotone non-decreasing.
    #
    # If a variable v can only reach - nodes (or cannot reach +) it is monotone non-increasing.

    initial = find_initial(g)

    monotone_graph = nx.DiGraph()

    vars = {}
    for var in initial.free:
        vars[var] = Var(var)
    for var, _ in initial.fixed:
        vars[var] = Var(var)

    pos_vars = {}
    for var in vars:
        pos_vars[var] = Positive(var)

    neg_vars = {}
    for var in vars:
        neg_vars[var] = Negative(var)

    monotone_graph.add_nodes_from(vars.values())
    monotone_graph.add_nodes_from(pos_vars.values())
    monotone_graph.add_nodes_from(neg_vars.values())
    monotone_graph.add_node(PositiveTerminal)
    monotone_graph.add_node(NegativeTerminal)

    for node in g.nodes:
        match node.op:
            case Addition(lhs=lhs, rhs=rhs):
                if isinstance(rhs, int):
                    if rhs > 0:
                        monotone_graph.add_edge(vars[lhs], PositiveTerminal)
                        monotone_graph.add_edge(pos_vars[lhs], PositiveTerminal)
                        monotone_graph.add_edge(neg_vars[lhs], NegativeTerminal)
                    elif rhs < 0:
                        monotone_graph.add_edge(vars[lhs], NegativeTerminal)
                        monotone_graph.add_edge(pos_vars[lhs], NegativeTerminal)
                        monotone_graph.add_edge(neg_vars[lhs], PositiveTerminal)
                else:
                    monotone_graph.add_edge(vars[lhs], pos_vars[rhs])
                    monotone_graph.add_edge(pos_vars[lhs], pos_vars[rhs])
                    monotone_graph.add_edge(neg_vars[lhs], neg_vars[rhs])
            case Subtraction(lhs=lhs, rhs=rhs):
                if isinstance(rhs, int):
                    if rhs > 0:
                        monotone_graph.add_edge(vars[lhs], NegativeTerminal)
                        monotone_graph.add_edge(pos_vars[lhs], NegativeTerminal)
                        monotone_graph.add_edge(neg_vars[lhs], PositiveTerminal)
                    elif rhs < 0:
                        monotone_graph.add_edge(vars[lhs], PositiveTerminal)
                        monotone_graph.add_edge(pos_vars[lhs], PositiveTerminal)
                        monotone_graph.add_edge(neg_vars[lhs], NegativeTerminal)
                else:
                    monotone_graph.add_edge(vars[lhs], neg_vars[rhs])
                    monotone_graph.add_edge(pos_vars[lhs], neg_vars[rhs])
                    monotone_graph.add_edge(neg_vars[lhs], pos_vars[rhs])
            case ConditionalIncrement(lhs=lhs, rhs=rhs):
                if isinstance(rhs, int):
                    if rhs > 0:
                        monotone_graph.add_edge(vars[lhs], PositiveTerminal)
                        monotone_graph.add_edge(pos_vars[lhs], PositiveTerminal)
                        monotone_graph.add_edge(neg_vars[lhs], NegativeTerminal)
                else:
                    monotone_graph.add_edge(vars[lhs], PositiveTerminal)
                    monotone_graph.add_edge(pos_vars[lhs], PositiveTerminal)
                    monotone_graph.add_edge(neg_vars[lhs], NegativeTerminal)

            case ConditionalDecrement(lhs=lhs, rhs=rhs):
                if isinstance(rhs, int):
                    if rhs > 0:
                        monotone_graph.add_edge(vars[lhs], NegativeTerminal)
                        monotone_graph.add_edge(pos_vars[lhs], NegativeTerminal)
                        monotone_graph.add_edge(neg_vars[lhs], PositiveTerminal)
                else:
                    monotone_graph.add_edge(vars[lhs], NegativeTerminal)
                    monotone_graph.add_edge(pos_vars[lhs], NegativeTerminal)
                    monotone_graph.add_edge(neg_vars[lhs], PositiveTerminal)

    monotone_increasing = set()
    monotone_decreasing = set()

    for var in vars:
        dfs = nx.dfs_tree(monotone_graph, vars[var])

        reaches_pos = PositiveTerminal in dfs.nodes
        reaches_neg = NegativeTerminal in dfs.nodes

        if not reaches_neg:
            monotone_increasing.add(var)
        if not reaches_pos:
            monotone_decreasing.add(var)

    return monotone_increasing, monotone_decreasing
