import { Composition } from "remotion";
import { Promo } from "./Promo";
import film from "./film.json";

export const RemotionRoot: React.FC = () => {
  return (
    <Composition
      id="Promo"
      component={Promo}
      durationInFrames={film.duration * film.fps}
      fps={film.fps}
      width={1920}
      height={1080}
    />
  );
};
