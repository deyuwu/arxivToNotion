from dotenv import load_dotenv, set_key
import os

from arxiv_client import arxiv_search, input_to_arxiv_query
from notion_client_manager import NotionClient, PAGE_FILTER, DATABASE_FILTER

# Saving the constructed URL in .env file
env_file = '.env'
DB_NAME = 'arxiv'


def init_setup():
    # Example usage
    url = input_to_arxiv_query()
    print(f"\nConstructed URL: http://export.arxiv.org/api/query?search_query={url}")

    # Check if the file exists and has the URL
    if os.path.exists(env_file):
        with open(env_file, 'r') as file:
            contents = file.read()
            if url in contents:
                print("URL already exists in .env file.")
            else:
                # Append the URL to the file
                with open(env_file, 'a') as file:
                    file.write(f"ARXIV_QUERY={url}\n")
                    print("URL saved to .env file.")


def main():
    load_dotenv()  # This loads environment variables from .env
    arxiv_query = os.environ.get('ARXIV_QUERY')
    notion_api_key = os.environ.get('NOTION_API_KEY')
    last_saved = os.environ.get('LAST_SAVED')
    if not arxiv_query:
        init_setup()
    if notion_api_key:
        print(f"Value of notion_api_key: {notion_api_key}")
        print(f"Value of arxiv_query: {arxiv_query}")
        print(f"Value of last_saved: {last_saved}")
    else:
        print("notion_api_key not set.")
        exit()

    page_name = input("\nEnter the page name you have shared with the integration: ")

    notion_client = NotionClient(notion_api_key)
    results = notion_client.search(page_name, PAGE_FILTER)

    result = results[0] if len(results) > 0 else None
    page_id = result['id']
    # create database if doesn't find
    database = notion_client.search(DB_NAME, DATABASE_FILTER)
    if len(database) == 0:
        database = notion_client.create_arxiv_database(page_id, DB_NAME)
    else:
        database = database[0]
    db_id = database['id']
    arxiv_results = arxiv_search(arxiv_query, 10)
    new_last_saved = None
    for ar in arxiv_results:
        if ar.entry_id == last_saved:
            print("Duplicate found, stopping writing.")
            break
        print(f"adding {ar.title}")
        notion_client.add_arxiv_data_to_database(db_id, ar)
        if new_last_saved is None:
            new_last_saved = ar.entry_id

    if new_last_saved:
        set_key(env_file, 'LAST_SAVED', new_last_saved)


if __name__ == "__main__":
    main()
