import React, { useEffect, useState } from 'react';
import classNames from 'classnames';
import {createUseStyles} from 'react-jss';
import { HuePicker, AlphaPicker } from 'react-color';
import tinycolor from 'tinycolor2';

const candycaneStripeImage = '/images/candycane-stripe.png';

const useStyles = createUseStyles({
  wrapper: {
    width: '70%',
    margin: 'auto',
    display: 'flex',
    flexDirection: 'column',
    flex: 1,
    justifyContent: 'space-evenly',
  },
  instructions: {
    fontFamily: 'Courgette',
    fontSize: '22px',
    margin: 0,
  },
  picker: {
    cursor: 'pointer',
    width: '100% !important',
    height: '35px !important',
    '& > div > div': {
      borderRadius: '10px !important',
    },
    '& > div > div > div > div': {
      position: 'relative',
      top: '-3px',
      border: '3px solid black',
      boxShadow: '0 0 5px 2px #AAAAAA !important',
      height: '35px !important',
      width: '35px !important',
      transform: 'translate(-20px, -1px) !important',
    },
  },
  huePicker: ({ hueColour }) => ({
    marginBottom: '30px',
    '& > div > div > div > div': {
      background: `${hueColour} !important`,
    }
  }),
  saturationPicker: ({ saturationColour}) => ({
    '& > div > div > div > div': {
      background: `${saturationColour} !important`,
    },
    '& > div > div:first-child > div': {
      background: 'white !important'
    }
  }),
  paintButtonWrapper: {
    borderStyle: 'solid',
    borderWidth: '6px',
    borderImage: `url(${candycaneStripeImage})`,
    borderImageRepeat: 'round',
    borderImageSlice: 50,
    margin: '0 auto',
    cursor: 'pointer',
  },
  paintButton: {
    margin: 0,
    display: 'block',
    width: '100%',
    border: 'none',
    fontSize: '36px',
    fontFamily: 'Courgette',
    padding: '5px 25px',
    background: '#555555',
    color: 'white',
    cursor: 'pointer',
  },
});

const useLocalStorage = (key, defaultValue) => {
  const [val, setVal] = useState(() => JSON.parse(localStorage.getItem(key)) || defaultValue);
  useEffect(() => {
    localStorage.setItem(key, JSON.stringify(val));
  });
  return [val, setVal];
};

export const PaintPage = () => {
  const [hue, setHue] = useLocalStorage('paintHue', 0);
  const [saturation, setSaturation] = useLocalStorage('paintSaturation', 1);
  const [isPainting, setIsPainting] = useState(false);

  const pickerColour = tinycolor.fromRatio({
    h: hue,
    s: 1,
    v: 1,
    a: saturation || 0,
  }).toHex8String();
  const hueColour = tinycolor.fromRatio({
    h: hue,
    s: 1,
    v: 1,
    a: 1
  }).toHexString();
  const saturationColour = tinycolor.fromRatio({
    h: hue,
    s: saturation,
    v: 1,
    a: 1
  }).toHexString();
  const classes = useStyles({ hueColour, saturationColour });

  const handlePaintButton = () => {
    const disallowedAlert = () => {
      alert('Your browser is not allowing this website to access motion data. If you are on an iPhone, go to Settings -> Safari -> Advanced -> Website Data, then search for this website, click Edit, and delete the entry for it.');
    }

    if (isPainting) {
      setIsPainting(false);
      return;
    }

    let permissionRequest = new Promise((resolve) => resolve('granted'));
    if (typeof(DeviceMotionEvent.requestPermission) === 'function') {
      let permissionRequest = DeviceMotionEvent.requestPermission();
    }
    permissionRequest.then((response) => {
      if (response === 'granted') {
        setIsPainting(true);
      }
      else {
        disallowedAlert();
      }
    }).catch((e) => {
      disallowedAlert();
      console.error(e);
    });
  };

  const [{ x, y, z }, setData] = useState({x: 0, y: 0, z: 0});
  const motionHandler = (event) => {
    setData(event.acceleration);
  };

  useEffect(() => {
    if (isPainting) {
      window.addEventListener('devicemotion', motionHandler);
      return () => window.removeEventListener('devicemotion', motionHandler);
    }
  }, [isPainting]);

  return (
    <>
      <div className={classes.wrapper}>
        <pre>x: {x}, y: {y}, z: {z}</pre>
        <p className={classes.instructions}>
          Pick a colour, click <em>Paint!</em>, then wave your phone
          around to paint on the cone of lights!
        </p>
        <div>
          <HuePicker
            className={classNames(classes.picker, classes.huePicker)}
            color={pickerColour}
            onChange={({ hsv }) => !isPainting && setHue(hsv.h / 360)}
          />
          <AlphaPicker
            className={classNames(classes.picker, classes.saturationPicker)}
            color={pickerColour}
            onChange={({ hsv }) => !isPainting && setSaturation(hsv.a)}
          />
        </div>
        <div className={classes.paintButtonWrapper}>
          <button className={classes.paintButton} onClick={handlePaintButton}>
            {isPainting ? 'Stop' : 'Paint!'}
          </button>
        </div>
      </div>
    </>
  );
};
