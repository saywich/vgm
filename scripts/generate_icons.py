import pathlib
import struct
import zlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "frontend" / "public"
POLYGON = (
    (120, 130), (192, 130), (256, 328), (320, 130), (392, 130), (288, 390),
    (224, 390)
)
BACKGROUND = (23, 23, 23)
ACCENT = (138, 180, 255)


def inside_polygon(x, y):
    inside = False
    for index, point in enumerate(POLYGON):
        previous = POLYGON[index - 1]
        if (point[1] > y) == (previous[1] > y):
            continue

        boundary = (
            (previous[0] - point[0]) * (y - point[1]) /
            (previous[1] - point[1]) + point[0]
        )
        if x < boundary:
            inside = not inside

    return inside


def chunk(kind, data):
    checksum = zlib.crc32(kind + data) & 0xffffffff
    return struct.pack("!I",
                       len(data)) + kind + data + struct.pack("!I", checksum)


def render(size):
    rows = []
    for row_index in range(size):
        row = bytearray()
        for column_index in range(size):
            x = (column_index + 0.5) * 512 / size
            y = (row_index + 0.5) * 512 / size
            foreground = inside_polygon(x, y
                                       ) or (x - 377)**2 + (y - 369)**2 < 22**2
            row.extend(ACCENT if foreground else BACKGROUND)
        rows.append(b"\0" + row)

    header = struct.pack("!2I5B", size, size, 8, 2, 0, 0, 0)
    pixels = zlib.compress(b"".join(rows))
    return (
        b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", header) + chunk(b"IDAT", pixels) +
        chunk(b"IEND", b"")
    )


def main():
    for size in (192, 512):
        (PUBLIC / f"icon-{size}.png").write_bytes(render(size))


if __name__ == "__main__":
    main()
