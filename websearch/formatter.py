def format_results(results: list) -> str:
    """
    Format a list of search results into a readable string for the LLM prompt.
    """
    if not results:
        return "No results found."

    formatted_texts = []
    for i, res in enumerate(results, 1):
        title = res.get('title', 'No Title')
        content = res.get('content', 'No Content')
        url = res.get('url', 'No URL')
        
        formatted_texts.append(
            f"Result {i}:\nTitle: {title}\nURL: {url}\nContent: {content}\n"
        )
        
    return "\n".join(formatted_texts)
