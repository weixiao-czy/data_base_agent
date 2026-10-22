import { AbsoluteFill, Audio, Sequence } from "remotion";
import "./global.css";
import track from "./audio/track.wav";
import film from "./film.json";
import { CommercialScene, FilmOverlay } from "./commercial/Commercial";

export const Promo: React.FC = () => (
  <AbsoluteFill style={{ backgroundColor: "#111916" }}>
    <Audio src={track} volume={1} />
    {film.scenes.map((scene, index) => (
      <Sequence key={scene.id} from={scene.from} durationInFrames={scene.duration}>
        <CommercialScene id={scene.id} duration={scene.duration} index={index} />
      </Sequence>
    ))}
    <FilmOverlay />
  </AbsoluteFill>
);
