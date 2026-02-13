import streamlit as st
from embeddings.search import semantic_search


st.set_page_config(
    page_title="StashSave AI Search",
    page_icon="🔎",
    layout="wide"
)


st.title("🔎 StashSave — Semantic Memory Search")
st.caption("Search across your saved developer tools using AI embeddings")


# Search input

query = st.text_input(
    "What are you looking for?",
    placeholder="e.g. figma to react, ai ui builder, auth library..."
)

top_k = st.slider("Number of results", 1, 10, 5)
user_id = st.number_input("User ID", min_value=1, step=1, value=1)


# Run search

if st.button("Search") and query:
    with st.spinner("Searching your memory..."):
        results = semantic_search(query=query, user_id=int(user_id), top_k=top_k)

    st.subheader(f"Results for: '{query}'")

    if not results:
        st.warning("No relevant memories found.")
    else:
        for r in results:
            with st.container():
                st.markdown(f"### {r['title']}")
                st.write(r["description"] or "No description available.")

                if r["tags"]:
                    st.caption(f"Tags: {r['tags']}")

                st.markdown(f"[Open link]({r['url']})")
                st.progress(min(r["score"], 1.0))
                st.caption(f"Relevance score: {r['score']:.3f}")

                st.divider()
