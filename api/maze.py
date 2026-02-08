import json
import random
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            parsed = urlparse(self.path)
            qs = parse_qs(parsed.query)

            w = int(qs.get("w", ["31"])[0])
            h = int(qs.get("h", ["21"])[0])
            seed = qs.get("seed", [None])[0]

            if seed is not None:
                random.seed(seed)

            # Force odd sizes and minimums
            w = max(11, w | 1)
            h = max(11, h | 1)

            grid = generate_maze(w, h)

            payload = {
                "w": w,
                "h": h,
                "grid": grid,          # 1 = wall, 0 = floor
                "start": [1, 1],
                "goal": [w - 2, h - 2],
            }

            body = json.dumps(payload).encode("utf-8")

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(body)

        except Exception as e:
            msg = json.dumps({"error": str(e)}).encode("utf-8")
            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(msg)


def generate_maze(w, h):
    # Perfect maze via randomized DFS carving
    grid = [[1 for _ in range(w)] for _ in range(h)]

    def carve(x, y):
        grid[y][x] = 0
        dirs = [(2, 0), (-2, 0), (0, 2), (0, -2)]
        random.shuffle(dirs)
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if 1 <= nx < w - 1 and 1 <= ny < h - 1 and grid[ny][nx] == 1:
                grid[y + dy // 2][x + dx // 2] = 0
                carve(nx, ny)

    carve(1, 1)
    grid[h - 2][w - 2] = 0
    return grid
