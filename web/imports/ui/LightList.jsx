import React, { useRef, useEffect } from 'react';
import {createUseStyles} from 'react-jss';
import classNames from 'classnames';
import Snowfall from 'react-snowfall';

import { LightButton } from './LightButton';
import { mediumBreakpoint } from './breakpoints';

const lightsSegmentImage = '/images/lights-segment.png';
const candycaneStripeImage = '/images/candycane-stripe.png';

const useStyles = createUseStyles({
  lightList: {
    position: 'relative',
    background: 'black',
    border: '12px ridge #a75220',
    display: 'flex',
    flexWrap: 'wrap',
    alignItems: 'stretch',
    alignContent: 'stretch'
  },
  light: {
    width: '50%',
    [mediumBreakpoint]: {
      width: '20%'
    },
    display: 'flex',
    alignItems: 'center',
  },
});

export const LightList = ({ lights, selectedLight, setSelectedLightId, className }) => {
  const selectedRef = useRef(null);
  const selectedClass = 'selected';
  const classes = useStyles();

  useEffect(() => {
    const selectedElements = Array.from(selectedRef.current.getElementsByClassName(selectedClass));
    selectedElements.forEach((selectedElement) => {
      setTimeout(() => selectedElement.scrollIntoView({
        behavior: 'smooth'
      }), 0);
    });
  }, [selectedLight?._id]);

  const handleClick = (light) => {
    setSelectedLightId(light._id);
  }

  return (
    <div className={classNames(className, classes.lightList)} ref={selectedRef}>
      { lights.map((light, lightIndex) =>
        <div key={ light._id }
             className={classNames({
               [classes.light]: true,
               [selectedClass]: (selectedLight === light)
             })}
        >
          <LightButton
            light={light}
            image={lightsSegmentImage}
            onClick={() => handleClick(light)}
            isSelected={selectedLight === light}
            selectedStyle={{
              border: '6px solid transparent',
              borderImage: `url(${candycaneStripeImage})`,
              borderImageRepeat: 'round',
              borderImageSlice: 50
            }}
            lightIndex={lightIndex}
          />
        </div>
      )}
      <Snowfall
        speed={[0.7, 1.0]}
        wind={[-0.2, 0.5]}
        radius={[0.5, 1.0]}
        snowflakeCount={50}
      />
    </div>
  )
}
