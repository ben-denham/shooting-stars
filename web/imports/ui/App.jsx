import React, { useState } from 'react';
import { useTracker } from 'meteor/react-meteor-data';
import {createUseStyles} from 'react-jss';

import { LightsCollection } from '/imports/db/LightsCollection';
import { LightList } from './LightList';
import { LightForm } from './LightForm';
import { LoadingSpinner } from './LoadingSpinner';

const useStyles = createUseStyles({
  app: {
    margin: '0px auto',
    height: '100%',
    width: '100%',
    maxWidth: '768px',
    textAlign: 'center',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'stretch',
    justifyContent: 'center',
    boxShadow: '0 0 30px 15px #303030'
  },
  loading: {
    margin: 'auto'
  },
  scrollable: {
    overflow: 'auto',
    '&::-webkit-scrollbar': {
      width: '10px'
    },
    '&::-webkit-scrollbar-track': {
      background: 'transparent'
    },
    '&::-webkit-scrollbar-thumb': {
      background: '#777777',
      borderRadius: '5px'
    },
    '&::-webkit-scrollbar-thumb:hover': {
      background: '#444444'
    }
  },
  lightList: {
    extend: 'scrollable',
    flex: 1,
  },
  lightForm: {
    extend: 'scrollable',
    background: '#181818'
  }
});

export const App = () => {
  const classes = useStyles();

  const { lights, isLoading } = useTracker(() => {
    const handler = Meteor.subscribe('lights');

    if (!handler.ready()) {
      return { lights: [], isLoading: true };
    }

    const lights = LightsCollection.find({}, {
      sort: { idx: 1 }
    }).fetch();

    return { lights };
  });
  const [selectedLightId, setSelectedLightId] = useState(null);

  const selectedLight = lights.find(light => light._id === selectedLightId);

  return (
    <div className={classes.app}>
      {isLoading && <LoadingSpinner className={classes.loading}></LoadingSpinner>}
      {!isLoading &&
       <>
         <LightList
           className={classes.lightList}
           lights={lights}
           selectedLight={selectedLight}
           setSelectedLightId={setSelectedLightId}
         />
         <LightForm
           className={classes.lightForm}
           light={selectedLight}
           setSelectedLightId={setSelectedLightId}
         />
       </>}
    </div>
  );
};
