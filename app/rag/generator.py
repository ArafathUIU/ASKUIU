from langchain.llms import OpenAI

def generate_answer(documents, query):
    llm = OpenAI(openai_api_key=os.getenv('OPENAI_API_KEY'))
    context = "\n".join([doc.page_content for doc in documents])
    prompt = f"""You are an expert assistant for United International University (UIU). Based on the following context, provide a concise and accurate answer to the query. Cite relevant sources.

Context: {context}

Query: {query}

Answer in 2-3 sentences, ensuring clarity and relevance.
"""
    return llm(prompt)