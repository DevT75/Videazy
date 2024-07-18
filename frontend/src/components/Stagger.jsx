// StaggerAnimation.jsx
import { useState, useEffect, useLayoutEffect, useRef } from "react";
import anime from "animejs";

const StaggerAnimation = () => {
  function useWindowSize() {
    const [size, setSize] = useState({
      rows: 0,
      cols: 0,
      total: 1,
    });

    useLayoutEffect(() => {
      function updateSize() {
        setSize({
          rows: Math.floor(window.innerHeight / 50),
          cols: Math.floor(window.innerWidth / 50),
          total:
            Math.floor(window.innerWidth / 50) *
            Math.floor(window.innerHeight / 50),
        });
      }
      window.addEventListener("resize", updateSize);
      updateSize();
      return () => window.removeEventListener("resize", updateSize);
    }, []);

    return size;
  }

  const { rows, cols, total } = useWindowSize();
  const [tiles, setTiles] = useState(Array.from(Array(total)));

  useEffect(() => {
    setTiles([...Array(total)]);
  }, [total]);

  const animation = useRef(null);

  useEffect(() => {
    animation.current = anime.timeline({
      targets: ".el",
      easing: "spring",
      duration: 0,
    });
  }, []);

  const [toggled, setToggled] = useState(false);

  const handleClick = (event) => {
    setToggled(!toggled);
    const el = event.target.id;
    animation.current.add({
      targets: ".el",
      opacity: toggled ? 0 : 1,
      delay: anime.stagger(20, {
        grid: [cols, rows],
        from: el,
      }),
    });
    animation.current.play();
  };

  return (
    <div className="relative h-screen w-screen overflow-hidden m-0">
      <div className="absolute inset-0 bg-gradient-to-r from-[var(--g1)] via-[var(--g2)] to-[var(--g1)] bg-[length:200%_100%] animate-background-pan"></div>
      <div
        id="tiles"
        className="absolute inset-0 grid"
        style={{
          gridTemplateColumns: `repeat(${cols}, 1fr)`,
          gridTemplateRows: `repeat(${rows}, 1fr)`,
        }}
      >
        {tiles.map((_, index) => (
          <div
            className="relative"
            key={index}
            id={index}
            onClick={handleClick}
          >
            <div className="absolute inset-[0.4px] bg-[rgb(20,20,20)]"></div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default StaggerAnimation;
