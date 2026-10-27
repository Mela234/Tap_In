import React, { useState, useEffect, useRef } from "react";
import { getHexagonTrends } from "./services/api";
import StoryDeck from "./StoryDeck";
import "./HexagonHub.css";

// Clockwise from the top facet. Keys match the backend topics.
const TOPICS = [
  {
    key: "tech",
    label: "Tech",
    light: "#e4e1ff",
    deep: "#8f86e8",
    icon: "M13 2 4 14h7l-1 8 9-12h-7z",
  },
  {
    key: "entertainment",
    label: "Entertainment",
    light: "#ffe0ea",
    deep: "#ef86ad",
    icon: "M12 3a9 9 0 1 0 0 18 9 9 0 0 0 0-18z M10 8.5v7l6-3.5z",
  },
  {
    key: "culture",
    label: "Culture",
    light: "#ffe6d6",
    deep: "#f4a172",
    icon: "M12 3c.6 4.2 2.8 6.4 7 7-4.2.6-6.4 2.8-7 7-.6-4.2-2.8-6.4-7-7 4.2-.6 6.4-2.8 7-7z M19 16.5c.2 1.3.9 2 2 2.2-1.1.2-1.8.9-2 2.2-.2-1.3-.9-2-2-2.2 1.1-.2 1.8-.9 2-2.2z",
  },
  {
    key: "world",
    label: "World",
    light: "#d9f3e9",
    deep: "#5fbf9c",
    icon: "M12 3a9 9 0 1 0 0 18 9 9 0 0 0 0-18z M3 12h18 M12 3c2.5 2.6 3.8 5.6 3.8 9s-1.3 6.4-3.8 9c-2.5-2.6-3.8-5.6-3.8-9S9.5 5.6 12 3z",
  },
  {
    key: "sports",
    label: "Sports",
    light: "#fff1c4",
    deep: "#e9bb3c",
    icon: "M7 4h10v4a5 5 0 0 1-10 0z M7 6H4.5a3 3 0 0 0 3 4 M17 6h2.5a3 3 0 0 1-3 4 M12 13v4 M8 20.5h8 M9.5 17h5",
  },
  {
    key: "money",
    label: "Money",
    light: "#dcecfa",
    deep: "#6aaee0",
    icon: "M12 3a9 9 0 1 0 0 18 9 9 0 0 0 0-18z M15 9.2c-.6-.9-1.7-1.4-3-1.4-1.7 0-3 .9-3 2.1 0 2.9 6 1.4 6 4.3 0 1.2-1.3 2.1-3 2.1-1.4 0-2.6-.6-3.2-1.5 M12 6.3v1.5 M12 16.3v1.5",
  },
];

const CHECK_ICON = "M5 12.5l4.5 4.5L19 7.5";

const R = 200;
const GAP = 5;
const IDLE_SPEED = 7; // degrees per second
const HOVER_SPEED = 1.2;

const point = (r, deg) => {
  const rad = (deg * Math.PI) / 180;
  return [r * Math.cos(rad), r * Math.sin(rad)];
};

const fmt = (pts) => pts.map(([x, y]) => `${x.toFixed(1)},${y.toFixed(1)}`).join(" ");

// Facet i is the triangle from the centre to the side between corners -120+60i and -60+60i.
const facetPoints = (i) => {
  const a = -120 + 60 * i;
  return fmt([[0, 0], point(R, a), point(R, a + 60)]);
};

const hexPoints = (r, offset = 0) =>
  fmt([0, 60, 120, 180, 240, 300].map((deg) => point(r, deg + offset)));

const loadCaughtUp = (edition) => {
  try {
    return JSON.parse(localStorage.getItem(`tapin-caughtup-${edition}`)) || {};
  } catch {
    return {};
  }
};

function Prism({ hovered, active, doneTopics, compact, onHover, onSelect }) {
  const spinRef = useRef(null);
  const tiltRef = useRef(null);
  const shineRefs = useRef([]);
  const shadeRefs = useRef([]);
  const iconRefs = useRef([]);
  const motion = useRef({ angle: 0, speed: IDLE_SPEED, light: -135, lightTarget: -135, lastMouse: 0 });
  const slowRef = useRef(false);

  useEffect(() => {
    slowRef.current = hovered !== null;
  }, [hovered]);

  // Spin the prism and relight each facet every frame, outside of React renders.
  useEffect(() => {
    const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    const m = motion.current;
    let last = performance.now();
    let raf;

    const tick = (now) => {
      const dt = Math.min(0.05, (now - last) / 1000);
      last = now;

      const targetSpeed = reduceMotion ? 0 : slowRef.current ? HOVER_SPEED : IDLE_SPEED;
      m.speed += (targetSpeed - m.speed) * Math.min(1, dt * 3);
      m.angle = (m.angle + m.speed * dt) % 360;

      // With no mouse around, let the light wander on its own.
      if (now - m.lastMouse > 2500 && !reduceMotion) m.lightTarget += dt * 14;
      const lightDelta = ((((m.lightTarget - m.light) % 360) + 540) % 360) - 180;
      m.light += lightDelta * Math.min(1, dt * 4);

      spinRef.current?.setAttribute("transform", `rotate(${m.angle.toFixed(2)})`);
      for (let i = 0; i < 6; i++) {
        const facing = ((-90 + 60 * i + m.angle - m.light) * Math.PI) / 180;
        const brightness = 0.5 + 0.5 * Math.cos(facing);
        shineRefs.current[i]?.setAttribute("opacity", (0.04 + 0.6 * brightness ** 2).toFixed(3));
        shadeRefs.current[i]?.setAttribute("opacity", (0.16 * (1 - brightness)).toFixed(3));
        const [x, y] = point(R * 0.56, -90 + 60 * i);
        iconRefs.current[i]?.setAttribute(
          "transform",
          `translate(${x.toFixed(1)} ${y.toFixed(1)}) rotate(${(-m.angle).toFixed(2)})`
        );
      }
      raf = requestAnimationFrame(tick);
    };

    raf = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(raf);
  }, []);

  // The light follows the cursor and the whole prism tilts towards it.
  useEffect(() => {
    const onMove = (e) => {
      const el = tiltRef.current;
      if (!el) return;
      const rect = el.getBoundingClientRect();
      const dx = e.clientX - (rect.left + rect.width / 2);
      const dy = e.clientY - (rect.top + rect.height / 2);
      motion.current.lightTarget = (Math.atan2(dy, dx) * 180) / Math.PI;
      motion.current.lastMouse = performance.now();
      const nx = Math.max(-1, Math.min(1, (dx / window.innerWidth) * 2));
      const ny = Math.max(-1, Math.min(1, (dy / window.innerHeight) * 2));
      el.style.transform = `rotateX(${(-ny * 16).toFixed(2)}deg) rotateY(${(nx * 16).toFixed(2)}deg)`;
    };
    window.addEventListener("pointermove", onMove);
    return () => window.removeEventListener("pointermove", onMove);
  }, []);

  const handleKey = (e, i) => {
    if (e.key === "Enter" || e.key === " ") {
      e.preventDefault();
      onSelect(i);
    }
  };

  return (
    <div className="prism-tilt" ref={tiltRef}>
      <div className="prism-shadow" aria-hidden="true" />
      <svg className="prism-svg" viewBox="-240 -240 480 480" role="group" aria-label="News categories">
        <defs>
          {TOPICS.map((t, i) => {
            const [x2, y2] = point(R * 0.87, -90 + 60 * i);
            return (
              <linearGradient key={t.key} id={`facet-${t.key}`} gradientUnits="userSpaceOnUse" x1="0" y1="0" x2={x2} y2={y2}>
                <stop offset="0" stopColor="#ffffff" />
                <stop offset="0.35" stopColor={t.light} />
                <stop offset="1" stopColor={t.deep} />
              </linearGradient>
            );
          })}
          <linearGradient id="facet-sheen" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0.35" stopColor="#fff" stopOpacity="0" />
            <stop offset="0.5" stopColor="#fff" stopOpacity="0.9" />
            <stop offset="0.65" stopColor="#fff" stopOpacity="0" />
            <animateTransform attributeName="gradientTransform" type="translate" from="-1 -1" to="1 1" dur="2.6s" repeatCount="indefinite" />
          </linearGradient>
          <radialGradient id="prism-pearl" cx="0.35" cy="0.3" r="0.8">
            <stop offset="0" stopColor="#ffffff" />
            <stop offset="0.55" stopColor="#f7ebf3" />
            <stop offset="1" stopColor="#dcb5cf" />
          </radialGradient>
        </defs>

        {!compact && (
          <g className="prism-orbit" aria-hidden="true">
            <polygon points={hexPoints(226, 30)} />
            {TOPICS.map((t, i) => {
              const [x, y] = point(226, -60 + 60 * i);
              return <circle key={t.key} cx={x} cy={y} r="4" fill={t.deep} />;
            })}
          </g>
        )}

        <g ref={spinRef}>
          {TOPICS.map((t, i) => {
            const lift = hovered === i ? 18 : active === i ? 26 : GAP;
            const [ox, oy] = point(lift, -90 + 60 * i);
            const done = doneTopics.has(t.key);
            const pts = facetPoints(i);
            return (
              <g
                key={t.key}
                className={`facet ${active !== null && active !== i ? "is-dim" : ""}`}
                style={{ transform: `translate(${ox}px, ${oy}px)` }}
                role="button"
                tabIndex={0}
                aria-label={t.label}
                aria-pressed={active === i}
                onClick={() => onSelect(i)}
                onKeyDown={(e) => handleKey(e, i)}
                onMouseEnter={() => onHover(i)}
                onMouseLeave={() => onHover(null)}
                onFocus={() => onHover(i)}
                onBlur={() => onHover(null)}
              >
                <polygon className="facet-base" points={pts} fill={`url(#facet-${t.key})`} />
                <polygon ref={(el) => (shineRefs.current[i] = el)} points={pts} fill="#ffffff" />
                <polygon ref={(el) => (shadeRefs.current[i] = el)} points={pts} fill="#3a2434" />
                {done && <polygon className="facet-sheen" points={pts} fill="url(#facet-sheen)" />}
                <polygon className="facet-edge" points={pts} />
                <g ref={(el) => (iconRefs.current[i] = el)} className="facet-icon">
                  <path d={done ? CHECK_ICON : t.icon} transform="scale(1.55) translate(-12 -12)" />
                </g>
              </g>
            );
          })}
          <circle className="prism-glow" r="34" />
          <polygon className="prism-pearl" points={hexPoints(22)} fill="url(#prism-pearl)" />
        </g>
      </svg>
    </div>
  );
}

function HexagonHub() {
  const [topics, setTopics] = useState({});
  const [edition, setEdition] = useState(null);
  const [error, setError] = useState(null);
  const [hovered, setHovered] = useState(null);
  const [active, setActive] = useState(null);
  const [caughtUp, setCaughtUp] = useState({});

  useEffect(() => {
    const fetchTopics = async () => {
      try {
        const data = await getHexagonTrends();
        setTopics(data.topics || {});
        setEdition(data.edition);
        setCaughtUp(loadCaughtUp(data.edition));
      } catch (err) {
        console.error("Error fetching hexagon trends:", err);
        setError("Couldn't reach the newsroom");
      }
    };

    fetchTopics();
  }, []);

  useEffect(() => {
    if (!edition) return;
    try {
      localStorage.setItem(`tapin-caughtup-${edition}`, JSON.stringify(caughtUp));
    } catch {
      // Storage unavailable (private mode); progress just won't persist.
    }
  }, [caughtUp, edition]);

  useEffect(() => {
    if (active === null) return;
    const onKey = (e) => e.key === "Escape" && setActive(null);
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [active]);

  const storiesFor = (key) => topics[key] || [];
  const doneTopics = new Set(
    TOPICS.filter((t) => {
      const stories = storiesFor(t.key);
      return stories.length > 0 && stories.every((s) => caughtUp[`${t.key}-${s.id}`]);
    }).map((t) => t.key)
  );

  const selectTopic = (i) => {
    setActive(active === i ? null : i);
    setHovered(null);
  };

  const activeTopic = active !== null ? TOPICS[active] : null;
  const captionTopic = hovered !== null ? TOPICS[hovered] : activeTopic;
  const themeTopic = activeTopic || captionTopic;

  return (
    <section
      className={`hex-hub ${activeTopic ? "is-open" : ""}`}
      style={themeTopic ? { "--topic": themeTopic.deep, "--topic-soft": themeTopic.light } : undefined}
    >
      <div className="hex-atmosphere" aria-hidden="true">
        <span className="blob blob-1" />
        <span className="blob blob-2" />
        <span className="blob blob-3" />
        <span className="blob blob-4" />
        <div className="hex-tint" />
        <div className="hex-grain" />
      </div>

      <div className="prism-stage">
        <Prism
          hovered={hovered}
          active={active}
          doneTopics={doneTopics}
          compact={!!activeTopic}
          onHover={setHovered}
          onSelect={selectTopic}
        />
      </div>

      <div className="hex-caption" aria-live="polite">
        {captionTopic ? (
          <span className="caption-name" key={captionTopic.key}>
            {captionTopic.label}
            <sup style={{ color: captionTopic.deep }}>{storiesFor(captionTopic.key).length}</sup>
          </span>
        ) : error ? (
          <span className="caption-hint">{error}</span>
        ) : (
          <span className="caption-hint">tap a piece</span>
        )}
      </div>

      {activeTopic && (
        <StoryDeck
          key={activeTopic.key}
          stories={storiesFor(activeTopic.key)}
          isCaughtUp={(id) => !!caughtUp[`${activeTopic.key}-${id}`]}
          onGotIt={(id) => setCaughtUp((prev) => ({ ...prev, [`${activeTopic.key}-${id}`]: true }))}
          onClose={() => setActive(null)}
        />
      )}
    </section>
  );
}

export default HexagonHub;
