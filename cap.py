#=====importing libraries===========
import os
from datetime import datetime, date


DATETIME_STRING_FORMAT = "%Y-%m-%d"


def main():
    """Entry point of program"""
    # Create storage files for users and tasks if they dont already exist
    initialize_files()

    # Handle login
    current_user = user_login()

    # Main loop
    for choice in main_menu(current_user):
        if choice == 'r':
            reg_user()
        elif choice == 'a':
            add_task()
        elif choice == 'va':
            view_all()
        elif choice == 'vm':
            view_mine(current_user)
        elif choice == 'gr':
            generate_reports()
        elif choice == 'ds' and current_user == 'admin':
            display_statistics()
        elif choice == 'e':
            print('Goodbye!!!')
            exit()
        else:
            print("You have made a wrong choice, Please Try again")


def initialize_files():
    """Initialize tasks.txt and user.txt if they don't exist."""
    if not os.path.exists("tasks.txt"):
        with open("tasks.txt", "w") as default_file:
            pass

    if not os.path.exists("user.txt"):
        with open("user.txt", "w") as default_file:
            default_file.write("admin;password")


def load_tasks():
    """Load tasks from tasks.txt and return as a list of dictionaries."""
    with open("tasks.txt", 'r') as task_file:
        task_data = task_file.read().strip().split("\n")
        task_list = []
        for t_str in task_data:
            if t_str:  # skip empty lines
                task_components = t_str.split(";")
                task_list.append({
                    'username': task_components[0],
                    'title': task_components[1],
                    'description': task_components[2],
                    'due_date': datetime.strptime(task_components[3], DATETIME_STRING_FORMAT),
                    'assigned_date': datetime.strptime(task_components[4], DATETIME_STRING_FORMAT),
                    'completed': task_components[5] == "Yes"
                })
        return task_list


def load_users():
    """Load users from user.txt and return as a dictionary."""
    with open("user.txt", 'r') as user_file:
        user_data = user_file.read().strip().split("\n")
        return {user.split(';')[0]: user.split(';')[1] for user in user_data}


def save_users(username_password):
    """Save user data to user.txt."""
    with open("user.txt", "w") as out_file:
        user_data = [f"{username};{password}" for username, password in username_password.items()]
        out_file.write("\n".join(user_data))


def save_tasks(task_list):
    """Save tasks to tasks.txt."""
    with open("tasks.txt", "w") as task_file:
        task_list_to_write = []
        for t in task_list:
            str_attrs = [
                t['username'],
                t['title'],
                t['description'],
                t['due_date'].strftime(DATETIME_STRING_FORMAT),
                t['assigned_date'].strftime(DATETIME_STRING_FORMAT),
                "Yes" if t['completed'] else "No"
            ]
            task_list_to_write.append(";".join(str_attrs))
        task_file.write("\n".join(task_list_to_write))


def user_login():
    """Handle user login."""

    # Load users from filestorage
    users = load_users()

    while True:
        print("LOGIN")
        curr_user = input("Username: ")
        curr_pass = input("Password: ")
        if curr_user not in users:
            print("User does not exist")
        elif users[curr_user] != curr_pass:
            print("Wrong password")
        else:
            print("Login Successful!")
            return curr_user


def main_menu(user):
    """Display the main menu and handle user options."""
    while True:
        if user == "admin":
            options = [
            "r - Registering a user",
            "a - Adding a task",
            "va - View all tasks",
            "vm - View my tasks",
            "gr - Generate reports",
            "ds - Display statistics",
            "e - Exit: ",
            ]
        else:
            options = [
            "r - Registering a user",
            "a - Adding a task",
            "va - View all tasks",
            "vm - View my tasks",
            "e - Exit: ",
            ]
        print()
        print("Select one of the following Options below:")
        menu = input("\n".join(options)).lower()

        yield menu  # Use a generator to get menu choices


def reg_user():
    """Register a new user."""

    users = load_users()

    while True:  
        new_username = input("New Username: ")
        new_password = input("New Password: ")
        confirm_password = input("Confirm Password: ")

        if new_password != confirm_password:
            print("Passwords do not match")
            continue

        if new_username in users:
            print("username already exists")
            continue
        
        users[new_username] = new_password
        save_users(users)
        print("New user added")
        return
       


def add_task():
    """Allow a user to add a new task."""

    # Load users from filestorage
    users = load_users()

    task_username = input("Name of person assigned to task: ")
    if task_username not in users:
        print("User does not exist. Please enter a valid username")
        return

    task_title = input("Title of Task: ")
    task_description = input("Description of Task: ")

    while True:
        try:
            task_due_date = input("Due date of task (YYYY-MM-DD): ")
            due_date_time = datetime.strptime(task_due_date, DATETIME_STRING_FORMAT)
            break
        except ValueError:
            print("Invalid datetime format. Please use the format specified")

    curr_date = date.today()
    new_task = {
        "username": task_username,
        "title": task_title,
        "description": task_description,
        "due_date": due_date_time,
        "assigned_date": curr_date,
        "completed": False
    }

    task_list = load_tasks()
    task_list.append(new_task)
    save_tasks(task_list)
    print("Task successfully added.")


def view_all():
    """View tasks for all users."""

    tasks = load_tasks()
    # Display heading
    print("\n\t---ALL TASKS---\n")

    for t in tasks:
        print_task(t)

def view_mine(user):
    """View tasks for current user."""

    # Load tasks from filestorage
    tasks = load_tasks()

    # Create an index to store task id and position in tasks
    task_index= {}
    index = 0
    task_id = 1

    # Display heading
    print("\n\t---MY TASKS---\n")
    for t in tasks:
        if t['username'] == user:
            task_index[task_id] = index
            print_task(t, task_id)
            task_id += 1
        index += 1

    while True:
        try:
            select_task = int(input("Please select a task to mark or edit or enter -1 to "\
                            "go back to main menu: "))
            if select_task == -1:
                return
            
            # If id selected does not exist, prompt user again
            if select_task > task_id:
                print("You have selected a task that does not exist. Please",
                      "enter a valid id\n")
                continue

            break # Break out of loop if input is valid
        except ValueError:
            print("Please enter a number")

    # Display selected task
    print("\t---Selected task---")
    print_task(tasks[task_index[select_task]], select_task)
    
    while True:
        m_or_e = input("Please enter 'm' to mark task as completed or 'e' to edit task: ")
        if m_or_e == 'm':
            tasks[task_index[select_task]]['completed'] = True
            save_tasks(tasks)
            return
        elif m_or_e == 'e':
            if tasks[task_index[select_task]]['completed'] == True:
                print("Cannot edit task. Task already completed")
            target, value = get_target()
            tasks[task_index[select_task]][target] = value
            save_tasks(tasks)
            return
        else:
            print("Please enter a valid option")


def print_task(task, task_id=None):
    """Prints a task to the screen"""

    disp_str = f"Task: \t\t {task['title']}\n"
    if task_id:
        disp_str += f"Task ID: \t {task_id}\n"
    disp_str += f"Assigned to: \t {task['username']}\n"
    disp_str += f"Date Assigned: \t {task['assigned_date'].strftime(DATETIME_STRING_FORMAT)}\n"
    disp_str += f"Due Date: \t {task['due_date'].strftime(DATETIME_STRING_FORMAT)}\n"
    disp_str += f"Task Description: \n {task['description']}\n"
    disp_str += f"Task Complete?: \t {task['completed']}"

    # Display task info
    print(disp_str, "\n")


def get_target():
    """Gets target to be edited and new value"""
    while True:
        target = input("Please enter 'u' to edit username or 'd' to edit due date")
        if target == 'u':
            new_username = input("Please enter the new username")
            """tasks[task_index[select_task]]['username'] = new_username
            save_tasks(tasks)
            """
            return 'username', new_username
        elif target == 'd':
            while True:
                try:
                    task_due_date = input("Due date of task (YYYY-MM-DD): ")
                    task_due_date = datetime.strptime(task_due_date, DATETIME_STRING_FORMAT)
                    return 'due_date', task_due_date
                except ValueError:
                    print("Invalid datetime format. Please use the format specified")
        else:
            print("Please enter a valid option")


def generate_reports():
    """Generate reports about tasks and users into task_overview.txt and 
    user_overview.txt"""

    generate_task_report()
    generate_user_report()


def generate_task_report():
    """Generates report about tasks and saves to task_overview.txt"""

    # Load tasks from file storage
    tasks = load_tasks()

    filename = "task_overview.txt"

    total_tasks = len((tasks))
    comp_tasks = 0
    overdue_tasks = 0
    for task in tasks:
        if task['completed']:
            comp_tasks += 1
        else:
            if datetime.now() > task['due_date']:
                overdue_tasks += 1
    uncomp_tasks = total_tasks - comp_tasks

    task_report = []
    task_report.append(f"\n\t---TASK REPORT---\n")
    task_report.append(f"Total number of tasks: {total_tasks}")
    task_report.append(f"Completed tasks: {comp_tasks}")
    task_report.append(f"Uncompleted tasks: {uncomp_tasks}")
    task_report.append(f"Overdue tasks: {overdue_tasks}")
    task_report.append(
        f"Percentage of incomplate tasks: {uncomp_tasks/total_tasks:.2%}")
    task_report.append(
        f"Percentage of tasks overdue: {comp_tasks/total_tasks:.2%}")

    with open(filename, 'w') as t_file:
        t_file.write("\n".join(task_report))


def generate_user_report():
    """Generates report about users and saves to user_overview.txt"""

    # Load task and user data from file storage
    users = load_users()
    tasks = load_tasks()

    filename = 'user_overview.txt'

    # Get report data
    total_users = len(users)
    total_tasks = len(tasks)

    # Create string to store user report in
    user_report = "\n\t---USER REPORT---\n"
    user_report += f"\nTotal number of users: {total_users}\n"
    user_report += f"Total number of tasks: {total_tasks}\n"

    for username in users.keys():
        user_report += f"\nUser: {username}\n"
        task_count = 0
        comp_count = 0
        overdue_count = 0
        for task in tasks:
            if task['username'] == username:
                task_count += 1
                if task['completed']:
                    comp_count += 1
                    if datetime.now() > task['due_date']:
                        overdue_count += 1
        uncomp_count = task_count - comp_count
        user_report += f"\tTotal tasks assigned: {task_count}\n"
        user_report += f"\tPercentage of tasks assigned: {task_count/total_tasks:.2%}\n"
        user_report += f"\tPercentage of completed tasks: {comp_count/task_count:.2%}\n"
        user_report += f"\tPercentage of uncompleted tasks: {uncomp_count/task_count:.2%}\n"
        user_report += f"\tPercentage of overdue tasks: {overdue_count/task_count:.2%}\n"
        
    # Save report to file
    with open(filename, 'w') as u_file:
        u_file.write(user_report)


def display_statistics():
    """
    Displays reports read from task_overview.txt and user_overview.txt on
    the screen in a user-friendly manner
    """

    # Generate reports if files don't exist
    if not os.path.exists('task_overview.txt'):
        generate_reports()
    if not os.path.exists('user_overview.txt'):
        generate_reports()
    
    # Display task report
    with open('task_overview.txt', 'r') as t_file:
        task_report = t_file.read()
        print(task_report)

    # Display user report
    with open('user_overview.txt', 'r') as u_file:
        user_report = u_file.read()
        print(user_report)
        

if __name__ == '__main__':
    main()
