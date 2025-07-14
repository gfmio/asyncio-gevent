#!/usr/bin/env python3
"""
Script to verify that the asyncio_gevent package directory is included
in both source and wheel distributions.
"""

import sys
import tarfile
import zipfile
from pathlib import Path
from typing import List, Set

PACKAGE_NAME = "asyncio_gevent"
ROOT_INIT_PY = f"{PACKAGE_NAME}/__init__.py"
OTHER_REQUIRED_FILES = {
    "NOTICE",
}


def get_distribution_files() -> List[Path]:
    """Get all distribution files in the dist/ directory."""
    dist_dir = Path("dist")
    if not dist_dir.exists():
        print("❌ dist/ directory does not exist. Run 'task build' first.")
        sys.exit(1)

    files = list(dist_dir.glob("*.tar.gz")) + list(dist_dir.glob("*.whl"))
    if not files:
        print("❌ No distribution files found in dist/. Run 'task build' first.")
        sys.exit(1)

    return files


def get_source_files(package_name: str) -> Set[str]:
    """Get the list of python files in the package."""
    package_dir = Path(package_name)
    base_dir = package_dir.parent

    if not package_dir.exists():
        print(f"❌ {package_name} package directory does not exist.")
        sys.exit(1)

    return {f.relative_to(base_dir).as_posix() for f in package_dir.glob("**/*.py") if f.is_file()}


def extract_file_list(dist_file: Path) -> Set[str]:
    """Extract the list of files from a distribution archive."""
    if dist_file.name.endswith(".tar.gz"):
        # Source distribution (.tar.gz)
        with tarfile.open(dist_file, "r:gz") as tar:
            return set(tar.getnames())
    elif dist_file.suffix == ".whl":
        # Wheel distribution (.whl)
        with zipfile.ZipFile(dist_file, "r") as zip_file:
            return set(zip_file.namelist())
    else:
        raise ValueError(f"Unsupported distribution format for {dist_file}. Expected .tar.gz or .whl")


def determine_path_prefix(file_list: Set[str], root_init_py: str) -> str:
    """Determine the path prefix for the package."""
    matching_files = [f for f in file_list if f.endswith(root_init_py)]

    if not matching_files:
        raise ValueError(f"No {root_init_py} found in the package")

    # Sort by the number of slashes to find the root package directory
    matching_files.sort(key=lambda f: len(Path(f).parts))

    return matching_files[0][: -len(root_init_py)]


def verify_package_contents(
    dist_file: Path, package_name: str, root_init_py: str, other_required_files: Set[str]
) -> bool:
    """Verify that the asyncio_gevent package is properly included."""
    print(f"🔍 Checking {dist_file.name}...")

    source_files = get_source_files(package_name)

    if not source_files:
        print(f"❌ {package_name} package directory is empty or does not exist.")
        return False

    try:
        file_list = extract_file_list(dist_file)

        # Identify the path prefix for the asyncio_gevent package
        path_prefix = determine_path_prefix(file_list, root_init_py)

        # Find all package files in the asyncio_gevent package

        package_files = {f for f in file_list if f.startswith(path_prefix + package_name + "/") and f.endswith(".py")}

        if not package_files:
            print(f"❌ No {package_name} package files found in {dist_file.name}")
            return False

        # Check if the package files match the source files exactly

        unprefixed_package_files = {f[len(path_prefix) :] for f in package_files}

        missing_files = set()
        unexpected_files: set[str] = set()

        if unprefixed_package_files != source_files:
            missing_files = source_files - unprefixed_package_files
            unexpected_files = unprefixed_package_files - source_files

        # Check for other required files

        for required_file in other_required_files:
            if path_prefix + required_file not in file_list:
                missing_files.add(required_file)

        if missing_files:
            print(f"❌ Missing required files in {dist_file.name}: {missing_files}")
            return False

        if unexpected_files:
            print(f"❌ Unexpected files in {dist_file.name}: {unexpected_files}")
            return False

        print(f"✅ {dist_file.name} contains asyncio_gevent package ({len(package_files)} files)")
        return True

    except (OSError, tarfile.TarError, zipfile.BadZipFile) as e:
        print(f"❌ Error checking {dist_file.name}: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error checking {dist_file.name}: {e}")
        raise


def main():
    """Main verification function."""
    print("🔍 Verifying package contents in distributions...")

    dist_files = get_distribution_files()
    all_passed = True

    for dist_file in dist_files:
        if not verify_package_contents(dist_file, PACKAGE_NAME, ROOT_INIT_PY, OTHER_REQUIRED_FILES):
            all_passed = False

    if all_passed:
        print("\n✅ All distributions contain the asyncio_gevent package!")
        sys.exit(0)
    else:
        print("\n❌ Some distributions are missing the asyncio_gevent package!")
        sys.exit(1)


if __name__ == "__main__":
    main()
