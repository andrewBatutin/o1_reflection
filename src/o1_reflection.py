import os
from pathlib import Path
from openai import OpenAI

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

open_ai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

O1_REFLECTION_PROMPT = """
Your task if to carefully read the content below and give your best to answer next questions:

1. How O1 Models Works? Give the answer based both on openai documentation and additional research material.
2. Try to reverse engineer how O1 does the reasoning process.
3. Using provided research information on RL and LLMs try to explain the possible training process of O1 models.
4. Evaluate how much GPU resources are needed to train O1 models.
5. Explain the difference between train-time compute and test-time compute for O1 models.
6. Give the list of core ideas, mathematical concepts and algorithms that are used in O1 models.
7. Explain limitations at scaling O1 models. What prevents train time and test time compute to be scaled up? 

"""

def generate_openai_response(prompt, model="o1-preview"):
    response = open_ai_client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )
    return response.choices[0].message.content

def read_md_files():
    md_dir = Path("resources/md")
    md_contents = []
    
    for file in md_dir.glob("*.md"):
        with open(file, "r", encoding="utf-8") as f:
            md_contents.append(f.read())
    
    return md_contents

def run_analysis(documents_list):
    # Concatenate O1_REFLECTION_PROMPT and items from document list

    # drop 0,6,7 elements from the list


    combined_content = O1_REFLECTION_PROMPT + "\n\n" + "\n\n".join(documents_list)

    # Call generate_openai_response with the combined content
    response = generate_openai_response(combined_content, model="o1-preview")

    # Print or process the response as needed
    print("O1 Reflection Analysis:")
    print(response)
    # Write response to file
    output_dir = Path("resources/output")
    output_dir.mkdir(exist_ok=True)
    output_file = output_dir / "o1_reflection_analysis.txt"
    
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(response)
    
    print(f"Analysis written to {output_file}")


if __name__ == "__main__":
    # Read markdown files
    md_files_content = read_md_files()

    part_1 = md_files_content[:]
    #part_2 = md_files_content[11:]

    # Run the analysis
    run_analysis(part_1)
    #run_analysis(part_2)

