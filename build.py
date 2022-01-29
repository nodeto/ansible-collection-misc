#!/usr/bin/env python
"""Create an importable galaxy artifact."""
import shutil
import pathlib
import subprocess  # nosec
import galaxy_importer.main


def add_docs(file_path: pathlib.Path) -> None:
    """Replace '# {{ documentation }}' with yml found in docs directory.

    Args:
        file_path: path to file to be changed
    """
    documentation_lines = []
    docs_dir = file_path.parent.joinpath("docs")
    for doc_file in docs_dir.joinpath(file_path.stem).iterdir():
        documentation_lines.append(f"{doc_file.stem.upper()} = r'''")
        documentation_lines.extend(doc_file.read_text().splitlines())
        documentation_lines.append("'''")
    documentation_lines = [x + "\n" for x in documentation_lines]

    file_lines = file_path.read_text().splitlines()
    file_lines = [x + "\n" for x in file_lines]
    with file_path.open("wt") as out_f:
        for index, line in enumerate(file_lines):
            if line.startswith("# {{ documentation }}"):
                out_f.writelines(file_lines[:index])
                out_f.writelines(documentation_lines)
                out_f.writelines(file_lines[index + 1 :])
                break
        else:
            out_f.writelines(file_lines)

    shutil.rmtree(docs_dir)


def build() -> None:
    """Create an importable ansible-galaxy artifact."""
    project_root_dir = pathlib.Path(__file__).parent.resolve()
    build_dir = project_root_dir / "build"
    build_dir.mkdir(exist_ok=True)

    for collection in ["nodeto/misc"]:
        collection_src_dir = project_root_dir / collection
        collection_build_dir = build_dir / collection
        collection_build_dir.mkdir(parents=True, exist_ok=True)

        subprocess.run(  # nosec
            [
                "/usr/bin/rsync",
                "-a",
                "--delete",
                f"{collection_src_dir}/.",
                f"{collection_build_dir}/",
            ],
            check=True,
        )

        for plugins_dir in collection_build_dir.joinpath("plugins").iterdir():
            if plugins_dir.is_dir():
                for plugin_file in plugins_dir.iterdir():
                    if plugin_file.suffix == ".py":
                        add_docs(plugin_file)

        galaxy_path = subprocess.check_output(  # nosec command is bash builtin
            "command -v ansible-galaxy", shell=True, executable="/bin/bash"
        )

        build_result = subprocess.check_output(  # nosec vars are not from user input
            [galaxy_path.strip(), "collection", "build", collection, "--force"],
            cwd=str(build_dir),
        )

        built_file = build_result.split()[-1].strip().decode()
        galaxy_importer.main.main(args=(built_file,))


if __name__ == "__main__":
    build()
