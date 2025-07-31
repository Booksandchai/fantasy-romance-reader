export default function Recommendations({ books, onMarkRead }) {
  if (books.length === 0) return <div>Loading recommendations...</div>;
  return (
    <div>
      {books.map((b) => (
        <div key={b.olid} style={{ display: "flex", alignItems: "center", marginBottom: 8 }}>
          <div style={{ flex: 1 }}>
            <div>{b.title}</div>
            <div style={{ fontSize: 12 }}>{b.authors}</div>
          </div>
          <button onClick={() => onMarkRead(b.olid)}>Mark Read</button>
        </div>
      ))}
    </div>
  );
}
