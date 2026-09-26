from linux_server_diag.checks import (
    check_filesystem,
    check_memory,
    check_system,
)


def test_system():
    result = check_system()

    assert "hostname" in result
    assert "cpu_count" in result
    assert result["cpu_count"] > 0


def test_memory():
    result = check_memory()

    assert "total_mb" in result
    assert result["total_mb"] > 0


def test_filesystem():
    result = check_filesystem("/")

    assert result["path"] == "/"
    assert result["size_gb"] > 0
