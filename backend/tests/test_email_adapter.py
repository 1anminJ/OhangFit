from app.adapters.email import MockEmailAdapter


def test_send_magic_link_does_not_raise(capsys):
    adapter = MockEmailAdapter()
    adapter.send_magic_link("test@example.com", "sometoken")
    captured = capsys.readouterr()
    assert "test@example.com" in captured.out
