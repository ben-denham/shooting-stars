import React from 'react';

const Light = ({ light, onClick }) => {
  return (
    <div onClick={onClick}>
      Light {light.idx} ({light.colourMode}, {light.colourHue}, {light.colourSaturation}, {light.animation})
    </div>
  );
}

export const LightList = ({ lights, setSelectedLightId }) => {
  return <div id="lights">
    { lights.map(light =>
      <Light key={ light._id }
             light={light}
             onClick={() => setSelectedLightId(light._id)}>
      </Light>
    )}
  </div>
}
