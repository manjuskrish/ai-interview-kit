"""
Same simple structure, with the three likely issues fixed.
"""
from openai import OpenAI

client = OpenAI()
MODEL = "gpt-4o"


def chunk(text, size=200, overlap=50):
    if overlap >= size:
        raise ValueError("overlap must be smaller than size")
    chunks = []
    start = 0
    while start < len(text):
        chunks.append(text[start:start + size])
        if start + size >= len(text):  # FIX 1: stop after the last chunk
            break
        start += size - overlap
    return chunks


def summarize(chunks):
    summaries = []
    for c in chunks:  # FIX 2: loop OUTSIDE the call, one request per chunk
        response = client.chat.completions.create(
            model=MODEL,
            temperature=0.2,
            max_tokens=150,  # FIX 3: cap output length
            messages=[{"role": "user", "content": f"Summarize this: {c}"}],
        )
        summaries.append(response.choices[0].message.content)
    return summaries


def meta_summary(summaries):
    combined = "\n".join(summaries)
    response = client.chat.completions.create(
        model=MODEL,
        temperature=0.2,
        max_tokens=300,  # FIX 3: cap output length
        messages=[{"role": "user", "content": f"Combine into a final summary: {combined}"}],
    )
    return response.choices[0].message.content


def main():
    text = open("doc.txt").read()
    chunks = chunk(text)
    summaries = summarize(chunks)
    print(meta_summary(summaries))


if __name__ == "__main__":
    main()
