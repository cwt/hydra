import pytest
from unittest.mock import patch
import os  # For os.path.join

# Assuming ssh.py is importable
from ananta.ssh import get_ssh_keys


# Use patch to mock os.path.exists and os.path.expanduser
@patch("ananta.ssh.os.path.exists")
@patch("ananta.ssh.os.path.expanduser", return_value="/fake/home/.ssh")
def test_get_ssh_keys(mock_expanduser, mock_exists):
    """Tests the logic for selecting SSH keys."""

    # --- Scenario 1: Specific key path provided ---
    assert get_ssh_keys("/path/to/my/specific_key", None) == [
        "/path/to/my/specific_key"
    ]
    assert get_ssh_keys("/another/key", "/default/key") == ["/another/key"]
    # Ensure os.path.exists was not called in these cases
    assert not mock_exists.called

    # Reset mock calls for the next scenarios
    mock_exists.reset_mock()

    # --- Scenario 2: Host file specifies '#', default key provided ---
    assert get_ssh_keys("#", "/path/to/default_key") == ["/path/to/default_key"]
    assert not mock_exists.called

    mock_exists.reset_mock()

    # --- Scenario 3: Host file specifies '#', no default key, check common keys ---

    # Mock os.path.exists to simulate finding id_ed25519 first
    def exists_side_effect_ed25519(path):
        if path == "/fake/home/.ssh/id_ed25519":
            return True
        return False

    mock_exists.side_effect = exists_side_effect_ed25519
    expected_keys_ed25519 = [os.path.join("/fake/home/.ssh", "id_ed25519")]
    assert get_ssh_keys("#", None) == expected_keys_ed25519
    # Check that expanduser was called once and exists was called for id_ed25519
    mock_expanduser.assert_called_once_with("~/.ssh")
    mock_exists.assert_any_call("/fake/home/.ssh/id_ed25519")

    mock_exists.reset_mock()
    mock_expanduser.reset_mock()  # Reset call count

    # Mock os.path.exists to simulate finding only id_rsa
    def exists_side_effect_rsa(path):
        if path == "/fake/home/.ssh/id_rsa":
            return True
        return False

    mock_exists.side_effect = exists_side_effect_rsa
    expected_keys_rsa = [os.path.join("/fake/home/.ssh", "id_rsa")]
    assert get_ssh_keys("#", None) == expected_keys_rsa
    mock_expanduser.assert_called_once_with("~/.ssh")
    mock_exists.assert_any_call("/fake/home/.ssh/id_ed25519")  # Checked first
    mock_exists.assert_any_call(
        "/fake/home/.ssh/id_rsa"
    )  # Then checked and found

    mock_exists.reset_mock()
    mock_expanduser.reset_mock()

    # Mock os.path.exists to simulate finding no common keys
    mock_exists.side_effect = lambda path: False
    with pytest.raises(ConnectionError, match="No SSH keys found"):
        get_ssh_keys("#", None)
    mock_expanduser.assert_called_once_with("~/.ssh")
    assert mock_exists.call_count == 4  # Checked all common keys

    # --- Scenario 4: key_path is None or empty string (should behave like '#') ---
    mock_exists.reset_mock()
    mock_expanduser.reset_mock()
    mock_exists.side_effect = exists_side_effect_ed25519  # Find ed25519 again
    assert get_ssh_keys(None, None) == expected_keys_ed25519
    assert get_ssh_keys("", None) == expected_keys_ed25519
