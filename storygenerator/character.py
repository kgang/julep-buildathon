import dotenv
import os

from julep import Client

from storygenerator import linkedin_scraper


dotenv.load_dotenv(override=True)
client = Client(api_key=os.environ['JULEP_API_KEY'])


class StoryCharacter:
    @classmethod
    def gen_character(cls, li_url: str):
        """
        profile:
          LinkedIn profile or basic description
        """
        char_dict = linkedin_scraper.url_to_profile(li_url)
        return StoryCharacter(
            name=char_dict['name'],
            description=f"""
                Your name is {char_dict['name']}
                Some of your personality traits are {",".join(char_dict['traits'])}
                This is your background story:
                  {char_dict['background']}
                Your potential as a hero is {char_dict['potential']}
            """
        )

    def __init__(self, description: str, name: str = "John"):
        from storygenerator import main

        self.name = name
        self.description = description
        self._user = client.users.create(
            name="Storyteller",
            about="You are a creative storyteller that crafts engaging stories.",
        )
        self._julep_agent = None
        self._session = None
        self._history = []  # Add events to its history to be prepended to its messages
        self.add_history(f"""
                    Your name is {self.name}.
                    This is a description of you: {self.description}
                """)

    @property
    def julep_agent(self):
        if self._julep_agent is None:
            self._julep_agent = client.agents.create(
                name=self.name,
                model="claude-3.5-sonnet",
                # about=self.description
                about=f"""
                    Your name is {self.name}.
                    This is a description of you: {self.description}
                """,
            )
        return self._julep_agent

    @property
    def session(self):
        if self._session is None:
            self._session = client.sessions.create(
                agent=self.julep_agent.id,
                user=self._user.id,
            )
        return self._session

    def add_history(self, message, role="user"):
        self._history.append({
            "role": role,
            "content": message
        })

    def chat(self, message: str, situation: str | None = None):
        """
        situation:
          What's the context/environment/system prompt for this interaction
        """
        if situation is not None:
            self.add_history(situation)

        message = {
            "role": "user",
            "content": message,
        }
        messages = [message]
        if self._history:
            # Prepend history to list of messages
            messages = self._history + messages
            # Reset history
            self._history = []
        response = client.sessions.chat(
            session_id=self.session.id,
            messages=messages,
        )
        return response.choices[0].message.content