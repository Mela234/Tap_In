import React, { useState, useEffect, useMemo } from "react";

const SWIPE_THRESHOLD = 110;
const CONFETTI_COLORS = ["#8f86e8", "#ef86ad", "#f4a172", "#5fbf9c", "#e9bb3c", "#6aaee0", "#c48bb4"];

const Icon = ({ d, size = 22 }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
    <path d={d} />
  </svg>
);

const ICONS = {
  back: "M15 18l-6-6 6-6",
  skip: "M9 18l6-6-6-6",
  check: "M5 12.5l4.5 4.5L19 7.5",
  close: "M6 6l12 12M18 6L6 18",
  external: "M7 17L17 7M9 7h8v8",
};

function Confetti() {
  // Fixed pseudo-random spread so the burst looks organic but renders deterministically.
  const pieces = useMemo(
    () =>
      Array.from({ length: 26 }, (_, i) => {
        const angle = (i / 26) * Math.PI * 2 + ((i * 37) % 10) / 10;
        const dist = 110 + ((i * 53) % 90);
        return {
          x: `${Math.cos(angle) * dist}px`,
          y: `${Math.sin(angle) * dist - 30}px`,
          rot: `${(i * 67) % 360}deg`,
          c: CONFETTI_COLORS[i % CONFETTI_COLORS.length],
          delay: `${(i % 5) * 30}ms`,
        };
      }),
    []
  );

  return (
    <div className="confetti" aria-hidden="true">
      {pieces.map((p, i) => (
        <span
          key={i}
          style={{ "--x": p.x, "--y": p.y, "--rot": p.rot, "--c": p.c, animationDelay: p.delay }}
        />
      ))}
    </div>
  );
}

function StoryCard({ story, n, depth, flipped, drag, onPointerDown, onPointerMove, onPointerUp }) {
  const isTop = depth === 0;
  const dx = isTop && drag ? drag.dx : 0;
  const style = {
    "--k": depth,
    "--r": `${depth === 0 ? 0 : depth % 2 ? 2.5 : -2}deg`,
    zIndex: 10 - depth,
  };
  if (dx) style.transform = `translateX(${dx}px) rotate(${dx / 16}deg)`;

  return (
    <div
      className={`card ${isTop && flipped ? "is-flipped" : ""} ${drag ? "is-dragging" : ""}`}
      style={style}
      aria-hidden={!isTop}
      onPointerDown={isTop ? onPointerDown : undefined}
      onPointerMove={isTop ? onPointerMove : undefined}
      onPointerUp={isTop ? onPointerUp : undefined}
      onPointerCancel={isTop ? onPointerUp : undefined}
    >
      <div className="card-inner">
        <div className="card-face card-front">
          <div className="card-top">
            <span className="card-num">{String(n + 1).padStart(2, "0")}</span>
            {story.source && (
              <span className="card-src">
                {story.source}
                {story.coverage > 1 && <b> +{story.coverage - 1}</b>}
              </span>
            )}
          </div>
          <h3 className="card-title">{story.title}</h3>
          <span className="card-hint">tap to flip</span>
        </div>

        <div className="card-face card-back">
          <span className="card-hint card-kicker">the gist</span>
          <div className="card-gist">
            <p>{story.description}</p>
            {story.why_it_matters && (
              <p className="card-why">
                <span>why it matters</span>
                {story.why_it_matters}
              </p>
            )}
          </div>
          {story.source_links?.[0] && (
            <a className="card-link" href={story.source_links[0]} target="_blank" rel="noreferrer">
              full story <Icon d={ICONS.external} size={16} />
            </a>
          )}
        </div>
      </div>

      {isTop && dx !== 0 && (
        <span
          className={`card-stamp ${dx > 0 ? "is-got" : "is-skip"}`}
          style={{ opacity: Math.min(1, Math.abs(dx) / SWIPE_THRESHOLD) }}
        >
          {dx > 0 ? "got it" : "skip"}
        </span>
      )}
    </div>
  );
}

function StoryDeck({ stories, isCaughtUp, onGotIt, onClose }) {
  const [pos, setPos] = useState(0);
  const [flipped, setFlipped] = useState(false);
  const [drag, setDrag] = useState(null);
  const [flying, setFlying] = useState([]);

  const finished = pos >= stories.length;
  const gotCount = stories.filter((s) => isCaughtUp(s.id)).length;

  const dismiss = (dir) => {
    if (finished) return;
    const story = stories[pos];
    if (dir > 0) onGotIt(story.id);
    const flight = { story, n: pos, dir, key: `${story.id}-${Date.now()}` };
    setFlying((f) => [...f, flight]);
    setTimeout(() => setFlying((f) => f.filter((x) => x !== flight)), 600);
    setPos(pos + 1);
    setFlipped(false);
  };

  const back = () => {
    if (pos === 0) return;
    setPos(pos - 1);
    setFlipped(false);
  };

  useEffect(() => {
    const onKey = (e) => {
      if (e.key === "ArrowRight") dismiss(1);
      else if (e.key === "ArrowLeft") back();
      else if (e.key === "ArrowDown") dismiss(-1);
      else if ((e.key === " " || e.key === "Enter") && e.target === document.body) {
        e.preventDefault();
        setFlipped((f) => !f);
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  });

  const onPointerDown = (e) => {
    if (e.target.closest("a")) return;
    e.currentTarget.setPointerCapture(e.pointerId);
    setDrag({ x: e.clientX, dx: 0 });
  };

  const onPointerMove = (e) => {
    if (drag) setDrag({ ...drag, dx: e.clientX - drag.x });
  };

  const onPointerUp = () => {
    if (!drag) return;
    const { dx } = drag;
    setDrag(null);
    if (Math.abs(dx) > SWIPE_THRESHOLD) dismiss(dx > 0 ? 1 : -1);
    else if (Math.abs(dx) < 6) setFlipped((f) => !f);
  };

  const visible = stories.slice(pos, pos + 3);

  return (
    <div className="deck-wrap">
      <div className="deck-head">
        <span className="deck-count">
          {finished ? stories.length : pos + 1} / {stories.length}
        </span>
        <button className="deck-close" onClick={onClose} aria-label="Close">
          <Icon d={ICONS.close} size={18} />
        </button>
      </div>

      <div className="deck">
        {finished ? (
          <div className="deck-done">
            {stories.length > 0 && gotCount > 0 && <Confetti />}
            <span className="done-gem" aria-hidden="true" />
            <p className="done-title">{stories.length === 0 ? "quiet week here" : "all caught up"}</p>
            <p className="done-sub">
              {stories.length === 0
                ? "nothing new on this side yet"
                : `${gotCount} of ${stories.length} in the bag`}
            </p>
            <div className="done-actions">
              {stories.length > 0 && (
                <button className="pill" onClick={() => setPos(0)}>
                  again
                </button>
              )}
              <button className="pill pill-main" onClick={onClose}>
                another piece
              </button>
            </div>
          </div>
        ) : (
          visible
            .map((story, depth) => (
              <StoryCard
                key={story.id}
                story={story}
                n={pos + depth}
                depth={depth}
                flipped={flipped}
                drag={depth === 0 ? drag : null}
                onPointerDown={onPointerDown}
                onPointerMove={onPointerMove}
                onPointerUp={onPointerUp}
              />
            ))
            .reverse()
        )}

        {flying.map(({ story, n, dir, key }) => (
          <div key={key} className="card is-flying" style={{ "--dir": dir }} aria-hidden="true">
            <div className="card-inner">
              <div className="card-face card-front">
                <div className="card-top">
                  <span className="card-num">{String(n + 1).padStart(2, "0")}</span>
                </div>
                <h3 className="card-title">{story.title}</h3>
              </div>
            </div>
          </div>
        ))}
      </div>

      {!finished && (
        <>
          <div className="deck-controls">
            <button className="ctl" onClick={back} disabled={pos === 0} aria-label="Previous story">
              <Icon d={ICONS.back} />
            </button>
            <button className="ctl ctl-main" onClick={() => dismiss(1)} aria-label="Got it">
              <Icon d={ICONS.check} size={28} />
            </button>
            <button className="ctl" onClick={() => dismiss(-1)} aria-label="Skip story">
              <Icon d={ICONS.skip} />
            </button>
          </div>
          <div className="deck-dots" aria-hidden="true">
            {stories.map((s, i) => (
              <span
                key={s.id}
                className={`dot ${i === pos ? "is-current" : ""} ${isCaughtUp(s.id) ? "is-got" : ""}`}
              />
            ))}
          </div>
        </>
      )}
    </div>
  );
}

export default StoryDeck;
