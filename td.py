#!/usr/bin/env python3
import os
import sys
import datetime
import logging

# Environment variables
TODO_FILE_PATH = os.getenv('TODO_FILE_PATH', '/home/ubuntu/Projects/notes/')
DEFAULT_TODO_FILE_NAME = "default"
TODO_EDITOR = os.getenv('TODO_EDITOR', 'code')
LOG_FILE_PATH = os.getenv('LOG_FILE_PATH', '/home/ubuntu/Projects/notes/todo.log')
MAX_LIST_ITEMS = 10

# Configure logging
log_file_path = os.path.expanduser(LOG_FILE_PATH)
logging.basicConfig(filename=log_file_path, level=logging.INFO,
                    format='%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')


def create_todo_file_if_not_exists(todo_file_path):
    """Create the todo file if it doesn't exist."""
    if not os.path.exists(todo_file_path):
        with open(todo_file_path, 'w'):
            pass  # Create an empty file
        log_create_todo_list(todo_file_path)

def add_task(todo_file_path, task):
    """Add a task to the todo file."""
    create_todo_file_if_not_exists(todo_file_path)
    task_line = f"{task}\n"

    with open(todo_file_path, 'r') as f:
        lines = f.readlines()

    if len(lines) >= MAX_LIST_ITEMS:
        print(f"Maximum number of tasks ({MAX_LIST_ITEMS}) reached.")
        print("Please edit your todo list to add more tasks.")
        return

    with open(todo_file_path, 'a') as f:
        f.write(task_line)
    print(f"Task added: {task}")

    log_task(task)

def log_task(task):
    """Log task operations to the log file."""
    logging.info(f"Task added: {task}")

def mark_task_as_done(todo_file_path, task_index):
    """Mark a task as done by removing it from the todo list."""
    create_todo_file_if_not_exists(todo_file_path)

    with open(todo_file_path, 'r') as f:
        lines = f.readlines()

    if 1 <= task_index <= len(lines):
        completed_task = lines[task_index - 1].strip()
        
        with open(todo_file_path, 'w') as f:
            for i, line in enumerate(lines):
                if i != task_index - 1:
                    f.write(line)

        print(f"Task marked as done: {completed_task}")
        log_task_completed(completed_task)
    else:
        print("Invalid task number.")

def log_task_completed(task):
    """Log completed task to the log file."""
    logging.info(f"Task completed: {task}")
    
def list_tasks(todo_file_path):
    """List up to 10 tasks from the todo file."""
    create_todo_file_if_not_exists(todo_file_path)

    with open(todo_file_path, 'r') as f:
        lines = f.readlines()

    num_tasks = min(len(lines), MAX_LIST_ITEMS)
    for i in range(num_tasks):
        print(f"{i+1}: {lines[i].strip()}")

    if num_tasks == 0:
        print("No tasks in To Do.")

def edit_todo_file(todo_file_path):
    """Edit the todo file using the specified editor."""
    os.system(f"{TODO_EDITOR} {todo_file_path}")

def list_all_todo_files():
    """List all todo files in the user's home directory and their tasks."""
    todo_files = [filename for filename in os.listdir(TODO_FILE_PATH) if filename.startswith('todo_')]

    if todo_files:
        for todo_file in todo_files:
            todo_file_path = os.path.join(TODO_FILE_PATH, todo_file)
            todo_name = todo_file.replace('todo_', '').replace('.md', '')
            print(f"{todo_name}:")
            tasks = list_tasks(todo_file_path)
            if tasks:
                for i, task in enumerate(tasks):
                    print(f"  {i+1}. {task}")
            print()  # Add a blank line between lists
    else:
        print("No todo lists found.")

def move_task(source_todo_file_path, task_index, dest_todo_file_path):
    """Move a task from one todo list to another."""
    create_todo_file_if_not_exists(source_todo_file_path)
    create_todo_file_if_not_exists(dest_todo_file_path)

    with open(source_todo_file_path, 'r') as f:
        lines = f.readlines()

    if 1 <= task_index <= len(lines):
        task_to_move = lines[task_index - 1].strip()

        # Remove task from source todo list
        with open(source_todo_file_path, 'w') as f:
            for i, line in enumerate(lines):
                if i != task_index - 1:
                    f.write(line)

        # Add task to destination todo list
        with open(dest_todo_file_path, 'a') as f:
            f.write(f"{task_to_move}\n")
        
        source_name = source_todo_file_path.replace(TODO_FILE_PATH, '').replace('todo_', '').replace('.md', '')
        dest_name = dest_todo_file_path.replace(TODO_FILE_PATH, '').replace('todo_', '').replace('.md', '')
        print(f"Task moved: {task_to_move} from {source_name} to {dest_name}")
        log_move_task(source_todo_file_path, dest_todo_file_path, task_to_move)
    else:
        print("Invalid task number.")

def log_move_task(source_todo_file_path, dest_todo_file_path, task):
    """Log task move operation to the log file."""
    logging.info(f"Task moved: '{task}' from '{source_todo_file_path}' to '{dest_todo_file_path}'")

def log_create_todo_list(todo_file_path):
    """Log todo list creation to the log file."""
    logging.info(f"Created new todo list: '{os.path.basename(todo_file_path)}'")

def main():
    if len(sys.argv) < 2 and sys.argv[1] not in ['add', 'edit', 'mark', 'list', 'list_all','mv']:
        todo_file_name = DEFAULT_TODO_FILE_NAME
    elif sys.argv[1] in ['add', 'edit', 'mark', 'list', 'list_all','mv']:
        todo_file_name = DEFAULT_TODO_FILE_NAME
    else:
        todo_file_name = sys.argv[1]
        sys.argv.pop(1)
    
    command = sys.argv[1] if len(sys.argv) > 1 else None

    todo_file_path = os.path.expanduser(os.path.join(TODO_FILE_PATH, "todo_" + todo_file_name + ".md"))

    if command == 'add':
        if len(sys.argv) < 3:
            print(f"Usage: td {todo_file_name} add [task]")
            sys.exit(1)
        task = ' '.join(sys.argv[2:])
        add_task(todo_file_path, task)
    elif command == 'edit':
        edit_todo_file(todo_file_path)
    elif command == 'mark':
        if len(sys.argv) < 3:
            print(f"Usage: td {todo_file_name} mark <task_number>")
            sys.exit(1)
        task_number = int(sys.argv[2])
        mark_task_as_done(todo_file_path, task_number)
    elif command == 'list':
        list_tasks(todo_file_path)
    elif command == 'list_all':
        list_all_todo_files()
    elif command == 'mv':
        if len(sys.argv) < 5:
            print(f"Usage: td mv <source_todo_file> <task_number> <dest_todo_file>")
            sys.exit(1)
        source_todo_file = sys.argv[2]
        task_number = int(sys.argv[3])
        dest_todo_file = sys.argv[4]
        move_task(os.path.expanduser(os.path.join(TODO_FILE_PATH, "todo_" + source_todo_file + ".md")),
                  task_number,
                  os.path.expanduser(os.path.join(TODO_FILE_PATH, "todo_" + dest_todo_file + ".md")))
    else:
        print(f"Usage: td [{DEFAULT_TODO_FILE_NAME}] <todo_file_name> {{add|edit|mark|list|list_completed}}")
        sys.exit(1)

if __name__ == "__main__":
    main()