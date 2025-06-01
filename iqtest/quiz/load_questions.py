import json
import os
import re
from django.conf import settings
from quiz.models import Question, OptionImage

def extract_image_path(text):
    """Extract image path from markdown syntax like ![](path/to/image.png)."""
    match = re.search(r'!\[\]\((.*?)\)', text)
    return match.group(1) if match else None

def load_questions(json_file, answer_file, image_base_dir):
    # Extract dataset name from json_file (e.g., 'T1-105-public' from 'data/T1-105-public.json')
    dataset_name = os.path.basename(json_file).split('.')[0]

    # Load JSON files
    with open(json_file, 'r') as f:
        questions = json.load(f)
    with open(answer_file, 'r') as f:
        answers = json.load(f)

    for q in questions:
        original_id = str(q['id'])  # Get the original ID from JSON
        source_id = f"{dataset_name}_{original_id}"  # Create unique source_id, e.g., 'T1-105-public_0'

        # Check for duplicates using source_id
        if Question.objects.filter(source_id=source_id).exists():
            print(f"Skipping duplicate question with source_id {source_id}")
            continue

        stem = q['stem']
        raw_options = q['options']
        category = q['category']
        answer_data = answers[original_id]
        answer = answer_data['answer'][0] if len(answer_data['answer']) == 1 else answer_data['answer']
        hint = answer_data.get('hint', "")  # Extract hint, default to "" if not present

        # Normalize options to a dictionary
        if isinstance(raw_options, list):
            raw_options = {str(i): option for i, option in enumerate(raw_options)}
        elif not isinstance(raw_options, dict):
            print(f"Warning: Unexpected options format for question {original_id}: {raw_options}")
            continue

        # Handle question (stem) image
        image_path = extract_image_path(stem)
        if image_path:
            stem = re.sub(r'!\[\]\(.*?\)', '', stem).strip()  # Remove image markdown from text
            image_name = os.path.basename(image_path)  # e.g., "1.png"
            full_image_path = os.path.join(image_base_dir, image_name)  # e.g., "data/T1-105-public/media/1.png"
            has_image = True
        else:
            full_image_path = None
            image_name = None
            has_image = False

        # Create question object with hint
        question = Question(
            source_id=source_id,
            text=stem,
            options={},  # Temporary, filled later
            correct_answer=str(answer),
            category=category,
            has_image=has_image,
            hint=hint,  # Add the hint here
        )
        question.save()

        # Upload question image if it exists
        if full_image_path and os.path.exists(full_image_path):
            with open(full_image_path, 'rb') as img_file:
                question.image.save(image_name, img_file, save=True)
        elif full_image_path:
            print(f"Warning: Question image not found at {full_image_path}")

        # Process options
        processed_options = {}
        for key, value in raw_options.items():
            option_image_path = extract_image_path(value)
            if option_image_path:  # Option is an image
                option_image_name = os.path.basename(option_image_path)  # e.g., "1A.png"
                full_option_image_path = os.path.join(image_base_dir, option_image_name)
                if os.path.exists(full_option_image_path):
                    option_image = OptionImage(question=question, key=key)
                    option_image.save()
                    with open(full_option_image_path, 'rb') as img_file:
                        option_image.image.save(option_image_name, img_file, save=True)
                    processed_options[key] = option_image_name
                else:
                    print(f"Warning: Option image not found at {full_option_image_path}")
                    processed_options[key] = option_image_name  # Fallback
            else:  # Option is text
                processed_options[key] = value

        # Update question with processed options
        question.options = processed_options
        question.save()

if __name__ == '__main__':
    load_questions(
        'data/logic-diagram-public.json',
        'data/logic-diagram-public.answer.json',
        'data/logic-diagram-public/media'
    )



