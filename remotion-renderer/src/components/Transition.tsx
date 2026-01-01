import React from 'react';
import { useCurrentFrame, interpolate } from 'remotion';

interface TransitionProps {
  children: React.ReactNode;
  transitionType: 'fade' | 'slide' | 'zoom';
  durationInFrames: number;
  direction?: 'in' | 'out';
}

export const Transition: React.FC<TransitionProps> = ({
  children,
  transitionType,
  durationInFrames,
  direction = 'in',
}) => {
  const frame = useCurrentFrame();
  const progress = Math.min(frame / durationInFrames, 1);

  let opacity = 1;
  let translateX = 0;
  let scale = 1;

  if (transitionType === 'fade') {
    opacity = direction === 'in' ? progress : 1 - progress;
  } else if (transitionType === 'slide') {
    translateX = direction === 'in'
      ? interpolate(progress, [0, 1], [-100, 0])
      : interpolate(progress, [0, 1], [0, 100]);
  } else if (transitionType === 'zoom') {
    scale = direction === 'in'
      ? interpolate(progress, [0, 1], [0.8, 1])
      : interpolate(progress, [0, 1], [1, 1.2]);
    opacity = direction === 'in' ? progress : 1 - progress;
  }

  return (
    <div
      style={{
        width: '100%',
        height: '100%',
        opacity,
        transform: `translateX(${translateX}%) scale(${scale})`,
      }}
    >
      {children}
    </div>
  );
};
