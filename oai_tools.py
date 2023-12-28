# This script provides an interactive command-line interface for performing various tasks using the OpenAI API.
# It includes functionalities like listing assistants, creating and deleting threads, fetching messages, 
# managing files, and more. The script uses environment variables for configuration and provides a menu-driven user experience.

import os
import sys
import appdirs
import json
import openai
from dotenv import load_dotenv


load_dotenv()  # Load environment variables from a .env file

# Now you can use the environment variable
openai_api_key = os.getenv('OPENAI_API_KEY')

# Retrieve and set the OpenAI API key from environment variables
openai_api_key = os.getenv('OPENAI_API_KEY')
client = openai.Client(api_key=openai_api_key)


# Function to get the data file path
def get_user_defaults_file_path():
    user_defaults_path = appdirs.user_data_dir('Cleverbit OpenAI API Tools', 'Cleverbit')
    os.makedirs(user_defaults_path, exist_ok=True)
    return os.path.join(user_defaults_path, 'thread_ids.json')


def list_assistants():
    """
    Fetches and lists all available assistants.
    Assistants are listed in descending order and limited to the top 20.
    If no assistants are available, it prints a message indicating so.
    """
    print("Fetching assistants...")
    response = client.beta.assistants.list(
       order="desc",
        limit="20",
    )

    if not response.data:
        print("No assistants available.")
    else:
        for i, assistant in enumerate(response.data, 1):
            print(f"{i}. 🤖 {assistant.name}  (id:{assistant.id})")


def create_thread():
    """
    Creates a new thread using the OpenAI API.
    Stores the ID of the created thread in a local file.
    Prints the ID of the created thread upon successful creation.
    """
    print("Creating a thread...")
    response = client.beta.threads.create()
    thread_id = response.id
    print(f"Created a thread! id:{thread_id}")
    
    # Store the thread ID in a file
    user_defaults = get_user_defaults_file_path()
    if os.path.exists(user_defaults):
        with open(user_defaults, 'r') as file:
            data = json.load(file)
            thread_ids = data.get('thread_ids', [])
    else:
        thread_ids = []

    thread_ids.append(thread_id)

    with open(user_defaults, 'w') as file:
        json.dump({'thread_ids': thread_ids}, file)


def list_threads():
    """
    Lists all stored thread IDs.
    """
    user_defaults = get_user_defaults_file_path()
    if os.path.exists(user_defaults):
        with open(user_defaults, 'r') as file:
            data = json.load(file)
            thread_ids = data.get('thread_ids', [])
            if thread_ids:
                print("Stored thread IDs:")
                for i, tid in enumerate(thread_ids, 1):
                    print(f"{i}. {tid}")
            else:
                print("No thread IDs stored.")
    else:
        print("No thread IDs stored.")


def delete_thread(thread_id):
    """
    Deletes a specified thread given its thread ID.
    The function prints a success message if the thread is deleted successfully,
    or an error message if there is a problem during deletion.

    :param thread_id: The ID of the thread to be deleted.
    """
    if not thread_id:
        print("No thread ID provided. Please provide a valid thread ID.")
        return

    print(f"Deleting thread {thread_id}...")
    response = client.beta.threads.delete(thread_id)
    if response.deleted:
        print("Thread deleted successfully!")
    else:
        print("There was a problem.")


def list_messages(thread_id):
    """
    Fetches and lists all messages for a specified thread.
    For each message, it prints the message index, message ID, role, and content.

    This function is useful for retrieving and displaying the conversation history
    or interactions within a specific thread.

    :param thread_id: The ID of the thread for which messages are to be fetched.
    """
    if not thread_id:
        print("No thread ID provided. Please provide a valid thread ID.")
        return
    
    print(f"Fetching messages for thread id:{thread_id}...")

    response = client.beta.threads.messages.list(thread_id)

    if not response.data:
        print("This thread has no messages.")
    else:
        for i, message in enumerate(response.data, 1):
            print(f"\n{i}. {message.id} - {message.role}\n\"{message.content.value}\"")


def list_files():
    """
    Lists all available files in the OpenAI environment.
    For each file, it prints its index, filename, and ID.
    If no files are available, a message indicating this is printed.
    """
    print("Fetching files...")
    response = client.files.list()

    if not response.data:
        print("No files available.")
    else:
        for i, file in enumerate(response.data, 1):
            print(f"{i}. {file.filename} - {file.id}")


def upload_file(file_path):
    """
    Uploads a file to the OpenAI environment for a specified purpose.
    The user is prompted to select the purpose of the upload:
    'Assistants' or 'Fine-tune'. The file is then uploaded accordingly.

    :param file_path: The relative path of the file to be uploaded.
    """
    if not file_path:
        print("No file path provided. Please provide a valid file path.")
        return

    print("Select the purpose of the file upload:")
    print("1. Assistants (max 2m tokens)")
    print("2. Fine-tune (.jsonl, max size: 512MB, may incur costs)")
    choice = input("Enter your choice (1 or 2): ").strip()

    # Map the choice to the purpose
    purpose_options = {"1": "assistants", "2": "fine-tune"}
    purpose = purpose_options.get(choice, "assistants")  # Default to "assistants" if invalid choice

    response = client.files.create(
        file=open(file_path, "rb"),
        purpose=purpose
    )

    print(f"{response.filename} uploaded! id:{response.id}")


def delete_file(file_id=None):
    """
    Deletes a file from the OpenAI environment. If the file ID is not provided, it prompts the user
    to select a file from a list of available files. The selected file is then deleted.

    :param file_id: The ID of the file to delete. If None, the user is prompted to choose a file.
    """
    if file_id is None:
        print("Fetching files...")
        response = client.files.list()

        if not response.data:
            print("No files available.")
            return
        
        files = response.data
        for i, file in enumerate(files, 1):
            print(f"{i}. {file.filename} - {file.id}")

        try:
            file_index = int(input("Enter the file number to delete: ")) - 1
            if 0 <= file_index < len(files):
                file = files[file_index]
                file_id = file.id
            else:
                print("Invalid file number.")
                return
        except ValueError:
            print("Invalid input. Please enter a number.")
            return

    # Code to delete a file
    response = client.files.delete(file_id)
    print(f"{file_id}: {response.deleted}")
    return


def styled_input(prompt, style="\033[1m", end_style="\033[0m"):
    """
    Prints a styled prompt and returns the user's input. This function is used to enhance
    the visual appeal of command-line prompts.

    :param prompt: The prompt to display.
    :param style: ANSI style code to apply to the prompt.
    :param end_style: ANSI code to reset the style after the prompt.
    :return: The user's input as a string.
    """
    print(f"{style}{prompt}{end_style}", end="")
    return input()



menu_structure = [
    ("🤖 Assistants", None),
    ("List Assistants", list_assistants),

    ("🧵 Threads", None),
    ("List Threads", list_threads),
    ("Create a Thread", create_thread),
    ("Delete a Thread", lambda: delete_thread(input("Enter the thread ID to delete: ").strip())),
    ("List Messages For Thread", lambda: list_messages(input("Enter the thread ID: ").strip())),

    ("📄 Files", None),
    ("List Files", list_files),
    ("Upload a File", lambda: upload_file(input("Enter the RELATIVE path of the file to upload: "))),
    ("Delete a File", lambda: delete_file(input("Enter the file ID to delete: ").strip() or None)),
]

# Create a separate list for functions
menu_functions = [func for _, func in menu_structure if func]


def display_menu():
    """
    Displays the main menu with section titles and numbered menu options. 
    It differentiates between headers and options, dynamically numbering the latter 
    for user selection. This ensures alignment between the displayed menu and 
    corresponding functions in menu_functions.
    """
    print("\n\033[1mOpenAI API Tools:\033[0m")
    for text, func in menu_structure:
        if func:
            print(f"   {menu_functions.index(func) + 1}. {text}")
        else:
            print(f"\n\033[1m{text}:\033[0m")


def run():
    """
    The main function that runs the interactive command-line interface. It displays the menu,
    takes user input for menu options, and executes the corresponding functions.
    """
    first_run = True
    while True:

        if first_run:
            display_menu()
            choice = styled_input("\nEnter your choice, or 'exit' to quit: ")
            first_run = False
        else :
            choice = styled_input("Enter your choice (or type 'menu' to see options, 'exit' to quit):")

        if choice.lower() == 'menu':
            display_menu()
        elif choice.lower() == 'exit':
            print("Have a nice day! 😃")
            break

        try:
            choice_index = int(choice) - 1  # Convert to zero-based index
            if 0 <= choice_index < len(menu_functions):
                menu_functions[choice_index]()  # Call the corresponding function
            else:
                print("Invalid choice. Please try again.")
        except ValueError:
            if choice.lower() != 'menu':
                print("Invalid choice. Please enter a number.")


if __name__ == "__main__":
    run()
