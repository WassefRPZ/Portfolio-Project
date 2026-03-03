export default function Home() {
  const posts = [
    {
      id: 1,
      initials: "AM",
      name: "Alice Martinez",
      time: "2 hours ago",
      content:
        "Just finished an epic 4-hour session of Gloomhaven! Our party finally defeated the boss. What an incredible game! 🎲",
    },
    {
      id: 2,
      initials: "BK",
      name: "Ben Kim",
      time: "5 hours ago",
      content:
        "Won my first Catan tournament today! The longest road strategy finally paid off. Thanks everyone for the great matches! 🏆",
    },
  ];

  const events = [
    { id: 1, title: "D&D Campaign", time: "Tomorrow at 7:00 PM", players: "6 players" },
    { id: 2, title: "Catan Tournament", time: "Friday at 6:30 PM", players: "12 players" },
    { id: 3, title: "Board Game Night", time: "Sunday at 5:00 PM", players: "8 players" },
    { id: 4, title: "Magic: The Gathering", time: "Jan 15 at 8:00 PM", players: "4 players" },
  ];

  return (
    <div style={{ display: "flex", gap: 24 }}>

      {/* MAIN CENTER */}
      <div style={{ flex: 1 }}>

        {/* Share box */}
        <div
          style={{
            background: "#F4F1EA",
            padding: 16,
            borderRadius: 16,
            display: "flex",
            alignItems: "center",
            gap: 12,
            marginBottom: 24,
          }}
        >
          <div
            style={{
              width: 40,
              height: 40,
              borderRadius: "50%",
              background: "#6D4C41",
              color: "#FFF",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              fontWeight: "bold",
            }}
          >
            JD
          </div>

          <input
            placeholder="Share your gaming experience..."
            style={{
              flex: 1,
              padding: 12,
              borderRadius: 12,
              border: "none",
              outline: "none",
              background: "#E8E3D8",
            }}
          />

          <button
            style={{
              padding: "10px 18px",
              borderRadius: 12,
              border: "none",
              background: "#6D4C41",
              color: "#FFF",
              fontWeight: "bold",
              cursor: "pointer",
            }}
          >
            Post
          </button>
        </div>

        {/* Posts */}
        {posts.map((post) => (
          <div
            key={post.id}
            style={{
              background: "#F4F1EA",
              padding: 20,
              borderRadius: 16,
              marginBottom: 20,
            }}
          >
            <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
              <div
                style={{
                  width: 44,
                  height: 44,
                  borderRadius: "50%",
                  background: "#6D4C41",
                  color: "#FFF",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  fontWeight: "bold",
                }}
              >
                {post.initials}
              </div>

              <div>
                <div style={{ fontWeight: 700 }}>{post.name}</div>
                <div style={{ fontSize: 13, color: "#777" }}>{post.time}</div>
              </div>
            </div>

            <div style={{ marginTop: 12, lineHeight: 1.6 }}>
              {post.content}
            </div>
          </div>
        ))}
      </div>

      {/* RIGHT COLUMN */}
      <div style={{ width: 320 }}>
        <h3 style={{ marginBottom: 16 }}>Upcoming Events</h3>

        {events.map((event) => (
          <div
            key={event.id}
            style={{
              background: "#E8E3D8",
              padding: 16,
              borderRadius: 16,
              marginBottom: 16,
            }}
          >
            <div style={{ fontWeight: 700 }}>{event.title}</div>
            <div style={{ marginTop: 6, fontSize: 14, color: "#555" }}>
              {event.time}
            </div>
            <div style={{ marginTop: 6, fontSize: 14, color: "#6D4C41" }}>
              {event.players}
            </div>
          </div>
        ))}

        <button
          style={{
            width: "100%",
            padding: 14,
            borderRadius: 14,
            border: "none",
            background: "#6D4C41",
            color: "#FFF",
            fontWeight: "bold",
            cursor: "pointer",
          }}
        >
          View All Events
        </button>
      </div>
    </div>
  );
}