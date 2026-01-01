import React from 'react';
import { useCurrentFrame, useVideoConfig, interpolate, Img, spring } from 'remotion';
import { easeInOutCubic } from '../utils/easing';

interface KenBurnsSceneProps {
  imagePath: string;
  effect: 'zoom_in' | 'zoom_out' | 'pan_left' | 'pan_right' | 'pan_up' | 'pan_down' | 'static';
  durationInFrames: number;
}

export const KenBurnsScene: React.FC<KenBurnsSceneProps> = ({
  imagePath,
  effect,
  durationInFrames,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Плавная анимация с spring эффектом
  const progress = spring({
    frame,
    fps,
    config: {
      damping: 100,
      stiffness: 200,
      mass: 0.5,
    },
  });

  // Применяем easing для ещё большей плавности
  const easedProgress = easeInOutCubic(progress);

  // Эффекты трансформации
  let scale = 1;
  let translateX = 0;
  let translateY = 0;

  switch (effect) {
    case 'zoom_in':
      scale = interpolate(easedProgress, [0, 1], [1, 1.3]);
      break;
    case 'zoom_out':
      scale = interpolate(easedProgress, [0, 1], [1.3, 1]);
      break;
    case 'pan_left':
      scale = 1.2;
      translateX = interpolate(easedProgress, [0, 1], [10, -10]);
      break;
    case 'pan_right':
      scale = 1.2;
      translateX = interpolate(easedProgress, [0, 1], [-10, 10]);
      break;
    case 'pan_up':
      scale = 1.2;
      translateY = interpolate(easedProgress, [0, 1], [10, -10]);
      break;
    case 'pan_down':
      scale = 1.2;
      translateY = interpolate(easedProgress, [0, 1], [-10, 10]);
      break;
  }

  return (
    <div
      style={{
        width: '100%',
        height: '100%',
        overflow: 'hidden',
        backgroundColor: '#000',
      }}
    >
      <Img
        src={imagePath}
        style={{
          width: '100%',
          height: '100%',
          objectFit: 'cover',
          transform: `scale(${scale}) translate(${translateX}%, ${translateY}%)`,
          filter: 'brightness(1.05) contrast(1.1)',  // Лёгкий color grading
        }}
      />
    </div>
  );
};
