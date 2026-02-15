import { useEffect, useState } from "react";
import { hasSupabaseConfig, supabase } from "./supabaseClient";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";
const GITHUB_SCOPES = import.meta.env.VITE_GITHUB_SCOPES || "read:user repo";
const REDIRECT_URL = import.meta.env.VITE_SUPABASE_REDIRECT_URL || window.location.origin;

function App() {
  const [session, setSession] = useState(null);
  const [loading, setLoading] = useState(false);
  const [importMessage, setImportMessage] = useState("");
  const [importStage, setImportStage] = useState("");
  const [searchMessage, setSearchMessage] = useState("");
  const [query, setQuery] = useState("");
  const [topK, setTopK] = useState(5);
  const [results, setResults] = useState([]);

  useEffect(() => {
    if (!supabase) {
      return;
    }

    let mounted = true;
    supabase.auth.getSession().then(({ data }) => {
      if (mounted) {
        setSession(data.session || null);
      }
    });

    const {
      data: { subscription }
    } = supabase.auth.onAuthStateChange((_event, nextSession) => {
      setSession(nextSession || null);
    });

    return () => {
      mounted = false;
      subscription.unsubscribe();
    };
  }, []);

  const handleLogin = async () => {
    if (!supabase) {
      return;
    }
    setImportMessage("");
    await supabase.auth.signInWithOAuth({
      provider: "github",
      options: {
        redirectTo: REDIRECT_URL,
        scopes: GITHUB_SCOPES
      }
    });
  };

  const handleLogout = async () => {
    if (!supabase) {
      return;
    }
    await supabase.auth.signOut();
    setResults([]);
    setImportMessage("");
    setImportStage("");
    setSearchMessage("");
  };

  const handleImport = async () => {
    setImportMessage("");
    setImportStage("");
    if (!session?.user?.id) {
      setImportMessage("Login required.");
      return;
    }

    const providerToken = session.provider_token;
    if (!providerToken) {
      setImportMessage(
        "No GitHub provider token in session. Enable token flow/scopes in Supabase GitHub provider."
      );
      return;
    }

    setLoading(true);
    setImportStage("Importing GitHub stars...");
    try {
      const url = `${API_BASE_URL}/ingest/github/${session.user.id}?access_token=${encodeURIComponent(providerToken)}`;
      const response = await fetch(url, { method: "POST" });
      setImportStage("Generating embeddings and saving to database...");
      const body = await response.json();
      if (!response.ok) {
        throw new Error(body.detail || "Import failed");
      }
      setImportStage("Complete.");
      setImportMessage(`Imported/updated ${body.ingested} starred repositories. Go ahead with search.`);
    } catch (error) {
      setImportStage("Failed.");
      setImportMessage(error.message || "Import failed");
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async (event) => {
    event.preventDefault();
    setSearchMessage("");
    setResults([]);

    if (!session?.user?.id) {
      setSearchMessage("Login required.");
      return;
    }
    if (!query.trim()) {
      setSearchMessage("Enter a search query.");
      return;
    }

    setLoading(true);
    try {
      const params = new URLSearchParams({
        query: query.trim(),
        user_id: session.user.id,
        top_k: String(topK)
      });
      const response = await fetch(`${API_BASE_URL}/search?${params.toString()}`);
      const body = await response.json();
      if (!response.ok) {
        throw new Error(body.detail || "Search failed");
      }
      setResults(body.results || []);
      if (!body.results?.length) {
        setSearchMessage("No matching tools found.");
      }
    } catch (error) {
      setSearchMessage(error.message || "Search failed");
    } finally {
      setLoading(false);
    }
  };

  const username =
    session?.user?.user_metadata?.user_name ||
    session?.user?.user_metadata?.preferred_username ||
    session?.user?.email ||
    "";

  return (
    <div className="page">
      <div className="card">
        <h1>StashSave</h1>
        <p className="subtitle">GitHub stars import + semantic search</p>

        {!hasSupabaseConfig ? (
          <p className="error">
            Missing config: set VITE_SUPABASE_URL and VITE_SUPABASE_ANON_KEY in frontend/.env
          </p>
        ) : (
          <>
            <section>
              <h2>Login</h2>
              {session ? (
                <p className="ok">Connected as {username || "GitHub user"}</p>
              ) : (
                <p className="warn">Not connected</p>
              )}
              <div className="row">
                {!session ? (
                  <button onClick={handleLogin} disabled={loading}>
                    Login with GitHub
                  </button>
                ) : (
                  <button onClick={handleLogout} disabled={loading}>
                    Logout
                  </button>
                )}
                <button onClick={handleImport} disabled={loading || !session}>
                  Import GitHub Stars
                </button>
              </div>
              {importStage ? <p className="message">Status: {importStage}</p> : null}
              {importMessage ? <p className="message">{importMessage}</p> : null}
            </section>

            <section>
              <h2>Search Tools</h2>
              <form onSubmit={handleSearch}>
                <input
                  type="text"
                  placeholder="e.g. auth library, react form builder, ai coding assistant"
                  value={query}
                  onChange={(event) => setQuery(event.target.value)}
                />
                <label>
                  Number of results: {topK}
                  <input
                    type="range"
                    min="1"
                    max="10"
                    value={topK}
                    onChange={(event) => setTopK(Number(event.target.value))}
                  />
                </label>
                <button type="submit" disabled={loading || !session}>
                  Search
                </button>
              </form>
              {searchMessage ? <p className="message">{searchMessage}</p> : null}
              <div className="results">
                {results.map((item) => (
                  <article key={item.id} className="result">
                    <h3>{item.title}</h3>
                    <p>{item.description || "No description available."}</p>
                    {item.tags ? <p className="tags">Tags: {item.tags}</p> : null}
                    <a href={item.url} target="_blank" rel="noreferrer">
                      Open link
                    </a>
                    <p className="score">Relevance score: {item.score}</p>
                  </article>
                ))}
              </div>
            </section>
          </>
        )}
      </div>
    </div>
  );
}

export default App;
