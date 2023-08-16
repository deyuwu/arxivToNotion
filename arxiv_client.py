import urllib

import arxiv


# https://pypi.org/project/arxiv/
def arxiv_search(query, max_result=10, sort_by=arxiv.SortCriterion.SubmittedDate):
    search = arxiv.Search(
        query=query,
        max_results=max_result,
        sort_by=sort_by,
        sort_order=arxiv.SortOrder.Descending
    )

    return search.results()


def input_to_arxiv_query():
    # Mapping of user-friendly names to arXiv prefixes
    fields = {
        "All": "all",
        "Title": "ti",
        "Author": "au",
        "Abstract": "abs",
        "Comment": "co",
        "Journal Reference": "jr",
        "Subject Category": "cat",
        "Report Number": "rn",
        "ID": "id"
    }

    search_terms = []

    while True:
        # Display available fields for the user
        print("\nPlease select a field:")
        for i, (key, _) in enumerate(fields.items(), 1):
            print(f"{i}. {key}")

        # Get user choice
        choice = int(input("\nEnter your choice (number): "))
        while choice < 1 or choice > len(fields):
            print("Invalid choice. Try again.")
            choice = int(input("\nEnter your choice (number): "))

        # Find the corresponding arXiv prefix for the chosen field
        _, prefix = list(fields.items())[choice - 1]

        # Get user input for the chosen field
        query = input(f"Enter your search term for {list(fields.keys())[choice - 1]}: ")

        # If the chosen field is 'ID', use 'id_list' instead and break
        # (since combining 'ID' with other fields using Boolean operators doesn't make sense)
        if prefix == "id":
            return f"id_list={query}"

        search_terms.append(f"{prefix}:{urllib.parse.quote_plus(query)}")

        # Ask user if they want to add another field
        cont = input("Do you want to add another search term? (yes/no): ").lower()
        if cont != 'yes':
            break
    if len(search_terms) > 1:

        # Construct the final search string
        boolean_op = input("\nChoose a Boolean operator (AND/OR): ").upper()
        while boolean_op not in ['AND', 'OR']:
            print("Invalid choice. Choose AND or OR.")
            boolean_op = input("\nChoose a Boolean operator (AND/OR): ").upper()
        boolean_op = " " + boolean_op + " "
        return boolean_op.join(search_terms)
    else:
        return search_terms[0]
