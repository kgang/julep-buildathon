import os
import time

import requests
import yaml
from dotenv import load_dotenv
from julep import Julep
from openai import OpenAI

load_dotenv(override=True)
julep_api_key = os.getenv('JULEP_OPENAI_API_KEY')
client = Julep(api_key=julep_api_key)


def experiences_to_str(experiences: list[dict]) -> str:
    """
    Returns, in reverse order, work experience stringified.
    """
    res = []
    for experience in reversed(experiences):
        company = experience.get('company')
        title = experience.get('title')
        starts_at = experience.get('starts_at')
        ends_at = experience.get('ends_at', 'current')
        description = experience.get('description')

        experience_str = (
            f"Company: {company}\n"
            f"Title: {title}\n"
            f"Start Date: {starts_at}\n"
            f"End Date: {ends_at}\n"
            f"Description: {description}\n"
        )
        res.append(experience_str)

    return '\n'.join(res)


def education_to_str(education: list[dict]) -> str:
    res = []
    for edu in reversed(education):
        field_of_study = edu.get('field_of_study')
        degree_name = edu.get('degree_name')
        school = edu.get('school')
        description = edu.get('description')
        grade = edu.get('grade')
        activities = edu.get('activities_and_societies')
        starts_at = edu.get('starts_at')
        ends_at = edu.get('ends_at')

        edu_string = (
            f"School: {school}\n"
            f"Degree: {degree_name} in {field_of_study}\n"
            f"Grade: {grade}\n"
            f"Activities: {activities}\n"
            f"Description: {description}\n"
            f"Start Date: {starts_at}\n"
            f"End Date: {ends_at}\n"
        )
        res.append(edu_string)

    return '\n'.join(res)


def person_to_str(person: dict):
    # Basic Information
    first_name: str | None = person.get('first_name')
    last_name: str | None = person.get('last_name')
    gender: str | None = person.get('gender')
    birth_date: str | None = person.get('birth_date')

    # Location Information
    city: str | None = person.get('city')
    state: str | None = person.get('state')
    country: str | None = person.get('country_full_name')

    # Profile Headline and Summary
    headline: str | None = person.get('headline')  # tagline
    summary: str | None = person.get('summary')  # longer headline

    # Professional Information
    industry: str | None = person.get('industry')
    occupation: str | None = person.get('occupation')

    # Experiences and Education
    experiences: list | None = person.get('experiences')
    experiences_str: str = experiences_to_str(experiences) if experiences else ""
    education: list | None = person.get('education')
    education_str: str = education_to_str(education) if education else ""

    pfp_url: str = person.get('profile_pic_url')
    pfp_description: str = pfp_to_description(pfp_url)

    return (
        f"Name: {first_name or ''} {last_name or ''}\n"
        f"Gender: {gender or 'N/A'}\n"
        f"Birth Date: {birth_date or 'N/A'}\n"
        f"Location: {city or ''}, {state or ''}, {country or ''}\n"
        f"Headline: {headline or 'N/A'}\n"
        f"Summary: {summary or 'N/A'}\n"
        f"Industry: {industry or 'N/A'}\n"
        f"Occupation: {occupation or 'N/A'}\n"
        f"Experiences:\n{experiences_str or 'No experience listed'}\n"
        f"Education:\n{education_str or 'No education listed'}"
    ), pfp_description


def pfp_to_description(pfp_url: str) -> str:
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    prompt = """Provide a detailed description of the person's physical appearance in three sentences. Focus on permanent features such as facial structure, skin tone, hair type, and body shape. Do not include details about their pose, actions, clothing, accessories, or any temporary features like expressions or makeup.
"""
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt,
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": pfp_url,
                        },
                    },
                ],
            }
        ],
        max_tokens=300,
    )

    return response.choices[0].message.content


def url_to_profile(li_url: str):

    headers = {'Authorization': f"Bearer {os.getenv('PROXYCURL_API_KEY')}"}
    url = "https://nubela.co/proxycurl/api/v2/linkedin"
    # e.g. https://www.linkedin.com/in/kent-g-00ba0743/

    params = {'linkedin_profile_url': li_url}
    person: dict = requests.get(url, headers=headers, params=params).json()
    person_str, pfp_description = person_to_str(person)

    profile_creator = client.agents.create(
        name='Hero Story Writer',
        model='gpt-4o-mini',
        about='You are a professional writer who crafts engaging profiles that introduce individuals at the start of their hero’s journey. Highlight their potential, core traits, and hint at upcoming challenges. Your tone is inspirational, grand, yet relatable, connecting the reader to the hero’s beginnings and setting the stage for their transformation.',
    )

    hero_writer_yaml = yaml.safe_load(
        """name: Hero Profile Writer
description: Creates a hero's profile based on a real person's LinkedIn data, focusing on the start of their journey.

main:
    - prompt:
          - role: system
            content: You are {{agent.name}}. {{agent.about}}
          - role: user
            content: >
                Based on the following annotated LinkedIn profile, create a hero's profile. The profile should focus on the start of the person's hero journey, highlighting their potential, core traits, and hinting at upcoming challenges. Don't change the profile's name.

                IMPORTANT: Create a *profile*, not a *story*. Profiles revolve around character traits. 

                '{{_.person_linkedin_str}}'

                Write the hero profile in a structured, readable format. Be inspirational and grand yet relatable.
                Return the profile in this format:

                ```yaml
                name: "<original_first_name> <original_last_name>"
                background: "<string>"
                traits: 
                    - "<trait>"
                    - "<trait>"
                potential: "<description of the person's potential>"
                ```

                Return your response in the format with valid YAML syntax.
            unwrap: true
            settings:
            model: gpt-4o-mini
            temperature: 0
"""
    )
    task = client.tasks.create(agent_id=profile_creator.id, **hero_writer_yaml)

    execution = client.executions.create(task_id=task.id, input={'person_linkedin_str': person_str})
    while (result := client.executions.get(execution.id)).status not in ['succeeded', 'failed']:
        time.sleep(1)

    if result.status == "succeeded":
        res = result.output
    else:
        raise Exception(result.error)
    choices = res.get('choices')
    message = choices[0]['message']['content']
    return yaml.safe_load('\n'.join(message.split('\n')[1:-1]))
