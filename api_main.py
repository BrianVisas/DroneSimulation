from server.api import create_app  # adjust import
import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=5001)
    args = parser.parse_args()

    app = create_app()
    app.run(host="0.0.0.0", port=args.port)

if __name__ == "__main__":
    main()
