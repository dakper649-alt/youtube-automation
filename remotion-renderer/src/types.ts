export interface Scene {
  imagePath: string;
  duration: number;
  effect: 'zoom_in' | 'zoom_out' | 'pan_left' | 'pan_right' | 'pan_up' | 'pan_down' | 'static';
  subtitle?: {
    text: string;
    startTime: number;
    endTime: number;
    highlighted?: boolean;
  };
}

export interface VideoConfig {
  scenes: Scene[];
  audioPath?: string;
  fps: number;
  width: number;
  height: number;
}
