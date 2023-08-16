import logging

import arxiv
from notion_client import Client, APIResponseError
from notion_client.helpers import get_id

logger = logging.getLogger(__name__)

ARXIV_PROPERTIES = {
    "Title": {"title": {}},
    "Updated": {"date": {}},
    "Published": {"date": {}},
    "Authors": {"rich_text": {}},
    "Summary": {"rich_text": {}},
    "Primary Category": {"select": {}},
    "Categories": {"multi_select": {}},
    "PDF Link": {"url": {}}
    # "Journal Reference": {"rich_text": {}},
    # "Entry ID": {"url": {}},
    # "Comment": {"text": {}},
    # "DOI": {"url": {}},
}
PAGE_FILTER = {"value": 'page', "property": "object"}
DATABASE_FILTER = {"value": 'database', "property": "object"}


class NotionClient:
    def __init__(self, api_key):
        self.notion = Client(auth=api_key)

    def search(self, query, filter):
        return self.notion.search(query=query, filter=filter).get("results")

    def create_database(self, parent_id: str, db_name: str, properties: dict) -> dict:
        """
        :param parent_id: ID of the parent page
        :param db_name: Title of the database
        :return dict: Dictionary representation of the newly created database in Notion.
        """

        logger.info(f"\n\nCreate database '{db_name}' in page {parent_id}...")

        title = [{"type": "text", "text": {"content": db_name}}]
        icon = {"type": "emoji", "emoji": "🎉"}
        # parent page is required
        parent = {"type": "page_id", "page_id": parent_id}
        return self.notion.databases.create(
            parent=parent, title=title, properties=properties, icon=icon
        )

    def add_row_to_database(self, database_id: str, properties: dict) -> dict:
        """
        Add a new row to a Notion database.
        :param database_id: The ID of the Notion database where the row should be added.
        :param properties: A dictionary representing the row's properties.
        :return a dictionary containing information about the created page (row).
        """

        # Define the parent database and properties for the new page (row)
        page_data = {
            "parent": {"database_id": database_id},
            "properties": properties
        }

        # Use the create method of the Notion Client's pages API
        new_page = self.notion.pages.create(**page_data)

        return new_page

    def retrieve_page(self, page_id):
        """
        Retrieve a Page object using the page ID specified
        :param page_id: Identifier for a Notion page
        :return: page object if found, else None
        """
        try:
            return self.notion.pages.retrieve(page_id)
        except APIResponseError as error:
            logging.error(error)
        return None

    def create_arxiv_database(self, parent_id: str, db_name: str):
        return self.create_database(parent_id, db_name, ARXIV_PROPERTIES)

    def add_arxiv_data_to_database(self, database_id: str, result: arxiv.Result) -> dict:

        properties = {
            "Updated": {"date": {"start": result.updated.isoformat()}},
            "Published": {"date": {"start": result.published.isoformat()}},
            "Title": {"title": [{"text": {"content": result.title}}]},
            "Authors": {"rich_text": [{"text": {"content": ', '.join([author.name for author in result.authors])}}]},
            "Summary": {"rich_text": [{"text": {"content": result.summary}}]},
            "Primary Category": {"select": {"name": result.primary_category}},
            "Categories": {"multi_select": [{"name": category} for category in result.categories]},
            "PDF Link": {"url": result.pdf_url}
            # "Journal Reference": {
            #     "rich_text": [{"text": {"content": result.journal_ref if result.journal_ref else ""}}]},
        }
        return self.add_row_to_database(database_id, properties)

