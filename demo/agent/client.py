"""Demo agent client — visits a merchant site via WebGate.

Usage:
  python client.py
  python client.py --domain localhost:8000  (custom domain)
  python client.py --intent "我想谈价格"   (custom intent)
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from sdk.python.webgate import discover, send, visit

def main():
    domain = "localhost:8000"
    intent = "你好，我想了解一下你们的价格"

    # Parse simple CLI args
    args = sys.argv[1:]
    i = 0
    while i < len(args):
        if args[i] == "--domain" and i + 1 < len(args):
            domain = args[i + 1]
            i += 2
        elif args[i] == "--intent" and i + 1 < len(args):
            intent = args[i + 1]
            i += 2
        elif args[i] == "--scheme" and i + 1 < len(args):
            i += 2  # skip for now
        else:
            i += 1

    # Step 1: Discover
    print(f"🔍 Discovering agent at {domain}...")
    try:
        manifest = discover(domain)
        print(f"   Found: endpoint={manifest['endpoint']}")
    except Exception as e:
        print(f"   Not found: {e}")
        print("   (No WebGate agent at this domain)")
        return

    # Step 2: Send message
    print(f"\n📨 Sending message: {intent}")
    response = send(
        manifest["endpoint"],
        {"from": "user-agent", "content": intent},
    )
    print(f"\n📩 Response from merchant agent:")
    print(f"   {response}")

if __name__ == "__main__":
    main()
