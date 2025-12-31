import React, { useState, useEffect } from "react";
import "./HighlightCarousel.css";

const highlights = [
  {
    id: 1,
    platform: "TikTok",
    title: "NPC Streaming",
    description: "Creators act like video game NPCs reacting to gifts.",
  },
  {
    id: 2,
    platform: "Instagram",
    title: "Photo Dump Era",
    description: "Casual, imperfect photo carousels replacing curated feeds.",
  },
  {
    id: 3,
    platform: "Twitter",
    title: "Main Character Threads",
    description: "Personal storytelling threads gaining viral traction.",
  },
];

function HighlightsCarousel() {
  const [index, setIndex] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setIndex((prev) => (prev + 1) % highlights.length);
    }, 4000);
    return () => clearInterval(interval);
  }, []);

  return (
    <section className="highlights-window">
      <div className="highlights-header">
        <h2>This Week’s Highlights</h2>
      </div>

      <div className="highlights-viewport">
        <div
          className="highlights-track"
          style={{ transform: `translateX(-${index * 100}%)` }}
        >
          {highlights.map((item) => (
            <div className="highlights-card" key={item.id}>
              <span className={`platform ${item.platform.toLowerCase()}`}>
                {item.platform}
              </span>
              <h3>{item.title}</h3>
              <p>{item.description}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

export default HighlightsCarousel;
