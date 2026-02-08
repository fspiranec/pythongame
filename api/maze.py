import json
import random

# Vercel Python runtime expects a handler(request) function.
def handler(request):
    # Maze size (odd numbers work best). You can change these defaults.
    w = int(request.get("query", {}).get("w", 31))
    h = int(request.get("query", {}).get("h", 21))
    seed = request.get("query", {}).get("seed")

    if seed is not None:
        random.seed(seed)

    # Force odd sizes and minimums
    w = max(11, w | 1)
    h = max(11, h | 1)

    maze = generate_maze(w, h)

    return {
        "statusCode": 200,
        "headers": {
            "content-type": "application/json",
            "cache-control": "no-store",
            "access-control-allow-origin": "*",
        },
        "body": json.dumps({
            "w": w,
            "h": h,
            "grid": maze,  # 1 = wall, 0 = floor
            "start": [1, 1],
            "goal": [w - 2, h - 2],
        }),
    }


def generate_maze(w, h):
    """
    Perfect maze via randomized DFS "carving" on a grid:
    - Start with all walls (1)
    - Carve passages (0) in steps of 2
    """
    grid = [[1 for _ in range(w)] for _ in range(h)]

    def carve(x, y):
        grid[y][x] = 0
        dirs = [(2, 0), (-2, 0), (0, 2), (0, -2)]
        random.shuffle(dirs)
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if 1 <= nx < w - 1 and 1 <= ny < h - 1 and grid[ny][nx] == 1:
                # knock down wall between
                grid[y + dy // 2][x + dx // 2] = 0
                carve(nx, ny)

    carve(1, 1)

    # Ensure goal is open
    grid[h - 2][w - 2] = 0
    return grid
