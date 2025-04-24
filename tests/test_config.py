from ananta.config import get_hosts

# Sample CSV content for testing
HOSTS_CSV_CONTENT = """
# This is a comment line
host-1,10.0.0.1,22,user1,/path/to/key1,web:db
host-2,10.0.0.2,2202,user2,#,web
host-3,10.0.0.3,22,user3,/specific/key3,app
#host-4,10.0.0.4,22,user4,#,disabled
host-5,10.0.0.5,22,user5,#
host-6,10.0.0.6,bad-port-format,user6,#, Tag With Space
"""


# Test successful parsing and no tag filtering
def test_get_hosts_no_tags(tmp_path):
    """Tests parsing the hosts file without any tag filtering."""
    p = tmp_path / "hosts.csv"
    p.write_text(HOSTS_CSV_CONTENT, encoding="utf-8")

    hosts, max_len = get_hosts(str(p), None)  # host_tags is None

    assert (
        len(hosts) == 4
    )  # host-1, host-2, host-3, host-5 (host-4 is commented, host-6 bad format)
    assert max_len == 6  # Length of "host-1", "host-2", etc.
    assert hosts[0] == ("host-1", "10.0.0.1", 22, "user1", "/path/to/key1")
    assert hosts[1] == ("host-2", "10.0.0.2", 2202, "user2", "#")
    assert hosts[2] == ("host-3", "10.0.0.3", 22, "user3", "/specific/key3")
    assert hosts[3] == ("host-5", "10.0.0.5", 22, "user5", "#")


# Test tag filtering
def test_get_hosts_with_tags(tmp_path):
    """Tests parsing with tag filtering."""
    p = tmp_path / "hosts.csv"
    p.write_text(HOSTS_CSV_CONTENT, encoding="utf-8")

    # Filter for 'web' tag
    hosts_web, max_len_web = get_hosts(str(p), "web")
    assert len(hosts_web) == 2
    assert [h[0] for h in hosts_web] == ["host-1", "host-2"]
    assert max_len_web == 6

    # Filter for 'app' tag
    hosts_app, max_len_app = get_hosts(str(p), "app")
    assert len(hosts_app) == 1
    assert hosts_app[0][0] == "host-3"
    assert max_len_app == 6

    # Filter for multiple tags 'db' or 'app'
    hosts_db_app, max_len_db_app = get_hosts(str(p), "db,app")
    assert len(hosts_db_app) == 2
    assert [h[0] for h in hosts_db_app] == ["host-1", "host-3"]
    assert max_len_db_app == 6

    # Filter for non-existent tag
    hosts_empty, max_len_zero = get_hosts(str(p), "nomatch")
    assert hosts_empty == []
    assert max_len_zero == 0


# Test handling of malformed lines (should be skipped)
def test_get_hosts_skips_malformed(tmp_path, capsys):
    """Tests that lines with format errors (like non-integer port) are skipped."""
    p = tmp_path / "hosts.csv"
    p.write_text(
        HOSTS_CSV_CONTENT, encoding="utf-8"
    )  # Includes host-6 with bad port

    hosts, _ = get_hosts(str(p), None)
    assert len(hosts) == 4  # host-6 should be skipped
    assert "host-6" not in [h[0] for h in hosts]

    # Check if the error message was printed (optional, requires capsys fixture)
    captured = capsys.readouterr()
    assert (
        f"Hosts file: {str(p)} parse error at row 7" in captured.out
    )  # Row numbers start from 1
