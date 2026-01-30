"""
Visualize Agent Example.

This script demonstrates how to key the new `framework.visualization` module
to generate a diagram of an agent.
"""

from framework.graph import EdgeCondition, EdgeSpec, GraphSpec, NodeSpec
from framework.visualization import MermaidRenderer


def build_sample_graph():
    """Build a sample graph manually (same as manual_agent.py)."""
    node1 = NodeSpec(
        id="greeter",
        name="Greeter",
        description="Generates a simple greeting",
        node_type="function",
        output_keys=["greeting"],
    )

    node2 = NodeSpec(
        id="uppercaser",
        name="Uppercaser",
        description="Converts greeting to uppercase",
        node_type="function",
        input_keys=["greeting"],
        output_keys=["final_greeting"],
    )

    edge1 = EdgeSpec(
        id="greet-to-upper",
        source="greeter",
        target="uppercaser",
        condition=EdgeCondition.ON_SUCCESS,
    )

    graph = GraphSpec(
        id="greeting-agent",
        goal_id="greet-user",
        entry_node="greeter",
        terminal_nodes=["uppercaser"],
        nodes=[node1, node2],
        edges=[edge1],
    )
    return graph


def main():
    print("🎨 Generating Mermaid Diagram for Greeting Agent...")

    graph = build_sample_graph()
    renderer = MermaidRenderer()
    diagram = renderer.render(graph)

    # Create HTML with Mermaid.js
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Agent Graph Visualization</title>
        <script type="module">
            import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
            mermaid.initialize({{ startOnLoad: true }});
        </script>
        <style>
            body {{ font-family: sans-serif; display: flex; flex-direction: column; align-items: center; padding: 20px; }}
            .mermaid {{ width: 100%; max-width: 800px; text-align: center; }}
            h1 {{ color: #333; }}
        </style>
    </head>
    <body>
        <h1>Agent Architecture: {graph.id}</h1>
        <div class="mermaid">
            {diagram}
        </div>
    </body>
    </html>
    """

    import os
    import webbrowser

    output_file = os.path.abspath("agent_graph.html")
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"✅ Generated: {output_file}")
    print("🚀 Opening in default browser...")
    webbrowser.open(f"file://{output_file}")


if __name__ == "__main__":
    main()
