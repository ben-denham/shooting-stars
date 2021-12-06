import React, { useState } from 'react';
import { useTracker } from 'meteor/react-meteor-data';
import {createUseStyles} from 'react-jss';

import { LightsCollection } from '/imports/db/LightsCollection';
import { LightList } from './LightList';
import { LightForm } from './LightForm';
import { mediumBreakpoint } from './breakpoints';
import { LoadingSpinner } from './LoadingSpinner';

const useStyles = createUseStyles({
  appOuter: {
    margin: '0px auto',
    height: '100%',
    width: '100%',
    maxWidth: '768px',
    textAlign: 'center',
    background: `repeating-linear-gradient(
      45deg,
      #FF5757,
      #FF5757 10px,
      #FFFFFF 10px,
      #FFFFFF 20px
    )`
  },
  appInner: {
    margin: '0 10px',
    height: '100%',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'stretch',
    justifyContent: 'center',
    background: '#1B1B1B'
  },
  loading: {
    margin: 'auto'
  },
  lightList: {
    flex: 1,
    background: 'black'
  },
  lightForm: {
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
    <div className={classes.appOuter}>
      <div className={classes.appInner}>
        {isLoading && <LoadingSpinner className={classes.loading}></LoadingSpinner>}
        {!isLoading &&
         <>
           <LightList
             className={classes.lightList}
             lights={lights}
             setSelectedLightId={setSelectedLightId}
           />
           <LightForm
             className={classes.lightForm}
             light={selectedLight}
           />
         </>}
      </div>
    </div>
  );
};
