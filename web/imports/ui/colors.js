import tinycolor from 'tinycolor2';

export const animationCss = {
  '@keyframes gradualAnimation': {
    from: {
      filter: 'hue-rotate(0deg)'
    },
    to: {
      filter: 'hue-rotate(360deg)'
    }
  }
};

export const getLightCss = (light) => {
  if (light.colourMode === 'white') {
    return {
      background: '#FDF4DC'
    };
  }
  else if (light.colourMode === 'colour') {
    return {
      background: tinycolor.fromRatio({
        h: light?.colourHue || 0,
        s: light?.colourSaturation || 0,
        v: 1,
        a: 1,
      }).toHexString()
    };
  }
  else if (light.colourMode === 'rainbow') {
    return {
      background: 'linear-gradient(to right, #FF3333,#FFFF33,#33FF33,#33FFFF,#3333FF)'
    };
  }
  else if (light.colourMode === 'gradual') {
    return {
      //background: 'hsl(0%, 100%, 70%)',
      '& > $lightBackground': {
        background: '#FF3333',
        animation: '$gradualAnimation 5s infinite',
      }
    };
  }
  else {
    return {
      background: '#333333',
    };
  }
};

export const getLightPickerColour = (light) => {
  return tinycolor.fromRatio({
    h: light?.colourHue || 0,
    s: 1,
    v: 1,
    a: light?.colourSaturation || 0,
  }).toHex8String();
};
