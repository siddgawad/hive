"""CLI commands for visualization."""

import argparse
import os
import sys
import webbrowser

from framework.visualization import MermaidRenderer


def register_visualization_commands(subparsers: argparse._SubParsersAction) -> None:
    """Register visualization commands with the main CLI."""

    vis_parser = subparsers.add_parser(
        "visualize",
        help="Visualize an agent graph",
        description="Generate a visual diagram of an exported agent's architecture.",
    )
    vis_parser.add_argument(
        "agent_path",
        type=str,
        help="Path to agent folder (containing agent.json)",
    )
    vis_parser.add_argument(
        "--format",
        "-f",
        choices=["html", "mermaid"],
        default="html",
        help="Output format: interactive HTML or raw Mermaid syntax (default: html)",
    )
    vis_parser.add_argument(
        "--output",
        "-o",
        type=str,
        help="Output file path (default: agent_graph.html or stdout for mermaid)",
    )
    vis_parser.add_argument(
        "--no-open",
        action="store_true",
        help="Do not automatically open the HTML file in browser",
    )
    vis_parser.add_argument(
        "--direction",
        choices=["TD", "LR", "BT", "RL"],
        default="TD",
        help="Diagram direction (Top-Down, Left-Right, etc.)",
    )
    vis_parser.set_defaults(func=cmd_visualize)


def cmd_visualize(args: argparse.Namespace) -> int:
    """Execute the visualize command."""
    from framework.runner import AgentRunner

    # Load the agent to get the graph
    try:
        # We use AgentRunner.load just to get the graph structure
        # We don't need to run it, so mocking is fine/irrelevant
        runner = AgentRunner.load(args.agent_path)
    except Exception as e:
        print(f"Error loading agent from {args.agent_path}: {e}", file=sys.stderr)
        return 1

    graph = runner.graph
    print(f"🎨 Generating visualization for agent: {graph.id}...")

    # Render
    renderer = MermaidRenderer(direction=args.direction)
    mermaid_code = renderer.render(graph)

    if args.format == "mermaid":
        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(mermaid_code)
            print(f"✅ Mermaid syntax written to {args.output}")
        else:
            print("-" * 40)
            print(mermaid_code)
            print("-" * 40)

    elif args.format == "html":
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Agent: {graph.id}</title>
    <script type="module">
        import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
        mermaid.initialize({{ startOnLoad: true }});
    </script>
    <style>
        body {{ font-family: system-ui, sans-serif; display: flex; flex-direction: column; align-items: center; padding: 20px; background: #f9f9f9; }}
        .container {{ background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); width: 100%; max-width: 1000px; }}
        .mermaid {{ text-align: center; }}
        h1 {{ color: #333; margin-bottom: 5px; }}
        p {{ color: #666; margin-top: 0; }}
        .meta {{ font-size: 0.9em; color: #888; margin-bottom: 20px; border-bottom: 1px solid #eee; padding-bottom: 10px; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>{graph.id}</h1>
        <p>{getattr(graph, "description", "")}</p>
        <div class="meta">
            Goal: {graph.goal_id} | Nodes: {len(graph.nodes)} | Edges: {len(graph.edges)}
        </div>
        <div class="mermaid">
            {mermaid_code}
        </div>
    </div>
</body>
</html>
"""
        # Determine output path
        output_path = args.output
        if not output_path:
            filename = f"{graph.id}_graph.html"
            output_path = os.path.abspath(filename)

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html_content)

        print(f"✅ Generated HTML: {output_path}")

        if not args.no_open:
            print("🚀 Opening in default browser...")
            webbrowser.open(f"file://{output_path}")

    return 0
