export default function ReadList({ books }) {
  if (books.length === 0) return <div>No books marked as read yet.</div>;
  return (
    <div style={{ maxHeight: 300, overflow: "auto" }}>
      {books.map((b) => (
        <div key={b.olid} style={{ marginBottom: 8 }}>
          <strong>{b.title}</strong> <br />
          <small>{b.authors}</small>
        </div>
      ))}
    </div>
  );
}

