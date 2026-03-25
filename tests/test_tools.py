"""Tests for the MCP server tools using mock mode."""

import pytest

from berrevoets_f360_mcp.mock import mock_response


class TestMockResponses:
    """Verify all mock handlers return expected structure."""

    def test_ping(self):
        result = mock_response("ping", {})
        assert result["status"] == "success"
        assert result["result"]["pong"] is True
        assert result["mode"] == "mock"

    def test_get_scene_info(self):
        result = mock_response("get_scene_info", {})
        r = result["result"]
        assert "design_name" in r
        assert "bodies" in r
        assert "sketches" in r
        assert isinstance(r["bodies"], list)

    def test_get_object_info(self):
        result = mock_response("get_object_info", {"name": "TestBody"})
        r = result["result"]
        assert r["found"] is True
        assert r["name"] == "TestBody"
        assert "bounding_box" in r

    def test_list_components(self):
        result = mock_response("list_components", {})
        r = result["result"]
        assert "components" in r
        assert r["count"] >= 1

    def test_export_stl(self):
        result = mock_response(
            "export_stl", {"body_name": "Body1", "file_path": "/tmp/test.stl"}
        )
        r = result["result"]
        assert r["exported"] is True

    def test_export_step(self):
        result = mock_response(
            "export_step", {"file_path": "/tmp/test.step"}
        )
        r = result["result"]
        assert r["exported"] is True

    def test_export_f3d(self):
        result = mock_response("export_f3d", {"file_path": "/tmp/test.f3d"})
        r = result["result"]
        assert r["exported"] is True

    def test_import_step(self):
        result = mock_response(
            "import_step", {"file_path": "/tmp/test.step"}
        )
        r = result["result"]
        assert r["imported"] is True

    def test_import_f3d(self):
        result = mock_response("import_f3d", {"file_path": "/tmp/test.f3d"})
        r = result["result"]
        assert r["imported"] is True

    def test_measure_distance(self):
        result = mock_response(
            "measure_distance",
            {"entity_one": "Body1", "entity_two": "Body2"},
        )
        r = result["result"]
        assert "distance" in r
        assert "point_one" in r
        assert "point_two" in r

    def test_measure_angle(self):
        result = mock_response(
            "measure_angle",
            {"entity_one": "Body1", "entity_two": "Body2"},
        )
        r = result["result"]
        assert "angle_degrees" in r

    def test_get_physical_properties(self):
        result = mock_response(
            "get_physical_properties", {"body_name": "Body1"}
        )
        r = result["result"]
        assert "mass" in r
        assert "volume" in r
        assert "center_of_mass" in r

    def test_get_parameters(self):
        result = mock_response("get_parameters", {})
        r = result["result"]
        assert "parameters" in r
        assert r["count"] >= 1

    def test_create_parameter(self):
        result = mock_response(
            "create_parameter",
            {"name": "width", "value": 5.0, "unit": "cm"},
        )
        r = result["result"]
        assert r["created"] is True
        assert r["name"] == "width"

    def test_set_parameter(self):
        result = mock_response(
            "set_parameter", {"name": "width", "value": 10.0}
        )
        r = result["result"]
        assert r["updated"] is True

    def test_delete_parameter(self):
        result = mock_response("delete_parameter", {"name": "width"})
        r = result["result"]
        assert r["deleted"] is True

    def test_execute_code(self):
        result = mock_response(
            "execute_code", {"code": "print('hello')"}
        )
        r = result["result"]
        assert r["executed"] is True

    def test_undo(self):
        result = mock_response("undo", {})
        r = result["result"]
        assert r["undone"] is True

    def test_delete_all(self):
        result = mock_response("delete_all", {})
        r = result["result"]
        assert r["deleted"] is True

    def test_unknown_command(self):
        result = mock_response("nonexistent_command", {})
        assert result["status"] == "error"
        assert "Unknown command" in result["message"]
