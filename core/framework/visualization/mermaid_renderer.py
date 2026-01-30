"""
Mermaid Renderer - Visualization for Agent Graphs.

This module converts a GraphSpec into Mermaid.js flowchart syntax,
enabling developers to visualize the architecture of their agents.

Usage:
    renderer = MermaidRenderer()
    mermaid_code = renderer.render(graph_spec)
    print(mermaid_code)
"""

from framework.graph.edge import EdgeCondition, EdgeSpec, GraphSpec
from framework.graph.node import NodeSpec


class MermaidRenderer:
    """Renders a GraphSpec as a Mermaid flowchart."""

    def __init__(self, direction: str = "TD"):
        """
        Initialize the renderer.

        Args:
            direction: Flowchart direction (TD, LR, BT, RL). Default "TD" (Top-Down).
        """
        self.direction = direction
        self._styles = {
            "node": "fill:#fff,stroke:#333,stroke-width:1px,color:#333",
            "entry": "fill:#e3f2fd,stroke:#2196f3,stroke-width:2px,color:#0d47a1",
            "terminal": "fill:#fbe9e7,stroke:#ff5722,stroke-width:2px,color:#bf360c",
            "pause": "fill:#fff8e1,stroke:#ffc107,stroke-width:2px,stroke-dasharray: 5 5,color:#ff6f00",
            "router": "fill:#f3e5f5,stroke:#9c27b0,stroke-width:1px,shape:rhombus,color:#4a148c",
        }

    def render(self, graph: GraphSpec) -> str:
        """
        Render the graph to Mermaid syntax.

        Args:
            graph: The GraphSpec to render

        Returns:
            String containing the Mermaid chart definition
        """
        lines = [f"graph {self.direction}"]

        # 1. Add Styling Classes
        lines.append("    classDef processing " + self._styles["node"] + ";")
        lines.append("    classDef entry " + self._styles["entry"] + ";")
        lines.append("    classDef terminal " + self._styles["terminal"] + ";")
        lines.append("    classDef pause " + self._styles["pause"] + ";")
        lines.append("    classDef router " + self._styles["router"] + ";")
        lines.append("")

        # 2. Add Nodes
        for node in graph.nodes:
            lines.append(self._render_node(node, graph))

        # 3. Add Edges
        lines.append("")
        for edge in graph.edges:
            lines.append(self._render_edge(edge))

        # 4. Add Router Route Edges (special case for Router nodes)
        for node in graph.nodes:
            if node.node_type == "router" and node.routes:
                for condition, target in node.routes.items():
                    # Create a synthetic edge for the diagram
                    lines.append(f'    {node.id} -- "{condition}" --> {target}')

        return "\n".join(lines)

    def _render_node(self, node: NodeSpec, graph: GraphSpec) -> str:
        """Render a single node definition with appropriate styling."""

        # Determine shape and style class
        shape_open = "["
        shape_close = "]"
        style_class = "processing"

        if node.id == graph.entry_node:
            style_class = "entry"
            shape_open = "(("
            shape_close = "))"
        elif node.id in graph.terminal_nodes:
            style_class = "terminal"
            shape_open = "(["
            shape_close = "])"
        elif node.id in graph.pause_nodes:
            style_class = "pause"
            shape_open = "{{"
            shape_close = "}}"
        elif node.node_type == "router":
            style_class = "router"
            shape_open = "{"
            shape_close = "}"

        # Sanitize label
        label = node.name.replace('"', "'")
        node_def = f'    {node.id}{shape_open}"{label}"{shape_close}:::{style_class}'

        # Add basic interaction hint (optional)
        # click node_id call callback()

        return node_def

    def _render_edge(self, edge: EdgeSpec) -> str:
        """Render a single edge connection."""

        label = ""
        arrow = "-->"

        if edge.condition == EdgeCondition.ON_SUCCESS:
            # Standard arrow
            pass
        elif edge.condition == EdgeCondition.ON_FAILURE:
            arrow = "-.->|failed|"
        elif edge.condition == EdgeCondition.CONDITIONAL:
            expr = edge.condition_expr or "?"
            # Truncate long expressions
            if len(expr) > 20:
                expr = expr[:17] + "..."
            arrow = f'-- "{expr}" -->'
        elif edge.condition == EdgeCondition.LLM_DECIDE:
            arrow = "-.->|llm decision|"

        if edge.description:
            label = f"|{edge.description}|"

        return f"    {edge.source} {arrow} {edge.target}"
