import ast
import io
import pathlib
import tokenize

ROOT = pathlib.Path(__file__).resolve().parents[1]
GENERATED = ROOT / "backend" / "vgm" / "generated"


def remove_annotations(source):
    lines = source.splitlines(keepends=True)
    starts = [0]
    for line in lines:
        starts.append(starts[-1] + len(line))

    changes = []
    for token in tokenize.generate_tokens(io.StringIO(source).readline):
        if token.type == tokenize.COMMENT:
            start = starts[token.start[0] - 1] + token.start[1]
            end = starts[token.end[0] - 1] + token.end[1]
            changes.append((start, end, ""))

    for node in ast.walk(ast.parse(source)):
        if not isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef)):
            continue
        if not node.body or not ast.get_docstring(node):
            continue

        statement = node.body[0]
        start = starts[statement.lineno - 1] + statement.col_offset
        end = starts[statement.end_lineno - 1] + statement.end_col_offset
        replacement = "pass" if len(node.body) == 1 else ""
        changes.append((start, end, replacement))

    for start, end, replacement in sorted(changes, reverse=True):
        source = source[:start] + replacement + source[end:]

    return source.lstrip()


def main():
    for path in GENERATED.glob("*_pb2*.py"):
        path.write_text(remove_annotations(path.read_text()))


if __name__ == "__main__":
    main()
