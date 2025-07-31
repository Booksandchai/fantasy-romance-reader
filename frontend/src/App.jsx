import { useEffect, useState } from "react";
import BookCard from "./components/BookCard.jsx";
import ReadList from "./components/ReadList.jsx";
import Recommendations from "./components/Recommendations.jsx";
import StatsChart from "./components/StatsChart.jsx";

console.log("frontend bundle loaded; backend URL:", import.meta.env.VITE_BACKEND_URL);

const BACKEND = import.meta.env.VITE_BACKEND_URL || "http://localhost:8000";

function getUserId() {
  let uid = localStorage.getItem("user_id");
  if (!uid) {
    uid = "user_" + Math.random().toString(36).substring(2, 8);
    localStorage.setItem("user_id", uid);
  }
  return uid;
}

function App() {
  const userId = getUserId();
  const [allBooks, setAllBooks] = useState([]);
  const [readBooks, setReadBooks] = useState([]);
  const [recs, setRecs] = useState([]);

  const fetchAll = async () => {
    try {
      const r = await fetch(`${BACKEND}/books`);
      const data = await r.json();
      setAllBooks(data);
    } catch (e) {
      console.error("fetchAll failed", e);
    }
  };

  const fetchRead = async () => {
    try {
      const r = await fetch(`${BACKEND}/user/${userId}/read`);
      const data = await r.json();
      setReadBooks(data);
    } catch (e) {
      console.error("fetchRead failed", e);
    }
  };

  const fetchRecs = async () => {
    try {
      const r = await fetch(`${BACKEND}/user/${userId}/recommendations`);
      const data = await r.json();
      setRecs(data);
    } catch (e) {
      console.error("fetchRecs failed", e);
    }
  };

  useEffect(() => {
    fetchAll();
    fetchRead();
    fetchRecs();
  }, []);

  const markRead = async (olid) => {
    await fetch(`${BACKEND}/user/${userId}/read`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ user_id: userId, olid }),
    });
    await fetchRead();
    await fetchRecs();
  };

  const genreCount = {};
  readBooks.forEach((b) => {
    b.subjects.split(",").forEach((s) => {
      const genre = s.trim().toLowerCase();
      if (!genre) return;
      genreCount[genre] = (genreCount[genre] || 0) + 1;
    });
  });
  const stats = Object.entries(genreCount).map(([name, value]) => ({ name, value }));

  return (
    <div style={{ padding: 20, maxWidth: 1000, margin: "0 auto", fontFamily: "inherit" }}>
      <div className="header">
        <h1>Fantasy & Romance Reader Tracker</h1>
        <div className="magic">✨ witchy & whimsical</div>
      </div>
      <p>
        User ID: <code>{userId}</code>
      </p>
      <div style={{ display: "flex", gap: 30 }}>
        <div style={{ flex: 2 }}>
          <h2>All Books</h2>
          <div className="book-grid">
            {allBooks.slice(0, 40).map((b) => (
              <BookCard key={b.olid} book={b} onMarkRead={() => markRead(b.olid)} />
            ))}
          </div>
        </div>
        <div style={{ flex: 1 }}>
          <div className="sidebar">
            <h2>You've Read</h2>
            <div className="read-list">
              <ReadList books={readBooks} />
            </div>
            <h2>Recommendations</h2>
            <div className="recs">
              <Recommendations books={recs} onMarkRead={(olid) => markRead(olid)} />
            </div>
            <h2>Genre Stats</h2>
            <div className="pie-wrapper">
              <StatsChart data={stats} />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;

