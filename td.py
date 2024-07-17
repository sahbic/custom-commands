#!/usr/bin/env python3
import os
import subprocess
import sys
import datetime
import logging


# read default value from TODO_FILE_PATH .todo_config file
def read_config(env_variable):
    # get directory of this file
    file_dir = os.path.dirname(os.path.realpath(__file__))
    # get the path of the .todo_config file
    config_file_path = os.path.join(file_dir, ".todo_config")
    with open(config_file_path, "r") as f:
        for line in f:
            key, value = line.strip().split("=")
            if key == env_variable:
                return value
    return None


# Environment variables
TODO_FILE_PATH = read_config("TODO_FILE_PATH")
# Constants
DEFAULT_TODO_FILE_NAME = "default"
TODO_EDITOR = os.getenv("TODO_EDITOR", "nano")
LOG_FILE_PATH = os.path.join(TODO_FILE_PATH, "todo.log")
MAX_LIST_ITEMS = 15

# Configure logging
log_file_path = os.path.expanduser(LOG_FILE_PATH)
logging.basicConfig(
    filename=log_file_path,
    level=logging.INFO,
    format="%(asctime)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


def create_todo_file_if_not_exists(todo_file_path):
    """Create the todo file if it doesn't exist."""
    if not os.path.exists(todo_file_path):
        with open(todo_file_path, "w"):
            pass  # Create an empty file
        log_create_todo_list(todo_file_path)


def add_task(todo_file_path, task, priority=4):
    """Add a task with priority to the todo file."""
    create_todo_file_if_not_exists(todo_file_path)
    task_line = f"{priority}:{task}\n"

    with open(todo_file_path, "r") as f:
        lines = f.readlines()

    if len(lines) >= MAX_LIST_ITEMS:
        print(f"Maximum number of tasks ({MAX_LIST_ITEMS}) reached.")
        print("Please edit your todo list to add more tasks.")
        return

    with open(todo_file_path, "a") as f:
        f.write(task_line)
    print(f"Task added with priority {priority}: {task}")

    log_task(task)


def log_task(task):
    """Log task operations to the log file."""
    logging.info(f"Task added: {task}")
    if is_git_repo(TODO_FILE_PATH):
        git_commit_and_push(TODO_FILE_PATH, f"Add task: {task}")


def mark_task_as_done(todo_file_path, task_index):
    """Mark a task as done by removing it from the todo list."""
    create_todo_file_if_not_exists(todo_file_path)

    with open(todo_file_path, "r") as f:
        lines = f.readlines()

    # Sort tasks by priority
    tasks = sorted(lines, key=lambda x: int(x.split(":")[0]))

    if 1 <= task_index <= len(tasks):
        completed_task = tasks[task_index - 1].strip()

        # Remove the task from the original lines
        lines.remove(tasks[task_index - 1])

        with open(todo_file_path, "w") as f:
            f.writelines(lines)

        print(f"Task marked as done: {completed_task}")
        log_task_completed(completed_task)
    else:
        print("Invalid task number.")


def log_task_completed(task):
    """Log completed task to the log file."""
    logging.info(f"Task completed: {task}")
    if is_git_repo(TODO_FILE_PATH):
        git_commit_and_push(TODO_FILE_PATH, f"Task completed: {task}")


def list_tasks(todo_file_path):
    """List up to MAX_LIST_ITEMS tasks from the todo file, sorted by priority."""
    create_todo_file_if_not_exists(todo_file_path)

    # Pull changes before listing tasks
    if is_git_repo(os.path.dirname(todo_file_path)):
        git_pull(os.path.dirname(todo_file_path))

    with open(todo_file_path, "r") as f:
        lines = f.readlines()

    tasks = sorted(lines, key=lambda x: int(x.split(":")[0]))

    num_tasks = min(len(tasks), MAX_LIST_ITEMS)
    for i in range(num_tasks):
        print(f"{i+1}: {tasks[i].strip()}")

    if num_tasks == 0:
        print("No tasks in To Do.")

    return tasks


def edit_todo_file(todo_file_path):
    """Edit the todo file using the specified editor."""
    # Pull changes before editing the todo file
    if is_git_repo(os.path.dirname(todo_file_path)):
        git_pull(os.path.dirname(todo_file_path))
    os.system(f"{TODO_EDITOR} {todo_file_path}")


def list_all_todo_files():
    """List all todo files in the user's home directory and their tasks."""
    todo_files = [
        filename
        for filename in os.listdir(TODO_FILE_PATH)
        if filename.startswith("todo_")
    ]

    if todo_files:
        for todo_file in todo_files:
            todo_file_path = os.path.join(TODO_FILE_PATH, todo_file)
            todo_name = todo_file.replace("todo_", "").replace(".md", "")
            print(f"{todo_name}:")
            tasks = list_tasks(todo_file_path)
            print()  # Add a blank line between lists
    else:
        print("No todo lists found.")


def move_task(source_todo_file_path, task_index, dest_todo_file_path):
    """Move a task from one todo list to another."""
    source_tasks = list_tasks(source_todo_file_path)
    dest_tasks = list_tasks(dest_todo_file_path)

    if 1 <= task_index <= len(source_tasks):
        task_to_move = source_tasks[task_index - 1].strip()

        # Remove the task from the source todo list
        with open(source_todo_file_path, "r") as f:
            source_lines = f.readlines()

        source_lines.remove(source_tasks[task_index - 1])

        with open(source_todo_file_path, "w") as f:
            f.writelines(source_lines)

        # Add the task to the destination todo list
        with open(dest_todo_file_path, "a") as f:
            f.write(f"{task_to_move}\n")

        source_name = (
            source_todo_file_path.replace(TODO_FILE_PATH, "")
            .replace("todo_", "")
            .replace(".md", "")
        )
        dest_name = (
            dest_todo_file_path.replace(TODO_FILE_PATH, "")
            .replace("todo_", "")
            .replace(".md", "")
        )
        print(f"Task moved: {task_to_move} from {source_name} to {dest_name}")
        log_move_task(source_todo_file_path, dest_todo_file_path, task_to_move)
    else:
        print("Invalid task number.")


def log_move_task(source_todo_file_path, dest_todo_file_path, task):
    """Log task move operation to the log file."""
    logging.info(
        f"Task moved: '{task}' from '{source_todo_file_path}' to '{dest_todo_file_path}'"
    )
    if is_git_repo(TODO_FILE_PATH):
        git_commit_and_push(
            TODO_FILE_PATH,
            f"Move task: '{task}' from '{source_todo_file_path}' to '{dest_todo_file_path}'",
        )


def log_create_todo_list(todo_file_path):
    """Log todo list creation to the log file."""
    logging.info(f"Created new todo list: '{os.path.basename(todo_file_path)}'")
    if is_git_repo(TODO_FILE_PATH):
        git_commit_and_push(TODO_FILE_PATH, f"Add new todo list: {todo_file_path}")


def is_git_repo(path):
    """Check if the given path is a Git repository."""
    return (
        subprocess.call(
            ["git", "-C", path, "rev-parse"],
            stderr=subprocess.STDOUT,
            stdout=open(os.devnull, "w"),
        )
        == 0
    )


def git_commit_and_push(repo_path, message):
    """Commit and push changes to the remote repository."""
    try:
        # add all files starting with "todo"
        for file in os.listdir(repo_path):
            if file.startswith("todo"):
                subprocess.check_call(["git", "-C", repo_path, "add", file])
        subprocess.check_call(
            ["git", "-C", repo_path, "commit", "-m", message, "--quiet"]
        )
        subprocess.check_call(["git", "-C", repo_path, "pull", "--quiet"])
        subprocess.check_call(["git", "-C", repo_path, "push", "--quiet"])
        # print("Changes committed and pushed to remote repository.")
    except subprocess.CalledProcessError as e:
        print(f"Error during git operations: {e}")


def git_pull(repo_path):
    """Pull changes from the remote repository."""
    try:
        subprocess.check_call(["git", "-C", repo_path, "pull", "--quiet"])
        # print("Changes pulled from remote repository.")
    except subprocess.CalledProcessError as e:
        print(f"Error during git pull operation: {e}")


def tag_task(todo_file_path, task_index, priority):
    """Tag a task with a priority."""
    tasks = list_tasks(todo_file_path)

    if 1 <= task_index <= len(tasks):
        tagged_task = tasks[task_index - 1].strip().split(":", 1)[1].strip()

        with open(todo_file_path, "r") as f:
            lines = f.readlines()

        # Replace the original task with the updated priority
        lines[lines.index(tasks[task_index - 1])] = f"{priority}: {tagged_task}\n"

        with open(todo_file_path, "w") as f:
            f.writelines(lines)

        print(f"Task tagged with priority {priority}: {tagged_task}")
        log_task(tagged_task)
    else:
        print("Invalid task number.")


def log_tag_task(task, new_priority):
    """Log tagging task with new priority to the log file."""
    logging.info(f"Task tagged with new priority {new_priority}: {task}")
    if is_git_repo(TODO_FILE_PATH):
        git_commit_and_push(
            TODO_FILE_PATH, f"Tag task with new priority {new_priority}: {task}"
        )


def main():
    if len(sys.argv) < 2 and sys.argv[1] not in [
        "add",
        "edit",
        "mark",
        "list",
        "list_all",
        "mv",
        "tag",
    ]:
        todo_file_name = DEFAULT_TODO_FILE_NAME
    elif sys.argv[1] in ["add", "edit", "mark", "list", "list_all", "mv", "tag"]:
        todo_file_name = DEFAULT_TODO_FILE_NAME
    else:
        todo_file_name = sys.argv[1]
        sys.argv.pop(1)

    command = sys.argv[1] if len(sys.argv) > 1 else None

    todo_file_path = os.path.expanduser(
        os.path.join(TODO_FILE_PATH, "todo_" + todo_file_name + ".md")
    )

    if command == "add":
        if len(sys.argv) < 3:
            print(f"Usage: td add <priority> <task>")
            sys.exit(1)
        priority = int(sys.argv[1]) if sys.argv[1].isdigit() else 4
        task = " ".join(sys.argv[2:])
        add_task(todo_file_path, task, priority)
    elif command == "edit":
        edit_todo_file(todo_file_path)
    elif command == "mark":
        if len(sys.argv) < 3:
            print(f"Usage: td {todo_file_name} mark <task_number>")
            sys.exit(1)
        task_number = int(sys.argv[2])
        mark_task_as_done(todo_file_path, task_number)
    elif command == "list":
        list_tasks(todo_file_path)
    elif command == "list_all":
        list_all_todo_files()
    elif command == "mv":
        if len(sys.argv) < 5:
            print(f"Usage: td mv <source_todo_file> <task_number> <dest_todo_file>")
            sys.exit(1)
        source_todo_file = sys.argv[2]
        task_number = int(sys.argv[3])
        dest_todo_file = sys.argv[4]
        move_task(
            os.path.expanduser(
                os.path.join(TODO_FILE_PATH, "todo_" + source_todo_file + ".md")
            ),
            task_number,
            os.path.expanduser(
                os.path.join(TODO_FILE_PATH, "todo_" + dest_todo_file + ".md")
            ),
        )
    elif command == "tag":
        if len(sys.argv) < 4:
            print(f"Usage: td {todo_file_name} tag <task_number> <new_priority>")
            sys.exit(1)
        task_number = int(sys.argv[2])
        new_priority = int(sys.argv[3])
        tag_task(todo_file_path, task_number, new_priority)
    else:
        print(
            f"Usage: td [{DEFAULT_TODO_FILE_NAME}] <todo_file_name> {{add|edit|mark|list|list_completed}}"
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
