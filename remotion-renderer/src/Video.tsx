import React from 'react';
import { Sequence, Audio } from 'remotion';
import { KenBurnsScene } from './components/KenBurnsScene';
import { AnimatedSubtitle } from './components/AnimatedSubtitle';
import { Transition } from './components/Transition';
import { VideoConfig } from './types';

interface VideoProps {
  config: VideoConfig;
}

export const Video: React.FC<VideoProps> = ({ config }) => {
  const { scenes, audioPath, fps } = config;

  let currentFrame = 0;

  return (
    <>
      {/* Аудио дорожка */}
      {audioPath && <Audio src={audioPath} />}

      {/* Сцены */}
      {scenes.map((scene, index) => {
        const durationInFrames = Math.round(scene.duration * fps);
        const sceneStart = currentFrame;
        currentFrame += durationInFrames;

        const transitionDuration = Math.round(0.5 * fps); // 0.5 сек transition

        return (
          <Sequence
            key={index}
            from={sceneStart}
            durationInFrames={durationInFrames}
          >
            {/* Transition in */}
            {index > 0 && (
              <Transition
                transitionType="fade"
                durationInFrames={transitionDuration}
                direction="in"
              >
                <KenBurnsScene
                  imagePath={scene.imagePath}
                  effect={scene.effect}
                  durationInFrames={durationInFrames}
                />
              </Transition>
            )}

            {/* Сцена без transition для первого кадра */}
            {index === 0 && (
              <KenBurnsScene
                imagePath={scene.imagePath}
                effect={scene.effect}
                durationInFrames={durationInFrames}
              />
            )}

            {/* Субтитры */}
            {scene.subtitle && (
              <AnimatedSubtitle
                text={scene.subtitle.text}
                startFrame={Math.round(scene.subtitle.startTime * fps)}
                durationInFrames={Math.round(
                  (scene.subtitle.endTime - scene.subtitle.startTime) * fps
                )}
                highlighted={scene.subtitle.highlighted}
              />
            )}
          </Sequence>
        );
      })}
    </>
  );
};
