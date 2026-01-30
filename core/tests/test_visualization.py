"""
Tests for the Visualization Module.
"""

from framework.graph.edge import EdgeCondition, EdgeSpec, GraphSpec
from framework.graph.node import NodeSpec
from framework.visualization import MermaidRenderer


def test_renderer_output_structure():
    """Test that the renderer produces valid Mermaid syntax structure."""

    # 1. Setup a minimal graph
    node1 = NodeSpec(
        id="start",
        name="Start Node",
        description="Entry",
        node_type="function",
        output_keys=["data"],
    )

    node2 = NodeSpec(
        id="end",
        name="End Node",
        description="Exit",
        node_type="function",
        input_keys=["data"],
    )

    edge = EdgeSpec(
        id="e1", source="start", target="end", condition=EdgeCondition.ON_SUCCESS
    )

    graph = GraphSpec(
        id="test-graph",
        goal_id="test-goal",
        entry_node="start",
        terminal_nodes=["end"],
        nodes=[node1, node2],
        edges=[edge],
    )

    # 2. Render
    renderer = MermaidRenderer(direction="LR")
    output = renderer.render(graph)

    # 3. Assertions
    # Check direction
    assert "graph LR" in output

    # Check styling definitions
    assert "classDef entry" in output
    assert "classDef terminal" in output

    # Check node rendering
    assert 'start(("Start Node")):::entry' in output
    assert 'end(["End Node"]):::terminal' in output

    # Check edge rendering
    assert "start --> end" in output


def test_router_node_rendering():
    """Test that router nodes and their routes are rendered correctly."""

    start_node = NodeSpec(
        id="start",
        name="Start",
        description="Entry",
        node_type="function",
        output_keys=[],
    )

    router = NodeSpec(
        id="router",
        name="My Router",
        description="Splits flow",
        node_type="router",
        routes={"yes": "node_yes", "no": "node_no"},
    )

    graph = GraphSpec(
        id="router-graph",
        goal_id="g1",
        entry_node="start",
        nodes=[start_node, router],
        edges=[],
    )

    renderer = MermaidRenderer()
    output = renderer.render(graph)

    # Check router specific styling
    assert "classDef router" in output
    assert 'router{"My Router"}:::router' in output

    # Check synthetic route edges
    assert 'router -- "yes" --> node_yes' in output
    assert 'router -- "no" --> node_no' in output
