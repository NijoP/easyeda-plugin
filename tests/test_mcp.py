import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))


def test_mcp_server_wiring():
    try:
        import mcp  # the optional MCP SDK  # noqa: F401
    except ImportError:
        print("SKIP — mcp SDK not installed (optional); underlying tools tested elsewhere.")
        return
    from pcbflow import mcp_server
    assert hasattr(mcp_server, "mcp") and callable(mcp_server.main)
    # the tool functions are thin glue over already-tested modules
    assert mcp_server.ipc_trace_width(10)["method"] == "plane/pour"
    assert mcp_server.stitch_pitch(0.7)["stitch_pitch_mm"] > 0
    print("PASS — mcp: server + tools wired.")


if __name__ == "__main__":
    test_mcp_server_wiring()
