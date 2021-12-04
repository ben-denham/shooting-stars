import React, { useState } from 'react';
import { useTracker } from 'meteor/react-meteor-data';

import { LightsCollection } from '/imports/api/lights';
import { LightList } from './LightList'
import { LightForm } from './LightForm'

const updateLight = (light, updates) => {
  LightsCollection.update(light._id, {
    $set: updates
  });
}

export const App = () => {
  const lights = useTracker(() => LightsCollection.find({}, {
    sort: { idx: 1 },
  }).fetch());
  const [selectedLightId, setSelectedLightId] = useState(null);

  const selectedLight = lights.find(light => light._id === selectedLightId);

  return (
    <div>
      <LightList lights={lights} setSelectedLightId={setSelectedLightId}></LightList>
      <LightForm light={selectedLight} updateLight={updateLight}></LightForm>
    </div>
  );
};
