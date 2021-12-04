import { Meteor } from 'meteor/meteor';
import { LightsCollection, LIGHT_COUNT } from '/imports/db/LightsCollection';
import '/imports/api/lightsMethods';
import '/imports/api/lightsPublications';

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
