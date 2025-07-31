export default function BookCard({ book, onMarkRead }) {
  return (
    <div className="card" style={{ width: 160 }}>
      {book.cover_url ? (
        <img
          src={book.cover_url}
          alt={book.title}
          style={{
            width: "100%",
            borderRadius: 8,
            filter: "drop-shadow(0 0 8px rgba(57,255,20,0.7))",
          }}
        />
      ) : (
        <div style={{ height: 160, background: "#222", borderRadius: 8 }} />
      )}
      <h4 style={{ margin: "6px 0" }}>{book.title}</h4>
      <div style={{ fontSize: 12, color: "var(--muted)" }}>{book.authors}</div>
      <div style={{ marginTop: 6, display: "flex", gap: 4, flexWrap: "wrap" }}>
        {(book.subjects || "")
          .split(",")
          .slice(0, 3)
          .map((s) => (
            <div key={s} className="tag">
              {s.trim()}
            </div>
          ))}
      </div>
      <button style={{ marginTop: 8, width: "100%" }} onClick={onMarkRead}>
        Mark as Read
      </button>
    </div>
  );
}
