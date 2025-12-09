def test_audit_logger_write_and_read(logger_tmp):
    logger_tmp.log_event(
        role="system",
        message="Test event",
        tool_name="test_tool",
        tool_args={"a": 1},
    )

    logs = logger_tmp.show_audit_log(limit=5)
    assert len(logs) == 1

    entry = logs[0]
    assert entry["role"] == "system"
    assert entry["message"] == "Test event"
    assert entry["tool_name"] == "test_tool"