from dataclasses import dataclass
from unittest.mock import patch

import litellm
import pytest

from elia_chat.app import Elia
from elia_chat.config import LaunchConfig
from elia_chat.screens.chat_screen import ChatScreen
from elia_chat.screens.home_screen import HomeScreen
from elia_chat.widgets.chatbox import Chatbox
from elia_chat.widgets.prompt_input import PromptInput


@dataclass
class Chunk:
    content: str

    @property
    def choices(self):
        return [self]

    @property
    def delta(self):
        return self


async def ac(*args, **kwargs):
    async def inner():
        for word in ["Hello ", "There ", "Everyone"]:
            yield Chunk(word)

    return inner()


@pytest.mark.asyncio
@patch.object(litellm, "acompletion", ac)
async def test_smoke():
    app = Elia(LaunchConfig())
    async with app.run_test() as pilot:
        await pilot.press(*"tell me a very short story")
        assert type(pilot.app.screen) == HomeScreen
        assert pilot.app.query_one(PromptInput).text == "tell me a very short story"

        await pilot.press("ctrl+j")

        assert type(pilot.app.screen) == ChatScreen
        [_, output] = pilot.app.query(Chatbox)
        assert output.markdown.markup == "Hello There Everyone"
