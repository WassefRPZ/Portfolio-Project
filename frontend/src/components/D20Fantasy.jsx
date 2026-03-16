/**
 * Composant visuel decoratif sur le theme D20.
 */

export default function D20Fantasy() {
  return (
    <svg width="240" height="240" viewBox="0 0 240 240" aria-label="D20">
      <defs>
        <linearGradient id="d20Gem" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0%" stopColor="#7a5244" />
          <stop offset="55%" stopColor="#6d4c41" />
          <stop offset="100%" stopColor="#3b261f" />
        </linearGradient>

        <linearGradient id="d20Gold" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0%" stopColor="#f3e4b3" />
          <stop offset="55%" stopColor="#d2ad59" />
          <stop offset="100%" stopColor="#a67a2d" />
        </linearGradient>

        <radialGradient id="d20Glow" cx="35%" cy="25%" r="75%">
          <stop offset="0%" stopColor="rgba(255,232,190,0.65)" />
          <stop offset="45%" stopColor="rgba(255,232,190,0.18)" />
          <stop offset="100%" stopColor="rgba(255,232,190,0)" />
        </radialGradient>

        <filter id="d20Shadow" x="-30%" y="-30%" width="160%" height="160%">
          <feDropShadow dx="0" dy="14" stdDeviation="10" floodColor="#000" floodOpacity="0.25" />
        </filter>
      </defs>

      <circle cx="120" cy="120" r="90" fill="url(#d20Glow)" />

      <g filter="url(#d20Shadow)">
        <polygon
          points="120,16 198,64 224,120 198,176 120,224 42,176 16,120 42,64"
          fill="url(#d20Gem)"
          stroke="url(#d20Gold)"
          strokeWidth="4"
        />

        <g stroke="rgba(255,255,255,0.18)" strokeWidth="2">
          <line x1="120" y1="16" x2="120" y2="224" />
          <line x1="16" y1="120" x2="224" y2="120" />
          <line x1="42" y1="64" x2="198" y2="176" />
          <line x1="198" y1="64" x2="42" y2="176" />
        </g>

        <text
          x="120"
          y="150"
          textAnchor="middle"
          fontSize="76"
          fontWeight="900"
          fill="rgba(255,255,255,0.92)"
          style={{ letterSpacing: "1px" }}
        >
          20
        </text>
      </g>
    </svg>
  );
}
