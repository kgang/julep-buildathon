

import dotenv
import os
import time
import yaml

from julep import Julep
from pprint import pprint

from storygenerator.character import client


dotenv.load_dotenv(override=True)


heros_journey = ["""
    1. Ordinary World
    Purpose: Establish the protagonist's normal life before the adventure begins.
    Key elements: Showcase the hero's environment, daily life, and introduce key relationships and the hero’s primary problem or flaw.
    Take into account: Create contrast between this normal world and the adventure to come.
""","""
    2. Call to Adventure
    Purpose: Present an event or challenge that pulls the hero out of their comfort zone.
    Key elements: Something disrupts the hero’s ordinary world, often involving a threat or opportunity.
    Take into account: Make the stakes clear and ensure the audience sees why this call is significant.
""","""
    3. Refusal of the Call
    Purpose: Show the hero’s hesitation or outright refusal to engage in the adventure.
    Key elements: The hero doubts their ability, is afraid, or doesn’t believe the adventure is necessary.
    Take into account: Emphasize the internal conflict—why the hero feels unprepared or unwilling to accept the challenge.
""","""
    4. Meeting the Mentor
    Purpose: The hero encounters a mentor who provides guidance, training, or motivation.
    Key elements: The mentor can be a person or even an experience that offers the hero tools, advice, or insight for the journey.
    Take into account: The mentor's advice should hint at deeper themes or foreshadow key challenges ahead.
""","""
    5. Crossing the Threshold
    Purpose: The hero commits to the adventure and leaves the ordinary world behind.
    Key elements: This is a point of no return where the hero steps into the unknown.
    Take into account: Make this transition feel significant; it's the moment the journey truly begins.
""","""
    6. Tests, Allies, and Enemies
    Purpose: The hero encounters challenges and forms key relationships.
    Key elements: Introduce obstacles that test the hero's abilities and determination, while allies and enemies help or hinder their progress.
    Take into account: These trials should reveal character development, hint at the larger stakes, and introduce complex relationships.
""","""
    7. Approach to the Inmost Cave
    Purpose: The hero nears the central ordeal of the journey, facing fears or preparing for a major challenge.
    Key elements: This could be a physical journey or an emotional confrontation that requires the hero to dig deep.
    Take into account: Build tension and highlight what the hero stands to lose or gain.
""","""
    8. Ordeal
    Purpose: The hero faces their greatest challenge or confronts death (literal or metaphorical).
    Key elements: This is the story’s climax where the hero must use all their skills to survive or succeed.
    Take into account: This should feel like a make-or-break moment that tests the hero’s core, pushing them to their limits.
""","""
    9. Reward (Seizing the Sword)
    Purpose: After overcoming the ordeal, the hero gains a reward—an object, insight, or power.
    Key elements: The reward can be tangible or intangible, but it should symbolize the hero's growth.
    Take into account: The reward should feel earned, not just handed to the hero.
""","""
    10. The Road Back
    Purpose: The hero begins the journey home but faces additional challenges.
    Key elements: New dangers emerge, or the consequences of earlier actions catch up with the hero.
    Take into account: This can be a time for reflection, and it also keeps the tension high as the hero returns to the ordinary world.
""","""
    11. Resurrection
    Purpose: The hero faces a final test, often in the ordinary world, that forces them to use what they've learned.
    Key elements: This is often the ultimate showdown where the hero proves they have changed.
    Take into account: This moment should mirror the earlier Ordeal but demonstrate the hero’s transformation.
""","""
    12. Return with the Elixir
    Purpose: The hero returns to the ordinary world, changed and carrying the lessons or benefits of the adventure.
    Key elements: The “elixir” could be wisdom, healing, or a literal treasure that improves the hero’s life or the lives of others.
    Take into account: The ending should bring closure, showing how the journey has impacted both the hero and the world around them.


    Each time you generate the story, you'll get a description of a detailed description of the specific step and the story up to the point. Your job is to generate the single following beat in the story.
    """]


agent = client.agents.create(
    name="Storytelling Agent",
    model="claude-3.5-sonnet",
    about=f"""You are a creative storyteller that crafts engaging stories on a myriad of topics.""",
)


# print('agent', agent.name, agent.about)
class Scene:
    def __init__(self, step: int):
        self.step = step

    def generate_scene(self, story_so_far = None): 
        main_story = [{
            'prompt': [
                {
                    'content': "You are a {{agent.name}}. {{agent.about}}",
                    'role': "system"
                },
                {
                    'content': f"""Your job is to generate a scene for the entire story. 
                        Here's the story so far
                        {story_so_far } 

                        Follow the story and generate a scene with the following structure.
                        {heros_journey[self.step]}
                        """,
                    'role': 'user'
                }
            ],
        }]

        task = client.tasks.create(
            agent_id=agent.id,
            main = main_story,
            name = f"storyteller step {self.step}",
            description = "Creates a scene.",
        )

        return task
    

def generate_story():

    story_so_far = ''
    for step in range(12):
        print("STORY PART", step)
        sceneGenerator = Scene(step)  
        task = sceneGenerator.generate_scene(story_so_far=story_so_far)
        execution = client.executions.create(
            task_id=task.id,
            input={}
        )

        print('creating execution id ', execution.id)
        print('task id ', task.id)

        # 🎉 Watch as the story and comic panels are generated
        while (result := client.executions.get(execution.id)).status not in ['succeeded', 'failed']:
            print(result.status, result.output)
            time.sleep(1)

        # 📦 Once the execution is finished, retrieve the results
        if result.status == "succeeded":
            # print("FULL OUTPUT", result.output)

            story = result.output.get('choices')[0]['message']['content']
            print(f"STORY STEP: {step}\n", story)

            story_so_far += f"""
                {story}
            """
            
        else:
            raise Exception(result.error)

    return story_so_far


if __name__ == "__main__":
    full_story = generate_story()

    print('\n\n FULL STORY \n\n', full_story)
