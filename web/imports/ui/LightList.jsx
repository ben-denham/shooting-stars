import React from 'react';
import {createUseStyles} from 'react-jss';
import classNames from 'classnames';
import Snowfall from 'react-snowfall';

const useStyles = createUseStyles({
  lightList: {
    position: 'relative',
  }
});

const Light = ({ light, onClick }) => {
  return (
    <div onClick={onClick}>
      Light {light.idx} ({light.colourMode}, {light.colourHue}, {light.colourSaturation}, {light.animation})
    </div>
  );
}

export const LightList = ({ lights, setSelectedLightId, className }) => {
  const classes = useStyles();

  return (
    <div className={classNames(className, classes.lightList)}>
      <Snowfall
        speed={[0.7, 1.0]}
        wind={[-0.2, 0.5]}
        radius={[0.5, 1.0]}
        snowflakeCount={50}
      />
      { lights.map(light =>
        <Light key={ light._id }
               light={light}
               onClick={() => setSelectedLightId(light._id)}>
        </Light>
      )}
    </div>
  )
}
