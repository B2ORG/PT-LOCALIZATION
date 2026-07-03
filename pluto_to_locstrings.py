# Converts runtime dumped strings to locstring file format

from copy import deepcopy
from typing import Self
import sys, pathlib


class StrFile:
    HEADER = [
        'VERSION             "1"\n',
        'CONFIG              "C:/projects/cod/t6/bin/StringEd.cfg"\n'
        'FILENOTES           "Dumped by Plutonium team, converted by Zi0"\n'
        '\n'
    ]
    def __init__(self, path: pathlib.Path):
        self.path = path
        self.strings = {}
        pair = []
        for line in path.read_text("utf-8").split("\n"):
            if line.startswith("REFERENCE"):
                pair.append(line[20:])
            elif len(pair) == 1 and line.startswith("LANG_ENGLISH"):
                pair.append(line[21:-1])

            if len(pair) == 2:
                self.strings[pair[0]] = pair[1]
                pair = []

        self.original = deepcopy(self.strings)


    def swap_with(self, incoming: dict[str, str]) -> Self:
        for k, v in incoming.items():
            if k in self.strings:
                self.strings[k] = v
        return self


    def changed(self) -> bool:
        return self.strings != self.original


    def export(self, path: pathlib.Path) -> Self:
        target = path / self.path.name
        print(f"Exporting to {target}")
        with target.open("w", encoding="utf-8") as str_io:
            str_io.writelines(StrFile.HEADER)
            for ref, val in self.strings.items():
                str_io.writelines([
                    f'REFERENCE           {ref}\n',
                    f'LANG_ENGLISH        "{val}"\n',
                    '\n'
                ])
            str_io.write("ENDMARKER")


def parse_pluto_strfile(strfile: pathlib.Path) -> dict[str, str]:
    raw = strfile.read_text("utf-8")
    contents = {}
    for line in raw.split("\n"):
        if " : " not in line:
            continue
        key, value = line.split(" : ", 1)
        contents[key] = value
    return contents


def load_pluto_strings(pluto_locstrings_path: str) -> dict[str, str]:
    locstrigs = pathlib.Path(pluto_locstrings_path)
    collection = {}
    for strfile in locstrigs.iterdir():
        collection |= parse_pluto_strfile(strfile)
    return collection


def generate_strfiles_from_using(collection: dict[str, str], template: pathlib.Path) -> None:
    files: list[StrFile] = [StrFile(tfile).swap_with(collection) for tfile in template.iterdir()]

    for str_file in files:
        if str_file.changed():
            str_file.export(pathlib.Path.cwd())


def main():
    locstrings_src, pluto_locstrings = sys.argv[1], sys.argv[2]
    pluto_strings = load_pluto_strings(pluto_locstrings)

    generate_strfiles_from_using(pluto_strings, pathlib.Path(locstrings_src))


if __name__ == "__main__":
    main()
