import React, { useState } from 'react';
import {createUseStyles} from 'react-jss';

import { NativityText } from './NativityText';

const useStyles = createUseStyles({
  wrapper: {
    overflowY: 'scroll',
  },
  title: {
    fontFamily: 'Courgette',
    fontSize: '48px',
    padding: '0 20px',
    margin: '0.4em 0',
  },
  instructions: {
    fontFamily: 'Courgette',
    fontSize: '24px',
    padding: '0 20px',
    margin: '0.3em 0',
  },
  translation: {
    fontStyle: 'italic',
    '& a': {
      color: 'white',
    },
  },
  modal: {
    position: 'absolute',
    top: 0,
    left: 0,
    width: '100%',
    height: '100%',
    zIndex: 1,
  },
  modalInner: {
    margin: '10vh auto 0 auto',
    width: 'min(80%, 40vh)',
    background: '#555555',
    border: '12px ridge #a75220',
    position: 'relative',
    '& img': {
      imageRendering: 'pixelated',
      width: '100%',
      display: 'block',
    },
    '& button': {
      position: 'absolute',
      top: '-20px',
      right: '-20px',
      width: '40px',
      height: '40px',
      padding: 0,
      borderRadius: '50%',
      fontSize: '25px',
      fontWeight: 'bold',
      border: '3px solid #6c3414',
      background: '#cb3d3d',
      color: 'white',
      cursor: 'pointer',
      fontFamily: 'Arial, sans-serif',
    },
  },
  modalBackground: {
    position: 'absolute',
    top: 0,
    left: 0,
    width: '100%',
    height: '100%',
    background: '#000000CC',
  },
});

export const StoryPage = () => {
  const classes = useStyles();
  const [image, setImage] = useState(null);

  const handleLinkClick = ({ key, image }) => {
    setImage(image);
    Meteor.callAsync('pictures.setPicture', key);
  };

  return (
    <>
      <div className={classes.wrapper}>
        <h1 className={classes.title}>The Nativity Story</h1>
        <p className={classes.instructions}>Click on the highlighted words to see a picture in the lights!</p>
        <NativityText onLinkClick={handleLinkClick} />
        <p className={classes.translation}>From the <a href="https://ebible.org/web/">Word English Bible (WEB)</a> translation.</p>
        {image &&
         <div className={classes.modal}>
           <div className={classes.modalBackground} onClick={() => setImage(null)}></div>
           <div className={classes.modalInner}>
             <img src={image} aria-label="Close"/>
             <button onClick={() => setImage(null)}>&#x2715;</button>
           </div>
         </div>
        }
      </div>
    </>
  );
};
