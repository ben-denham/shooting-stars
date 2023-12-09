import { Meteor } from 'meteor/meteor';
import { DDPRateLimiter } from 'meteor/ddp-rate-limiter';
import { LightsCollection, LIGHT_COUNT } from '/imports/db/LightsCollection';
import { lightsMethods } from '/imports/api/lightsMethods';
import { blocksMethods } from '/imports/api/blocksMethods';
import { picturesMethods } from '/imports/api/picturesMethods';
import { paintMethods } from '/imports/api/paintMethods';
import '/imports/api/lightsPublications';
import '/imports/api/blocksPublications';
import '/imports/api/picturesPublications';
import '/imports/api/paintPublications';

Meteor.startup(() => {
  // Initialise lights.
  for (let idx = 0; idx < LIGHT_COUNT; idx++) {
    if (!LightsCollection.findOne({idx})) {
      LightsCollection.insert({
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
        // Publications
        'lights',
        'blocksStates',
        'blocksInputs',
        'pictures',
        'paint',
      ].includes(name);
    },
    // Rate limit per connection ID
    connectionId() { return true; }
  },
  // Max 20 requests every second.
  20, 1000
);
