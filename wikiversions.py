from windows import version_info_windows
import sys
import json

def main():
    res = version_info_windows()

    with open("windows.json", "w", encoding="utf-8") as f:
        json.dump(res, f, indent=4, ensure_ascii=False)

    sys.exit(0)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Erro: {e}", file=sys.stderr)
        sys.exit(1)
