import dotenv
import os

from julep import Julep


dotenv.load_dotenv(override=True)
client = Julep(api_key=os.environ['JULEP_API_KEY'])

_npcs: dict[str, "StoryCharacter"] = {}
"""Map a npc's name to a character"""


class StoryCharacter:
    @classmethod
    def gen_character(cls, profile):
        """
        profile:
          LinkedIn profile or basic description
        """
        pass

    def __init__(self, description: str, age: int = 25, personality: str = "A normal person."):
        self.personality = personality
        self.age = age
        self.description = description

    def chat(context: str, character: str | None = None):
        """
        context:
          Tell the character what the context is on what's happening and prompt them to respond
          OR tell the character what they decided to say and have them add their personality
        
        character (optional):
          Who is the character responding to. Should be the unique name for the story
        """
        pass

    def interact_w_environment(env_description):
        pass

