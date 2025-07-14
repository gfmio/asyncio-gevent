import tarfile
import zipfile

import pytest

import scripts.verify_package_contents as vpc


@pytest.fixture
def tmp_package(tmp_path):
    pkg = tmp_path / vpc.PACKAGE_NAME
    pkg.mkdir()
    (pkg / "__init__.py").write_text("# init")
    (pkg / "mod.py").write_text("# mod")
    return pkg


def test_get_distribution_files_no_dist(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    with pytest.raises(SystemExit):
        vpc.get_distribution_files()


def test_get_distribution_files_empty(monkeypatch, tmp_path):
    dist = tmp_path / "dist"
    dist.mkdir()
    monkeypatch.chdir(tmp_path)
    with pytest.raises(SystemExit):
        vpc.get_distribution_files()


def test_get_distribution_files_found(monkeypatch, tmp_path):
    dist = tmp_path / "dist"
    dist.mkdir()
    (dist / "foo.tar.gz").write_text("x")
    (dist / "bar.whl").write_text("y")
    monkeypatch.chdir(tmp_path)
    files = vpc.get_distribution_files()
    assert len(files) == 2
    assert any(str(f).endswith(".tar.gz") for f in files)
    assert any(str(f).endswith(".whl") for f in files)


def test_get_distribution_files_ignores_other_extensions(monkeypatch, tmp_path):
    dist = tmp_path / "dist"
    dist.mkdir()
    (dist / "foo.tar.gz").write_text("x")
    (dist / "bar.whl").write_text("y")
    (dist / "baz.txt").write_text("z")
    (dist / "README.md").write_text("readme")
    monkeypatch.chdir(tmp_path)
    files = vpc.get_distribution_files()
    # Only .tar.gz and .whl should be included
    assert len(files) == 2
    assert all(str(f).endswith((".tar.gz", ".whl")) for f in files)


def test_get_source_files_missing(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    with pytest.raises(SystemExit):
        vpc.get_source_files("not_a_package")


def test_get_source_files(tmp_package, monkeypatch):
    monkeypatch.chdir(tmp_package.parent)
    files = vpc.get_source_files(vpc.PACKAGE_NAME)
    assert f"{vpc.PACKAGE_NAME}/__init__.py" in files
    assert f"{vpc.PACKAGE_NAME}/mod.py" in files


def test_extract_file_list_tar(tmp_path):
    tar_path = tmp_path / "test.tar.gz"
    with tarfile.open(tar_path, "w:gz") as tar:
        f = tmp_path / "foo.txt"
        f.write_text("hi")
        tar.add(f, arcname="foo.txt")
    files = vpc.extract_file_list(tar_path)
    assert "foo.txt" in files


def test_extract_file_list_whl(tmp_path):
    whl_path = tmp_path / "test.whl"
    with zipfile.ZipFile(whl_path, "w") as z:
        z.writestr("bar.txt", "hi")
    files = vpc.extract_file_list(whl_path)
    assert "bar.txt" in files


def test_extract_file_list_invalid(tmp_path):
    p = tmp_path / "foo.txt"
    p.write_text("x")
    with pytest.raises(ValueError):
        vpc.extract_file_list(p)


def test_determine_path_prefix():
    files = {"foo-1.0/asyncio_gevent/__init__.py", "foo-1.0/asyncio_gevent/mod.py"}
    prefix = vpc.determine_path_prefix(files, "asyncio_gevent/__init__.py")
    assert prefix == "foo-1.0/"


def test_determine_path_prefix_missing():
    files = {"foo-1.0/other/__init__.py"}
    with pytest.raises(ValueError):
        vpc.determine_path_prefix(files, "asyncio_gevent/__init__.py")


def make_dist_archive(tmp_path, files, archive_format="tar"):
    dist_path = tmp_path / ("dist.tar.gz" if archive_format == "tar" else "dist.whl")
    if archive_format == "tar":
        with tarfile.open(dist_path, "w:gz") as tar:
            for name, content in files.items():
                f = tmp_path / name
                f.parent.mkdir(parents=True, exist_ok=True)
                f.write_text(content)
                tar.add(f, arcname=name)
    else:
        with zipfile.ZipFile(dist_path, "w") as z:
            for name, content in files.items():
                z.writestr(name, content)
    return dist_path


@pytest.mark.parametrize("kind", ["tar", "whl"])
def test_verify_package_contents_success(tmp_path, kind, monkeypatch):
    # Simulate source files
    pkg = tmp_path / vpc.PACKAGE_NAME
    pkg.mkdir()
    (pkg / "__init__.py").write_text("# init")
    (pkg / "mod.py").write_text("# mod")
    (tmp_path / "NOTICE").write_text("notice")
    monkeypatch.chdir(tmp_path)
    # Simulate dist archive
    files = {
        f"foo-1.0/{vpc.PACKAGE_NAME}/__init__.py": "# init",
        f"foo-1.0/{vpc.PACKAGE_NAME}/mod.py": "# mod",
        "foo-1.0/NOTICE": "notice",
    }
    dist_path = make_dist_archive(tmp_path, files, kind)
    assert vpc.verify_package_contents(dist_path, vpc.PACKAGE_NAME, vpc.ROOT_INIT_PY, vpc.OTHER_REQUIRED_FILES)


@pytest.mark.parametrize("kind", ["tar", "whl"])
def test_verify_package_contents_missing_file(tmp_path, kind, monkeypatch):
    pkg = tmp_path / vpc.PACKAGE_NAME
    pkg.mkdir()
    (pkg / "__init__.py").write_text("# init")
    (pkg / "mod.py").write_text("# mod")
    (tmp_path / "NOTICE").write_text("notice")
    monkeypatch.chdir(tmp_path)
    files = {
        f"foo-1.0/{vpc.PACKAGE_NAME}/__init__.py": "# init",
        "foo-1.0/NOTICE": "notice",
    }
    dist_path = make_dist_archive(tmp_path, files, kind)
    assert not vpc.verify_package_contents(dist_path, vpc.PACKAGE_NAME, vpc.ROOT_INIT_PY, vpc.OTHER_REQUIRED_FILES)


@pytest.mark.parametrize("kind", ["tar", "whl"])
def test_verify_package_contents_unexpected_file(tmp_path, kind, monkeypatch):
    pkg = tmp_path / vpc.PACKAGE_NAME
    pkg.mkdir()
    (pkg / "__init__.py").write_text("# init")
    (pkg / "mod.py").write_text("# mod")
    (tmp_path / "NOTICE").write_text("notice")
    monkeypatch.chdir(tmp_path)
    files = {
        f"foo-1.0/{vpc.PACKAGE_NAME}/__init__.py": "# init",
        f"foo-1.0/{vpc.PACKAGE_NAME}/mod.py": "# mod",
        f"foo-1.0/{vpc.PACKAGE_NAME}/extra.py": "# extra",
        "foo-1.0/NOTICE": "notice",
    }
    dist_path = make_dist_archive(tmp_path, files, kind)
    assert not vpc.verify_package_contents(dist_path, vpc.PACKAGE_NAME, vpc.ROOT_INIT_PY, vpc.OTHER_REQUIRED_FILES)


@pytest.mark.parametrize("kind", ["tar", "whl"])
def test_verify_other_missing_file(tmp_path, kind, monkeypatch):
    pkg = tmp_path / vpc.PACKAGE_NAME
    pkg.mkdir()
    (pkg / "__init__.py").write_text("# init")
    (pkg / "mod.py").write_text("# mod")
    monkeypatch.chdir(tmp_path)
    files = {
        f"foo-1.0/{vpc.PACKAGE_NAME}/__init__.py": "# init",
    }
    dist_path = make_dist_archive(tmp_path, files, kind)
    assert not vpc.verify_package_contents(dist_path, vpc.PACKAGE_NAME, vpc.ROOT_INIT_PY, vpc.OTHER_REQUIRED_FILES)
