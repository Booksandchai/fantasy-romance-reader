export default function BookCard({ book, onMarkRead }) {
  return (
    <div style={{ border: "1px solid #ccc", padding: 8, width: 150, borderRadius: 8 }}>
      {book.cover_url ? (
        <img src={book.cover_url} alt={book.title} style={{ width: "100%", borderRadius: 4 }} />
      ) : (
        <div style={{ height: 160, background: "#eee" }} />
      )}
      <h4 style={{ margin: "4px 0" }}>{book.title}</h4>
      <div style={{ fontSize: 12 }}>{book.authors}</div>
      <button style={{ marginTop: 6 }} onClick={onMarkRead}>
        Mark as Read
      </button>
    </div>
  );
}
