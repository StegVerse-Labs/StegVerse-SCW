from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class TaskNode:
    id: str
    after: list[str] = field(default_factory=list)


class TaskGraph:
    """
    Very small DAG-like planner. For now we just linearize respecting simple
    "after" dependencies if present.
    """

    def __init__(self, nodes: dict[str, TaskNode]):
        self.nodes = nodes

    def linear_order(self, selected: list[str]) -> list[str]:
        """
        Return tasks in a sane execution order. For now, we do a simple
        depth-first topological sort over the selected tasks.
        """
        result: list[str] = []
        visited: dict[str, bool] = {}

        def visit(tid: str):
            if tid in visited:
                return
            visited[tid] = True
            node = self.nodes.get(tid)
            if not node:
                result.append(tid)
                return
            for dep in node.after:
                visit(dep)
            result.append(tid)

        for tid in selected:
            visit(tid)

        # Keep order stable while removing duplicates
        seen = set()
        ordered: list[str] = []
        for t in result:
            if t not in seen:
                seen.add(t)
                ordered.append(t)
        return ordered


def default_task_graph() -> TaskGraph:
    """
    Hardcoded Phase 2 default graph:
    - economic_snapshot before status_digest
    - repo_hygiene can run anytime
    """
    nodes = {
        "economic_snapshot": TaskNode("economic_snapshot", after=[]),
        "repo_hygiene": TaskNode("repo_hygiene", after=[]),
        "status_digest": TaskNode("status_digest", after=["economic_snapshot"]),
    }
    return TaskGraph(nodes)
