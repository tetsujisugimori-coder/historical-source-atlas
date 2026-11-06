"""Read-only CLI: never rebuild before inspecting existing outputs."""
from pathlib import Path
from integrity import verify
BASE = Path(__file__).resolve().parent

if __name__ == "__main__":
    count = verify(BASE/"eikyouki_records.json", BASE/"index.html", BASE/"eikyouki.db")
    print(f"PASS: {count} articles / 36 fields / JSON / HTML / read-only SQLite JOIN")
