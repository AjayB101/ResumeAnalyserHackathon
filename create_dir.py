import os

structure = {
    "frontend": [],
    "backend/agents": [
        "resume_analyzer.py",
        "behavioral_retriever.py",
        "mock_evaluator.py",
        "outcome_predictor.py",
        "gap_fixer.py"
    ],
    "backend": [
        "orchestrator.py",
        "api.py"
    ],
    "backend/prompts": [],
    "backend/database": [],
    "backend/tests": [],
    ".": [
        "requirements.txt",
        ".env"
    ]
}

def create_structure(structure):
    for folder, files in structure.items():
        folder_path = os.path.abspath(folder) if folder != "." else os.getcwd()
        os.makedirs(folder_path, exist_ok=True)

        for file in files:
            file_path = os.path.join(folder_path, file)
            if not os.path.exists(file_path):
                with open(file_path, "w") as f:
                    if file == ".env":
                        f.write("# Add your environment variables here\n")
                    elif file.endswith(".py"):
                        f.write(f"# {file.replace('.py', '').replace('_', ' ').title()} module\n")
                    else:
                        f.write("")

if __name__ == "__main__":
    create_structure(structure)
    print("✅ Updated project structure created successfully.")
