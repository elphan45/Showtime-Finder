import subprocess
import re
import os
import logging
import argparse
from typing import List, Tuple
from pathlib import Path
import torch
from transformers import pipeline, AutoModelForCausalLM, AutoTokenizer

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class VersionManager:
    """Manages reading and updating version information in a file using an absolute path."""
    def __init__(self, version_file: str = None):
        # Determine the project root (two directories above this file)
        project_root = Path(__file__).resolve().parent.parent
        if version_file is None:
            # Default absolute path to the version file
            self.version_file = project_root / 'src' / 'movie_scraper.py'
        else:
            version_path = Path(version_file)
            if not version_path.is_absolute():
                # Assume the provided path is relative to the project root
                self.version_file = project_root / version_file
            else:
                self.version_file = version_path
        self._validate_version_file()

    def _validate_version_file(self) -> None:
        if not self.version_file.exists():
            raise FileNotFoundError(f"Version file not found: {self.version_file}")

    def get_current_version(self) -> str:
        version_pattern = re.compile(r"^__version__\s*=\s*['\"]([^'\"]+)['\"]", re.M)
        with open(self.version_file, 'r') as f:
            content = f.read()
        match = version_pattern.search(content)
        if not match:
            raise ValueError("No valid __version__ found in file")
        return match.group(1)
    
    def update_version(self, new_version: str) -> None:
        version_pattern = re.compile(r"^(__version__\s*=\s*['\"]).*?(['\"])", re.M)
        with open(self.version_file, 'r+') as f:
            content = f.read()
            new_content = version_pattern.sub(rf"\1{new_version}\2", content)
            f.seek(0)
            f.write(new_content)
            f.truncate()

class GitManager:
    """Interacts with Git to obtain changed files and commit history."""
    @staticmethod
    def get_changed_files() -> List[str]:
        try:
            result = subprocess.run(
                ['git', 'diff', '--name-only', 'HEAD'],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            return result.stdout.decode().splitlines()
        except subprocess.CalledProcessError as e:
            logger.error(f"Error getting changed files: {e.stderr.decode()}")
            raise

    @staticmethod
    def get_commit_history(limit: int = 5) -> List[str]:
        try:
            result = subprocess.run(
                ['git', 'log', f'-{limit}', '--pretty=format:%s'],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            return result.stdout.decode().splitlines()
        except subprocess.CalledProcessError as e:
            logger.error(f"Error getting commit history: {e.stderr.decode()}")
            raise

class VersionIncrementor:
    """Determines how to increment the version based on commit messages and changed files."""
    @staticmethod
    def increment_version(version: str, level: str) -> str:
        try:
            parts = list(map(int, version.split('.')))
            if len(parts) != 3:
                raise ValueError("Invalid version format")
        except ValueError:
            raise ValueError(f"Invalid version string: {version}")

        if level == 'patch':
            parts[2] += 1
        elif level == 'minor':
            parts[1] += 1
            parts[2] = 0
        elif level == 'major':
            parts[0] += 1
            parts[1] = 0
            parts[2] = 0
        else:
            raise ValueError(f"Invalid version level: {level}")

        return '.'.join(map(str, parts))

    @classmethod
    def determine_change_level(cls, changed_files: List[str], commit_messages: List[str]) -> str:
        # Prefer commit-based detection using conventional commit indicators
        for msg in commit_messages:
            if msg.startswith('feat(') or msg.startswith('feat:'):
                return 'minor'
            if msg.startswith('BREAKING CHANGE:') or msg.startswith('!'):
                return 'major'
        # Fallback based on file type changes
        if any(f.endswith('.py') for f in changed_files):
            return 'minor'
        return 'patch'

class ReleaseNotesGenerator:
    """Generates release notes using a language model."""
    def __init__(self, model_name: str = 'EleutherAI/gpt-neo-1.3B'):
        self.model_name = model_name
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForCausalLM.from_pretrained(model_name)
        # Set device: use CUDA if available; otherwise CPU.
        self.device = 0 if torch.cuda.is_available() else -1
        logger.info(f"Device set to use {'cuda:0' if self.device == 0 else 'cpu'}")
        self.generator = pipeline(
            'text-generation',
            model=self.model,
            tokenizer=self.tokenizer,
            device=self.device
        )

    def generate_summary(self, commit_messages: List[str]) -> Tuple[str, str]:
        commit_str = "\n".join(commit_messages)
        prompt = (
            "Generate release notes with a title and description based on these commits:\n"
            f"{commit_str}\n\n"
            "Format:\nTitle: [title here]\nDescription: [description here]"
        )
        try:
            response = self.generator(
                prompt,
                max_length=200,
                num_return_sequences=1,
                temperature=0.7,
                do_sample=True
            )
            summary = response[0]['generated_text'].strip()
            logger.debug(f"Raw model output:\n{summary}")
        except RuntimeError as e:
            # Check if it's a CUDA OOM error
            if "CUDA out of memory" in str(e):
                logger.warning("CUDA out of memory encountered. Switching to CPU for generation.")
                torch.cuda.empty_cache()
                # Reinitialize the generator to use CPU
                self.generator = pipeline(
                    'text-generation',
                    model=self.model,
                    tokenizer=self.tokenizer,
                    device=-1
                )
                response = self.generator(
                    prompt,
                    max_length=200,
                    num_return_sequences=1,
                    temperature=0.7,
                    do_sample=True
                )
                summary = response[0]['generated_text'].strip()
            else:
                logger.error(f"Failed to generate release notes: {str(e)}")
                summary = "Title: New Release\nDescription: Various improvements and bug fixes"

        # Attempt to extract title and description; fallback if extraction fails
        title_match = re.search(r'Title:\s*(.+)', summary)
        desc_match = re.search(r'Description:\s*(.+)', summary, re.DOTALL)
        
        title = title_match.group(1).strip() if title_match else "New Release"
        description = desc_match.group(1).strip() if desc_match else "Various improvements and bug fixes"
        
        return title, description

def append_to_changelog(new_version: str, title: str, description: str, changelog_file: str = 'CHANGELOG.md') -> None:
    """
    Appends the new release information to the changelog file.
    """
    changelog_path = Path(changelog_file)
    entry = f"\n## Version {new_version}\n**{title}**\n\n{description}\n"
    try:
        if changelog_path.exists():
            with open(changelog_path, 'a') as f:
                f.write(entry)
        else:
            with open(changelog_path, 'w') as f:
                f.write(f"# Changelog\n{entry}")
        logger.info(f"Changelog updated at {changelog_path}")
    except Exception as e:
        logger.error(f"Failed to update changelog: {str(e)}")

def release_version(new_version: str) -> None:
    """
    Runs a Git release command to create a release for the new version.
    Adjust the command below if you use a different tool or workflow.
    """
    try:
        # Example: using a hypothetical 'git release' command
        result = subprocess.run(
            ['git', 'release', 'create', new_version],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        logger.info(f"Git release successful: {result.stdout.decode().strip()}")
    except subprocess.CalledProcessError as e:
        logger.error(f"Git release failed: {e.stderr.decode().strip()}")

def main():
    parser = argparse.ArgumentParser(description="Automate version bumping and release notes generation")
    parser.add_argument('--version_file', type=str, default=None,
                        help='Absolute or relative path to the version file. If relative, it is assumed relative to the project root.')
    parser.add_argument('--commit_limit', type=int, default=5, help='Number of commit messages to include')
    parser.add_argument('--model_name', type=str, default='EleutherAI/gpt-neo-1.3B', help='Model name for release notes generation')
    parser.add_argument('--update_changelog', action='store_true', help='Append release notes to CHANGELOG.md')
    args = parser.parse_args()

    try:
        # Initialize components with the given arguments
        version_manager = VersionManager(args.version_file)
        git_manager = GitManager()
        incrementor = VersionIncrementor()
        notes_generator = ReleaseNotesGenerator(args.model_name)

        # Gather information from Git and version file
        current_version = version_manager.get_current_version()
        changed_files = git_manager.get_changed_files()
        commit_messages = git_manager.get_commit_history(args.commit_limit)
        change_level = incrementor.determine_change_level(changed_files, commit_messages)
        new_version = incrementor.increment_version(current_version, change_level)
        title, description = notes_generator.generate_summary(commit_messages)

        # Update the version file
        version_manager.update_version(new_version)

        logger.info(f"Updated version: {current_version} → {new_version}")
        logger.info(f"Change level: {change_level}")
        logger.info(f"Release Title: {title}")
        logger.info(f"Release Description:\n{description}")

        # Optionally update the changelog
        if args.update_changelog:
            append_to_changelog(new_version, title, description)
        
        # Interactive prompt for releasing the updated version
        user_input = input("Do you want to release the updated version using git release? [y/n]: ").strip().lower()
        if user_input in ['y', 'yes']:
            release_version(new_version)
        else:
            logger.info("Release skipped by the user.")

    except Exception as e:
        logger.error(f"Failed to generate release: {str(e)}")
        raise SystemExit(1)

if __name__ == "__main__":
    main()
