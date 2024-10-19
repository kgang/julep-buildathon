import os

import dotenv
from julep import Client

from storygenerator import linkedin_scraper

dotenv.load_dotenv(override=True)
client = Client(api_key=os.environ['JULEP_API_KEY'])

kent_desc = "'\n                Your name is Kent G.\n                Some of your personality traits are Visionary,Resilient,Innovative,Mentor\n                This is your background story:\n                  Hailing from the vibrant borough of Queens, New York, Kent G. stands at the precipice of innovation, where technology meets creativity. As the Founder and CEO of Abstract Operators, Kent is poised to revolutionize the way we interact with artificial intelligence through open-source orchestration and advanced Kubernetes solutions. With a foundation built on rigorous academic training and a diverse professional journey, Kent embodies the spirit of a true pioneer.\n                Your potential as a hero is With a rich background in engineering physics and hands-on experience in financial engineering, Kent possesses a unique ability to navigate complex systems and extract actionable insights. Their journey has been marked by a relentless pursuit of knowledge, mentorship of others, and a passion for leveraging technology to solve real-world problems. As they embark on this next chapter, challenges loom on the horizon, from navigating the intricacies of the evolving AI landscape to building a robust venture ecosystem. Yet, with unwavering determination and a clear vision, Kent is destined to inspire and lead the charge into a future shaped by ingenuity and collaboration.\n            '"


class StoryCharacter:
    @classmethod
    def gen_character(cls, li_url: str):
        """
        profile:
          LinkedIn profile or basic description
        """
        char_dict, pfp_description = linkedin_scraper.url_to_profile(li_url)
        return (
            StoryCharacter(
                name=char_dict['name'],
                description=f"""
                Your name is {char_dict['name']}
                Some of your personality traits are {",".join(char_dict['traits'])}
                This is your background story:
                  {char_dict['background']}
                Your potential as a hero is {char_dict['potential']}
            """,
            ),
            pfp_description,
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
        self.add_history(
            f"""
                    Your name is {self.name}.
                    This is a description of you: {self.description}
                """
        )

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
        self._history.append({"role": role, "content": message})

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
