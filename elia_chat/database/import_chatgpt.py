import json
from datetime import datetime
from pathlib import Path

from elia_chat.database.database import get_session
from elia_chat.database.models import MessageDao, ChatDao


async def import_chatgpt_data(file: Path) -> None:
    # Load the JSON data
    with open(file, "r") as f:
        data = json.load(f)

    async with get_session() as session:
        # Iterate over each chat in the data
        for chat_data in data:
            # Create a new ChatDao instance and add it to the session
            chat = ChatDao(
                model=None, started_at=datetime.fromtimestamp(chat_data["create_time"])
            )
            session.add(chat)
            await session.commit()  # Make sure to commit so that chat.id is assigned

            for _message_id, message_data in chat_data["mapping"].items():
                message_info = message_data.get("message")
                if message_info:
                    metadata = message_info.get("metadata", {})
                    if metadata:
                        model = metadata.get("model_slug")
                        if model is not None:
                            chat.model = model
                            session.add(chat)
                            await session.commit()

                    message = MessageDao(
                        chat_id=chat.id,
                        role=message_info["author"]["role"],
                        content=message_info["content"]["parts"][0],
                        timestamp=datetime.fromtimestamp(message_info["create_time"]),
                        status=message_info.get("status"),
                        end_turn=message_info.get("end_turn"),
                        weight=message_info.get("weight"),
                        meta=metadata,
                        recipient=message_info.get("recipient"),
                    )
                    session.add(message)

            await session.commit()


if __name__ == "__main__":
    path = Path("resources/conversations.json")
    import asyncio

    asyncio.run(import_chatgpt_data(path))
