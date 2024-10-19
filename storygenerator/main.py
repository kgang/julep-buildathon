

import dotenv
import os
import time
import yaml

from julep import Julep


dotenv.load_dotenv(override=True)
client = Julep(api_key=os.environ['JULEP_API_KEY'])

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
    about=f"""You are a creative storyteller that crafts engaging stories on a myriad of topics.

        {"\n".join(heros_journey)}
    """,
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
            ]
        }]

        task = client.tasks.create(
            agent_id=agent.id,
            main = main_story,
            name = "storyteller",
            description = "Creates a story."
        )

        return task
    


if __name__ == "__main__":
    sceneGenerator = Scene(step = 0)  
    task = sceneGenerator.generate_scene(story_so_far='')
    execution = client.executions.create(
        task_id=task.id,
    )

    # 🎉 Watch as the story and comic panels are generated
    while (result := client.executions.get(execution.id)).status not in ['succeeded', 'failed']:
        print(result.status, result.output)
        time.sleep(1)

    # 📦 Once the execution is finished, retrieve the results
    if result.status == "succeeded":
        print(result.output)
    else:
        raise Exception(result.error)




# {'description': 'Create a story based on an idea.',
#  'main': [{'prompt': [{'content': 'You are {{agent.name}}. {{agent.about}}',
#                        'role': 'system'},
#                       {'content': "Based on the idea '{{_.idea}}', generate a "
#                                   'list of 5 plot ideas. Go crazy and be as '
#                                   'creative as possible. Return your output as '
#                                   'a list of long strings inside ```yaml tags '
#                                   'at the end of your response.\n',
#                        'role': 'user'}],
#            'unwrap': True},
#           {'evaluate': {'plot_ideas': "load_yaml(_.split('```yaml')[1].split('```')[0].strip())"}},
#           {'prompt': [{'content': 'You are {{agent.name}}. {{agent.about}}',
#                        'role': 'system'},
#                       {'content': 'Here are some plot ideas for a story: {% '
#                                   'for idea in _.plot_ideas %} - {{idea}} {% '
#                                   'endfor %}\n'
#                                   'To develop the story, we need to research '
#                                   'for the plot ideas. What should we '
#                                   'research? Write down wikipedia search '
#                                   'queries for the plot ideas you think are '
#                                   'interesting. Return your output as a yaml '
#                                   'list inside ```yaml tags at the end of your '
#                                   'response.\n',
#                        'role': 'user'}],
#            'settings': {'model': 'gpt-4o-mini', 'temperature': 0.7},
#            'unwrap': True},
#           {'evaluate': {'research_queries': "load_yaml(_.split('```yaml')[1].split('```')[0].strip())"}},
#           {'foreach': {'do': {'arguments': {'query': '_'},
#                               'tool': 'research_wikipedia'},
#                        'in': '_.research_queries'}},
#           {'evaluate': {'wikipedia_results': 'NEWLINE.join([f"- '
#                                              '{doc.metadata.title}: '
#                                              '{doc.metadata.summary}" for item '
#                                              'in _ for doc in '
#                                              'item.documents])'}},
#           {'prompt': [{'content': 'You are {{agent.name}}. {{agent.about}}',
#                        'role': 'system'},
#                       {'content': "Before we write the story, let's think and "
#                                   'deliberate. Here are some plot ideas:\n'
#                                   '{% for idea in outputs[1].plot_ideas %}\n'
#                                   '- {{idea}}\n'
#                                   '{% endfor %}\n'
#                                   '\n'
#                                   'Here are the results from researching the '
#                                   'plot ideas on Wikipedia:\n'
#                                   '{{_.wikipedia_results}}\n'
#                                   '\n'
#                                   'Think about the plot ideas critically. '
#                                   'Combine the plot ideas with the results '
#                                   'from Wikipedia to create a detailed plot '
#                                   'for a story.\n'
#                                   'Write down all your notes and thoughts.\n'
#                                   'Then finally write the plot as a yaml '
#                                   'object inside ```yaml tags at the end of '
#                                   'your response. The yaml object should have '
#                                   'the following structure:\n'
#                                   '\n'
#                                   '```yaml\n'
#                                   'title: "<string>"\n'
#                                   'characters:\n'
#                                   '- name: "<string>"\n'
#                                   '  about: "<string>"\n'
#                                   'synopsis: "<string>"\n'
#                                   'scenes:\n'
#                                   '- title: "<string>"\n'
#                                   '  description: "<string>"\n'
#                                   '  characters:\n'
#                                   '  - name: "<string>"\n'
#                                   '    role: "<string>"\n'
#                                   '  plotlines:\n'
#                                   '  - "<string>"```\n'
#                                   '\n'
#                                   'Make sure the yaml is valid and the '
#                                   'characters and scenes are not empty. Also '
#                                   'take care of semicolons and other gotchas '
#                                   'of writing yaml.',
#                        'role': 'user'}],
#            'unwrap': True},
#           {'evaluate': {'plot': "load_yaml(_.split('```yaml')[1].split('```')[0].strip())"}}],
#  'name': 'Storyteller',
#  'tools': [{'integration': {'method': 'search', 'provider': 'wikipedia'},
#             'name': 'research_wikipedia'}]}