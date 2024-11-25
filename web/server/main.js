import { Meteor } from 'meteor/meteor';
import { DDPRateLimiter } from 'meteor/ddp-rate-limiter';
import { LightsCollection, LIGHT_COUNT } from '/imports/db/LightsCollection';
import { lightsMethods } from '/imports/api/lightsMethods';
import { blocksMethods } from '/imports/api/blocksMethods';
import { picturesMethods } from '/imports/api/picturesMethods';
import { paintMethods } from '/imports/api/paintMethods';
import { presenceMethods } from '/imports/api/presenceMethods';
import '/imports/api/lightsPublications';
import '/imports/api/blocksPublications';
import '/imports/api/picturesPublications';
import '/imports/api/paintPublications';
import '/imports/api/presencePublications';

Meteor.startup(async () => {
  // Initialise lights.
  for (let idx = 0; idx < LIGHT_COUNT; idx++) {
    const light = await LightsCollection.findOneAsync({idx});
    if (!light) {
      await LightsCollection.insertAsync({
        idx,
        colourMode: 'white',
        colourHue: 0.0,
        colourSaturation: 1.0,
        animation: 'static',
      });
    }
  }
});


DDPRateLimiter.addRule(
  {
    name(name) {
      return [
        // Methods
        ...Object.keys(lightsMethods),
        ...Object.keys(blocksMethods),
        ...Object.keys(picturesMethods),
        ...Object.keys(paintMethods),
        ...Object.keys(presenceMethods),
        // Publications
        'lights',
        'blocksStates',
        'blocksInputs',
        'pictures',
        'paint',
        'presence',
      ].includes(name);
    },
    // Rate limit per connection ID
    connectionId() { return true; }
  },
  // Max 100 requests every second.
  100, 1000
);
