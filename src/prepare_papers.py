from pathlib import Path

from llama_index.core import SimpleDirectoryReader
from llama_index.readers.file import (
    HTMLTagReader,
    PyMuPDFReader,
)

# Define paths
raw_dir = Path("resources/raw")
md_dir = Path("resources/md")

# Ensure the markdown directory exists
md_dir.mkdir(parents=True, exist_ok=True)


# Function to convert and save as markdown
def convert_to_markdown():

    parser = PyMuPDFReader()
    file_extractor = {".pdf": parser}
    documents = SimpleDirectoryReader(
        raw_dir, file_extractor=file_extractor
    ).load_data()

    parser = HTMLTagReader()
    file_extractor = {".html": parser}
    documents = SimpleDirectoryReader(
        raw_dir, file_extractor=file_extractor
    ).load_data()


    # Convert to markdown and save
    for document in documents:

        # Get the original filename and change extension to .md
        original_filename = Path(document.metadata["file_name"]).stem
        md_filename = f"{original_filename}.md"
        md_dir_full = md_dir / md_filename

        # Extract the content from the document
        markdown_content = document.text

        # If the file already exists, append to it; otherwise, create a new file
        mode = 'a' if md_dir_full.exists() else 'w'
        with open(md_dir_full, mode, encoding='utf-8') as f:
            f.write(markdown_content + '\n\n')  # Add newlines for separation



if __name__ == "__main__":
    # Process all files in the raw directory
    convert_to_markdown()

    print("Conversion complete.")


