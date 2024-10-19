import base64
import os
import textwrap
import time
from pprint import pprint

import dotenv
import replicate
import yaml
from julep import Julep
from PIL import Image, ImageDraw, ImageFont

from storygenerator import character
from storygenerator.character import client

dotenv.load_dotenv(override=True)


heros_journey = [
    """
    1. Ordinary World
    Purpose: Establish the protagonist's normal life before the adventure begins.
    Key elements: Showcase the hero's environment, daily life, and introduce key relationships and the hero’s primary problem or flaw.
    Take into account: Create contrast between this normal world and the adventure to come.
""",
    """
    2. Call to Adventure
    Purpose: Present an event or challenge that pulls the hero out of their comfort zone.
    Key elements: Something disrupts the hero’s ordinary world, often involving a threat or opportunity.
    Take into account: Make the stakes clear and ensure the audience sees why this call is significant.
""",
    """
    3. Refusal of the Call
    Purpose: Show the hero’s hesitation or outright refusal to engage in the adventure.
    Key elements: The hero doubts their ability, is afraid, or doesn’t believe the adventure is necessary.
    Take into account: Emphasize the internal conflict—why the hero feels unprepared or unwilling to accept the challenge.
""",
    """
    4. Meeting the Mentor
    Purpose: The hero encounters a mentor who provides guidance, training, or motivation.
    Key elements: The mentor can be a person or even an experience that offers the hero tools, advice, or insight for the journey.
    Take into account: The mentor's advice should hint at deeper themes or foreshadow key challenges ahead.
""",
    """
    5. Crossing the Threshold
    Purpose: The hero commits to the adventure and leaves the ordinary world behind.
    Key elements: This is a point of no return where the hero steps into the unknown.
    Take into account: Make this transition feel significant; it's the moment the journey truly begins.
""",
    """
    6. Tests, Allies, and Enemies
    Purpose: The hero encounters challenges and forms key relationships.
    Key elements: Introduce obstacles that test the hero's abilities and determination, while allies and enemies help or hinder their progress.
    Take into account: These trials should reveal character development, hint at the larger stakes, and introduce complex relationships.
""",
    """
    7. Approach to the Inmost Cave
    Purpose: The hero nears the central ordeal of the journey, facing fears or preparing for a major challenge.
    Key elements: This could be a physical journey or an emotional confrontation that requires the hero to dig deep.
    Take into account: Build tension and highlight what the hero stands to lose or gain.
""",
    """
    8. Ordeal
    Purpose: The hero faces their greatest challenge or confronts death (literal or metaphorical).
    Key elements: This is the story’s climax where the hero must use all their skills to survive or succeed.
    Take into account: This should feel like a make-or-break moment that tests the hero’s core, pushing them to their limits.
""",
    """
    9. Reward (Seizing the Sword)
    Purpose: After overcoming the ordeal, the hero gains a reward—an object, insight, or power.
    Key elements: The reward can be tangible or intangible, but it should symbolize the hero's growth.
    Take into account: The reward should feel earned, not just handed to the hero.
""",
    """
    10. The Road Back
    Purpose: The hero begins the journey home but faces additional challenges.
    Key elements: New dangers emerge, or the consequences of earlier actions catch up with the hero.
    Take into account: This can be a time for reflection, and it also keeps the tension high as the hero returns to the ordinary world.
""",
    """
    11. Resurrection
    Purpose: The hero faces a final test, often in the ordinary world, that forces them to use what they've learned.
    Key elements: This is often the ultimate showdown where the hero proves they have changed.
    Take into account: This moment should mirror the earlier Ordeal but demonstrate the hero’s transformation.
""",
    """
    12. Return with the Elixir
    Purpose: The hero returns to the ordinary world, changed and carrying the lessons or benefits of the adventure.
    Key elements: The “elixir” could be wisdom, healing, or a literal treasure that improves the hero’s life or the lives of others.
    Take into account: The ending should bring closure, showing how the journey has impacted both the hero and the world around them.


    Each time you generate the story, you'll get a description of a detailed description of the specific step and the story up to the point. Your job is to generate the single following beat in the story.
    """,
]



class Scene:
    def __init__(
            self,
            hero_desc: str | None = character.kent_desc,
            li_url: str="https://www.linkedin.com/in/kent-g-00ba0743/"
    ):
        if hero_desc is None:
            self.hero, pfp_desc = character.StoryCharacter.gen_character(li_url=li_url)
        else:
            self.hero, pfp_desc = (
                character.StoryCharacter(name="Kent", description=hero_desc),
                "The person has short, dark hair styled upwards, with a clean and well-defined haircut.\n")
        self.hero_pfp_description = pfp_desc

        self.storyteller = character.StoryCharacter(
            name="Storyteller",
            description=f"""
                You are a creative storyteller that crafts engaging stories.
                You will create a story following with the following hero:
                Hero name: {self.hero.name}
                Hero description: {self.hero.description}
            """,
        )

    def generate_scene(self, step: int, story_so_far=''):
        if story_so_far:
            self.storyteller.add_history(story_so_far)
        resp = self.storyteller.chat(
            f"""
            Your job is to generate a very short section for the next part of the story. 
            The next part of the story should have these attributes:
                {heros_journey[step]}
            Limit your output to one concise sentence. Be descriptive of the scene.
        """
        )
        return resp


def generate_story(hero_desc = "", li_url: str="https://www.linkedin.com/in/kent-g-00ba0743/"):
    story_scene = Scene(hero_desc=hero_desc, li_url=li_url)

    full_story = []
    for step in range(12):
        print("STORY PART", step)

        story_chunk = story_scene.generate_scene(step)
        pprint(story_chunk)
        # Graphics generation
        hero_pfp_description = story_scene.hero_pfp_description

        style = 'grayscale, detailed drawing, japanese manga\n'
        prompt = f"""{style}
        {story_chunk}
        """

        output = replicate.run(
            "black-forest-labs/flux-dev",
            input={
                "prompt": prompt,
                "go_fast": False,
                "guidance": 6,
                "megapixels": "1",
                "num_outputs": 1,
                "aspect_ratio": "1:1",
                "output_quality": 80,
                "num_inference_steps": 28,
            },
        )

        base64_string = str(output[0]).replace("data:application/octet-stream;base64,", "")
        image_data = base64.b64decode(base64_string)
        with open(f"{step}_image.png", "wb") as file:
            file.write(image_data)

        image = Image.open(f'{step}_image.png')
        draw = ImageDraw.Draw(image)

        caption = story_chunk
        font_size = 16
        try:
            font = ImageFont.truetype("arial.ttf", font_size)
        except IOError:
            font = ImageFont.load_default(size=font_size)


        split_caption = textwrap.fill(caption).split('\n')
        for i, cap in enumerate(split_caption):
            bbox = draw.textbbox((0, 0), cap, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            image_width, image_height = image.size
            x_position = (image_width - text_width) / 2
            y_position = image_height - text_height - len(cap) * 2
            draw.text(
                (x_position, y_position + i * 30),
                cap, font=font, fill="black", stroke_fill='white', stroke_width=4)

        image.save(f'new2/{step}_captioned_image.png')

        full_story.append(story_chunk)

    return full_story


if __name__ == "__main__":
    full_story = generate_story()

    pprint(full_story)
