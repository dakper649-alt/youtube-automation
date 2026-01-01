import { registerRoot } from 'remotion';
import { Video } from './Video';
import config from './config.json';

registerRoot(() => {
  return <Video config={config} />;
});
