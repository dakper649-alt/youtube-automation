import React from 'react';
import { useCurrentFrame, useVideoConfig, interpolate, spring } from 'remotion';

interface AnimatedSubtitleProps {
  text: string;
  startFrame: number;
  durationInFrames: number;
  highlighted?: boolean;
}

export const AnimatedSubtitle: React.FC<AnimatedSubtitleProps> = ({
  text,
  startFrame,
  durationInFrames,
  highlighted = false,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const relativeFrame = frame - startFrame;
  const isVisible = relativeFrame >= 0 && relativeFrame < durationInFrames;

  if (!isVisible) return null;

  // Плавное появление
  const entrance = spring({
    frame: relativeFrame,
    fps,
    config: {
      damping: 200,
      stiffness: 300,
    },
  });

  const opacity = interpolate(entrance, [0, 1], [0, 1]);
  const translateY = interpolate(entrance, [0, 1], [30, 0]);
  const scale = interpolate(entrance, [0, 1], [0.8, 1]);

  // Пульсация для highlighted слов
  const pulse = highlighted
    ? Math.sin((relativeFrame / fps) * Math.PI * 2) * 0.1 + 1
    : 1;

  return (
    <div
      style={{
        position: 'absolute',
        bottom: '15%',
        left: '50%',
        transform: `translateX(-50%) translateY(${translateY}px) scale(${scale * pulse})`,
        opacity,
        maxWidth: '80%',
        textAlign: 'center',
      }}
    >
      <div
        style={{
          backgroundColor: highlighted ? '#FFD700' : 'rgba(0, 0, 0, 0.8)',
          color: highlighted ? '#000' : '#fff',
          padding: '16px 32px',
          borderRadius: '12px',
          fontSize: '48px',
          fontWeight: highlighted ? 'bold' : '600',
          fontFamily: 'Arial, sans-serif',
          boxShadow: '0 4px 20px rgba(0, 0, 0, 0.5)',
          border: highlighted ? '3px solid #FFA500' : 'none',
        }}
      >
        {text}
      </div>
    </div>
  );
};
