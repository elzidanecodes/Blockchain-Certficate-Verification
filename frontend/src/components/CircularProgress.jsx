// components/CircularProgress.jsx
import { useEffect, useState } from "react";
const RADIUS = 20;
const STROKE = 4;
const CIRCUMFERENCE = 2 * Math.PI * RADIUS;

const CircularProgress = ({ duration = 1000, onDone = () => {} }) => {
  const [offset, setOffset] = useState(CIRCUMFERENCE);
  const [done, setDone] = useState(false);

  useEffect(() => {
    const timeout = setTimeout(() => {
      setOffset(0);
      setDone(true);
      onDone();
    }, duration);
    return () => clearTimeout(timeout);
  }, [duration, onDone]);

  return (
    <div className="relative w-[40px] h-[40px]">
      <svg className="absolute top-0 left-0 w-full h-full rotate-[-90deg]">
        <circle
          cx="20"
          cy="20"
          r={RADIUS}
          stroke="#e5e7eb"
          strokeWidth={STROKE}
          fill="none"
        />
        {!done && (
          <circle
            cx="20"
            cy="20"
            r={RADIUS}
            stroke="#22c55e"
            strokeWidth={STROKE}
            fill="none"
            strokeDasharray={CIRCUMFERENCE}
            strokeDashoffset={offset}
            style={{
              transition: `stroke-dashoffset ${duration}ms linear`,
            }}
          />
        )}
      </svg>

      <div
        className={`relative w-[40px] h-[40px] rounded-50 z-10 flex items-center justify-center ${
          done ? "bg-green-success text-white" : "bg-gray-unsuccess text-white"
        }`}
      >
        ✓
      </div>
    </div>
  );
};

export default CircularProgress;