import { Meteor } from 'meteor/meteor';
import { LightsCollection, LIGHT_COUNT } from '/imports/api/lights';

Meteor.startup(() => {
  // Initialise lights.
  for (let idx = 0; idx < LIGHT_COUNT; idx++) {
    if (!LightsCollection.findOne({idx})) {
      LightsCollection.insert({
        idx,
        colourMode: 'white',
        colourHue: 255,
        colourSaturation: 255,
        animation: 'static',
      });
    }
  }
});
