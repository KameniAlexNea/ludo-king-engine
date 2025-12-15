"""Example usage of the Ludo Database API."""

import base64
from io import BytesIO

import requests
from PIL import Image

# Base URL for the API
BASE_URL = "http://localhost:8000"


def display_image_from_base64(img_base64: str):
    """Helper to display an image from base64 string."""
    img_data = base64.b64decode(img_base64)
    img = Image.open(BytesIO(img_data))
    img.show()
    return img


def example_empty_board():
    """Example: Get an empty board image."""
    print("=== Getting empty board ===")
    response = requests.get(f"{BASE_URL}/api/board/empty")
    data = response.json()

    print(f"Image size: {data['width']}x{data['height']}")

    # Optionally display the image
    # display_image_from_base64(data['image_base64'])

    return data


def example_new_game():
    """Example: Create a new game and get initial state."""
    print("\n=== Creating new game ===")

    # Get initial board state
    response = requests.post(f"{BASE_URL}/api/board", json={})
    data = response.json()

    print(f"Initial FEN: {data['fen']}")
    print(f"Current player: {data['current_player']}")
    print(f"Sample legal moves: {data['legal_moves'][:5]}")

    return data


def example_apply_moves():
    """Example: Apply a sequence of moves to a game."""
    print("\n=== Applying moves ===")

    # Start with a new game
    response = requests.post(f"{BASE_URL}/api/board", json={})
    initial_state = response.json()
    current_fen = initial_state["fen"]

    # Simulate rolling a 6 and entering a token
    print("\nRoll: 6")
    print("Current player: red")

    move_response = requests.post(
        f"{BASE_URL}/api/move",
        json={"fen": current_fen, "dice": 6, "move": "r0e"},  # Red token 0 enter
    )
    move_data = move_response.json()

    print(f"Move valid: {move_data['valid']}")
    print(f"Message: {move_data['message']}")
    print(f"Next player: {move_data['next_player']}")
    print(f"FEN after: {move_data['fen_after'][:50]}...")

    return move_data


def example_board_image():
    """Example: Get a board image with pieces."""
    print("\n=== Getting board image ===")

    # Get initial state
    response = requests.post(f"{BASE_URL}/api/board", json={})
    state = response.json()

    # Get image for this state
    img_response = requests.post(
        f"{BASE_URL}/api/board/image", json={"fen": state["fen"]}
    )
    img_data = img_response.json()

    print(f"Image size: {img_data['width']}x{img_data['height']}")

    # Optionally display
    # display_image_from_base64(img_data['image_base64'])

    return img_data


def example_create_game_record():
    """Example: Create a game record in the database."""
    print("\n=== Creating game record ===")

    response = requests.post(
        f"{BASE_URL}/api/games",
        json={
            "players": {
                "red": "Alice",
                "green": "Bob",
                "yellow": "Charlie",
                "blue": "Diana",
            },
            "event": "Test Tournament",
            "site": "Local Testing",
        },
    )
    game = response.json()

    print(f"Game ID: {game['game_id']}")
    print(f"Event: {game['event']}")
    print(f"Players: {game['players']}")
    print(f"Starting FEN: {game['starting_fen'][:50]}...")

    return game


def example_query_games():
    """Example: Query games from the database."""
    print("\n=== Querying games ===")

    response = requests.post(
        f"{BASE_URL}/api/games/query", json={"limit": 5, "offset": 0}
    )
    results = response.json()

    print(f"Total games found: {results['total_count']}")
    for game in results["games"]:
        print(f"  - {game['game_id']}: {game['event']} ({game['date']})")

    return results


def example_database_stats():
    """Example: Get database statistics."""
    print("\n=== Database Statistics ===")

    response = requests.get(f"{BASE_URL}/api/stats")
    stats = response.json()

    print(f"Total games: {stats['total_games']}")
    print(f"Total positions: {stats['total_positions']}")
    print(f"Total moves: {stats['total_moves']}")

    return stats


def main():
    """Run all examples."""
    print("Ludo Database API Examples")
    print("=" * 50)
    print(f"API URL: {BASE_URL}")
    print("=" * 50)

    try:
        # Basic board operations
        example_empty_board()
        example_new_game()
        example_apply_moves()
        example_board_image()

        # Database operations
        example_create_game_record()
        example_query_games()
        example_database_stats()

        print("\n" + "=" * 50)
        print("✓ All examples completed successfully!")
        print("=" * 50)

    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Could not connect to API server.")
        print(f"Make sure the server is running at {BASE_URL}")
        print("Run: python -m ludo_api.app")
    except Exception as e:
        print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    main()
