#!/usr/bin/env python3
"""
Ludo King Engine - Main Entry Point

Launches the web-based Ludo AI Visualizer interface.
"""

from ludo_interface.app import launch_app


def main():
    """Launch the Ludo AI Visualizer web interface."""
    print("🚀 Starting Ludo AI Visualizer...")
    app = launch_app()
    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        show_api=False,
        share=False
    )


if __name__ == "__main__":
    main()
