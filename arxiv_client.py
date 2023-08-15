import arxiv


# https://pypi.org/project/arxiv/
def arxiv_search(query, max_result, sort_by=arxiv.SortCriterion.SubmittedDate):
    search = arxiv.Search(
        query=query,
        max_results=max_result,
        sort_by=sort_by,
        sort_order=arxiv.SortOrder.Descending
    )

    return search.results()
