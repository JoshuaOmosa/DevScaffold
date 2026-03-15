import os
import sys

def create_project(name):
    # Defining a professional, enterprise-ready structure
    structure = [
        f"{name}/src/Models",
        f"{name}/src/Repositories",
        f"{name}/config",
        f"{name}/public",
        f"{name}/tests"
    ]

    print(f"--- 🛠️ Initializing Project Architecture: {name} ---")
    
    try:
        # 1. Create folders
        for folder in structure:
            os.makedirs(folder, exist_ok=True)
            print(f"Created directory: {folder}")

        # 2. Seed essential files
        # This automatically creates a basic README and .gitignore for the NEW project
        files = {
            f"{name}/README.md": f"# {name}\n\nProject initialized via DevScaffold automation.",
            f"{name}/.gitignore": "__pycache__/\n.env\n*.log\nvendor/",
            f"{name}/config/config.php": "<?php\n// Configuration settings",
        }

        for path, content in files.items():
            with open(path, "w") as f:
                f.write(content)
            print(f"Seeded file: {path}")

        print(f"\n✅ Success: Professional structure for '{name}' is ready.")
        
    except Exception as e:
        print(f"❌ Critical Error during scaffolding: {e}")

if __name__ == "__main__":
    # Check if a project name was provided in the command line
    if len(sys.argv) < 2:
        print("Usage: python src/dev_scaffold.py <ProjectName>")
    else:
        create_project(sys.argv[1])